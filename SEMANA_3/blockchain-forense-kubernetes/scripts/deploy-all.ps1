param(
  [string]$ClusterName = "blockchain-forense"
)

$ErrorActionPreference = "Stop"
$Namespace = "blockchain-forense"
$Root = Split-Path -Parent $PSScriptRoot

function Invoke-Step([string]$Message, [scriptblock]$Action) {
  Write-Host "`n=== $Message ===" -ForegroundColor Cyan
  & $Action
}

Invoke-Step "Verificar herramientas" {
  docker --version
  kind --version
  kubectl version --client
}

Invoke-Step "Construir imágenes" {
  docker build -t forense-contract:1.0 `
    (Join-Path $Root "contract")
  docker build -t forense-api:1.0 `
    (Join-Path $Root "api")
}

$clusters = kind get clusters
if ($clusters -notcontains $ClusterName) {
  Invoke-Step "Crear clúster Kind" {
    kind create cluster --name $ClusterName `
      --config (Join-Path $Root `
        "infraestructura/kind-cluster.yaml")
  }
} else {
  Write-Host "El clúster ya existe; se reutilizará." `
    -ForegroundColor Yellow
}

Invoke-Step "Seleccionar contexto kubectl" {
  kubectl config use-context "kind-$ClusterName"
  kubectl get nodes
}

Invoke-Step "Cargar imágenes locales en Kind" {
  kind load docker-image forense-contract:1.0 `
    --name $ClusterName
  kind load docker-image forense-api:1.0 `
    --name $ClusterName
}

Invoke-Step "Aplicar configuración base" {
  kubectl apply -f (Join-Path $Root `
    "kubernetes/00-namespace.yaml")
  kubectl apply -f (Join-Path $Root `
    "kubernetes/01-genesis-configmap.yaml")
  kubectl apply -f (Join-Path $Root `
    "kubernetes/02-secret-demo.yaml")
}

Invoke-Step "Desplegar los tres nodos Geth" {
  kubectl apply -f (Join-Path $Root `
    "kubernetes/network/03-pvc-geth.yaml")
  kubectl apply -f (Join-Path $Root `
    "kubernetes/network/04-services-geth.yaml")
  kubectl apply -f (Join-Path $Root `
    "kubernetes/network/05-statefulsets-geth.yaml")

  kubectl -n $Namespace rollout status `
    statefulset/geth-utpl --timeout=240s
  kubectl -n $Namespace rollout status `
    statefulset/geth-ministerio --timeout=240s
  kubectl -n $Namespace rollout status `
    statefulset/geth-auditora --timeout=240s
}

Invoke-Step "Conectar nodos Geth como peers" {
  kubectl apply -f (Join-Path $Root `
    "kubernetes/network/06-peer-script-configmap.yaml")
  kubectl -n $Namespace delete job `
    configurar-peers-geth --ignore-not-found
  kubectl apply -f (Join-Path $Root `
    "kubernetes/network/07-job-configurar-peers.yaml")
  kubectl -n $Namespace wait `
    --for=condition=complete `
    job/configurar-peers-geth --timeout=240s
  kubectl -n $Namespace logs job/configurar-peers-geth
}

Invoke-Step "Desplegar smart contract mediante Job" {
  kubectl -n $Namespace delete job `
    deploy-registro-evidencias --ignore-not-found
  kubectl apply -f (Join-Path $Root `
    "kubernetes/jobs/08-job-deploy-contract.yaml")
  kubectl -n $Namespace wait `
    --for=condition=complete `
    job/deploy-registro-evidencias --timeout=300s
}

$contractLogs = kubectl -n $Namespace logs `
  job/deploy-registro-evidencias
$contractLogs | Write-Host
$match = [regex]::Match(
  ($contractLogs -join "`n"),
  "CONTRACT_ADDRESS=(0x[a-fA-F0-9]{40})"
)
if (-not $match.Success) {
  throw "No fue posible extraer CONTRACT_ADDRESS."
}
$contractAddress = $match.Groups[1].Value
Write-Host "Contrato: $contractAddress" `
  -ForegroundColor Green

Invoke-Step "Crear ConfigMap de la API" {
  kubectl -n $Namespace create configmap `
    forense-api-config `
    --from-literal=BLOCKCHAIN_RPC_URL=http://geth-utpl:8545 `
    --from-literal=CONTRACT_ADDRESS=$contractAddress `
    --from-literal=CHAIN_ID=202606 `
    --dry-run=client -o yaml | kubectl apply -f -
}

Invoke-Step "Desplegar API con tres réplicas" {
  kubectl apply -f (Join-Path $Root `
    "kubernetes/api/09-deployment-api.yaml")
  kubectl apply -f (Join-Path $Root `
    "kubernetes/api/10-service-api.yaml")
  kubectl -n $Namespace rollout status `
    deployment/forense-api --timeout=240s
}

Invoke-Step "Resumen" {
  kubectl -n $Namespace get deployments
  kubectl -n $Namespace get replicasets
  kubectl -n $Namespace get pods -o wide
  kubectl -n $Namespace get services
  kubectl -n $Namespace get jobs
}

Write-Host "`nDespliegue completado." -ForegroundColor Green
Write-Host "Ejecute .\scripts\demo.ps1."
