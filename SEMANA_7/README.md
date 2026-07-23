# Semana 7 - Red blockchain privada con Geth en Kubernetes

Esta practica parte de la base Kubernetes de `SEMANA_6` y agrega la red blockchain privada con tres nodos Geth, uno por institucion.

En Semana 6 se trabajan APIs, replicas, Services, PostgreSQL y PVC. En Semana 7 se agrega Geth, red P2P, contrato desplegado con Job y flujo completo UTPL -> Ministerio -> Auditora.

## Objetivo

Simular una arquitectura multi-cloud local:

```text
UTPL                  -> Google Cloud / GKE simulado con Kind
Ministerio Ecuador    -> Azure / AKS simulado con Kind
Auditora Espana       -> AWS / EKS simulado con Kind
```

Cada institucion administra su propio cluster Kubernetes, su propia API, su propia base de datos PostgreSQL y su propio nodo blockchain Geth.

## Base de trabajo

La Semana 7 conserva la base de APIs y PostgreSQL persistente de Semana 6, y agrega la capa blockchain:

```powershell
Copy-Item -Recurse SEMANA_6 SEMANA_7
```

Se reutiliza:

- `api-universidad`
- `api-ministerio`
- `api-auditora`
- contrato `RegistroTitulos.sol`
- scripts Hardhat
- Dockerfiles de APIs
- modelos, schemas y endpoints FastAPI

Luego se reorganiza por institucion y se agregan manifiestos Kubernetes.

## Arquitectura final

```text
kind-cloud-utpl-gcp
  control-plane Kubernetes
  worker
    api-universidad x2
    postgres-universidad-0 + PVC
    geth-utpl-0 + PVC

kind-cloud-ministerio-azure
  control-plane Kubernetes
  worker
    api-ministerio x2
    postgres-ministerio-0 + PVC
    geth-ministerio-0 + PVC

kind-cloud-auditora-aws
  control-plane Kubernetes
  worker
    api-auditora x2
    postgres-auditora-0 + PVC
    geth-auditora-0 + PVC
```

La red blockchain queda asi:

```text
geth-utpl <----> geth-ministerio
geth-utpl <----> geth-auditora
geth-ministerio <----> geth-auditora
```

Direcciones validadoras usadas en el `genesis.json`:

```text
UTPL:       0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1
Ministerio: 0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0
Auditora:   0xcc6bfb2198f6511348151e403960aea2d166a694
```

Cada API usa su nodo local:

```text
api-universidad -> http://geth-utpl:8545
api-ministerio  -> http://geth-ministerio:8545
api-auditora    -> http://geth-auditora:8545
```

## Kubernetes control plane vs blockchain

Kubernetes si tiene un plano de control por cluster. En esta practica hay tres control planes: uno para UTPL, uno para Ministerio y uno para Auditora.

La blockchain no tiene nodo maestro. Los nodos Geth son pares. Cada uno conserva una copia de la cadena y se sincroniza con los demas.

## Por que Geth y no Ganache

Ganache fue util para Semanas 3, 4 y 5 porque permitia probar contratos y APIs rapidamente. En Semana 6 queremos demostrar infraestructura distribuida: nodos separados, peering, persistencia, Kubernetes y simulacion multi-cloud. Para eso se usa Geth.

En los manifiestos se fija `ethereum/client-go:v1.13.15` porque conserva soporte practico para Clique PoA y mineria local con `--mine`, adecuado para este laboratorio.

## Requisitos

- Docker Desktop
- Kind
- kubectl
- PowerShell
- Node.js solo si se desea ejecutar Hardhat fuera de Docker

Verificar:

```powershell
docker --version
kind --version
kubectl version --client
```

### Instalar Kind en Windows

Opcion recomendada con `winget`:

```powershell
winget install Kubernetes.kind --accept-package-agreements --accept-source-agreements
```

Despues de instalar, cerrar y volver a abrir PowerShell para que se actualice el `PATH`.

Verificar:

```powershell
kind --version
```

Si `kind` fue instalado pero PowerShell todavia no lo reconoce, agregar temporalmente la ruta instalada por `winget` en la sesion actual:

```powershell
$env:Path = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Kubernetes.kind_Microsoft.Winget.Source_8wekyb3d8bbwe;" + $env:Path
kind --version
```

Tambien se puede agregar al `PATH` de usuario de forma persistente:

```powershell
$kindPath = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Kubernetes.kind_Microsoft.Winget.Source_8wekyb3d8bbwe"
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";$kindPath",
  "User"
)
```

Luego cerrar y abrir PowerShell otra vez.

Nota: si se tiene Go instalado, tambien se puede usar el metodo oficial:

```powershell
go install sigs.k8s.io/kind@v0.32.0
```

En ese caso hay que asegurar que `$(go env GOPATH)\bin` este en el `PATH`.

## 1. Crear clusters Kind

```powershell
kind create cluster --name cloud-utpl-gcp --config .\utpl-gcp\infraestructura\kind-cluster.yaml
kind create cluster --name cloud-ministerio-azure --config .\ministerio-azure\infraestructura\kind-cluster.yaml
kind create cluster --name cloud-auditora-aws --config .\auditora-aws-espana\infraestructura\kind-cluster.yaml
```

Los clusters usan la imagen `kindest/node:v1.30.13`, fijada en cada `kind-cluster.yaml` para evitar cambios inesperados de la imagen por defecto de Kind.

Verificar:

```powershell
kubectl config get-contexts
kubectl --context kind-cloud-utpl-gcp get nodes
kubectl --context kind-cloud-ministerio-azure get nodes
kubectl --context kind-cloud-auditora-aws get nodes
```

## 2. Construir imagenes

Ejecutar desde `SEMANA_7`:

```powershell
docker build -t api-universidad:semana6 .\utpl-gcp\api-universidad
docker build -t api-ministerio:semana6 .\ministerio-azure\api-ministerio
docker build -t api-auditora:semana6 .\auditora-aws-espana\api-auditora
docker build -t registro-titulos-hardhat:semana6 .\blockchain-shared\hardhat
```

## 3. Cargar imagenes en Kind

```powershell
kind load docker-image api-universidad:semana6 --name cloud-utpl-gcp
kind load docker-image api-ministerio:semana6 --name cloud-ministerio-azure
kind load docker-image api-auditora:semana6 --name cloud-auditora-aws
kind load docker-image registro-titulos-hardhat:semana6 --name cloud-ministerio-azure
```

## 4. Desplegar Kubernetes por institucion

Primero crear namespaces:

```powershell
kubectl --context kind-cloud-utpl-gcp apply -f .\utpl-gcp\kubernetes\namespace.yaml
kubectl --context kind-cloud-ministerio-azure apply -f .\ministerio-azure\kubernetes\namespace.yaml
kubectl --context kind-cloud-auditora-aws apply -f .\auditora-aws-espana\kubernetes\namespace.yaml
```

Luego aplicar recursos:

```powershell
kubectl --context kind-cloud-utpl-gcp apply -f .\utpl-gcp\kubernetes
kubectl --context kind-cloud-ministerio-azure apply -f .\ministerio-azure\kubernetes
kubectl --context kind-cloud-auditora-aws apply -f .\auditora-aws-espana\kubernetes
```

## 5. Conectar nodos Geth

Los nodos Geth levantan con el mismo `genesis.json`. Para completar la red P2P se obtienen los `enode` reales y se agregan como peers con `admin.addPeer`.

Obtener los `enode` reales:

```powershell
$utplRaw = kubectl --context kind-cloud-utpl-gcp -n utpl exec geth-utpl-0 -- geth attach --exec "admin.nodeInfo.enode" /data/geth.ipc
$ministerioRaw = kubectl --context kind-cloud-ministerio-azure -n ministerio exec geth-ministerio-0 -- geth attach --exec "admin.nodeInfo.enode" /data/geth.ipc
$auditoraRaw = kubectl --context kind-cloud-auditora-aws -n auditora exec geth-auditora-0 -- geth attach --exec "admin.nodeInfo.enode" /data/geth.ipc
```

Construir peers usando los `NodePort` locales:

```powershell
$utplKey = (($utplRaw | Select-Object -First 1).Trim().Trim('"') -replace '^enode://([^@]+)@.*$', '$1')
$ministerioKey = (($ministerioRaw | Select-Object -First 1).Trim().Trim('"') -replace '^enode://([^@]+)@.*$', '$1')
$auditoraKey = (($auditoraRaw | Select-Object -First 1).Trim().Trim('"') -replace '^enode://([^@]+)@.*$', '$1')

$utplPeer = "enode://$utplKey@host.docker.internal:30311"
$ministerioPeer = "enode://$ministerioKey@host.docker.internal:30312"
$auditoraPeer = "enode://$auditoraKey@host.docker.internal:30313"
```

Agregar peers:

```powershell
$cmd = "admin.addPeer('$ministerioPeer')"
kubectl --context kind-cloud-utpl-gcp -n utpl exec geth-utpl-0 -- geth attach --exec $cmd /data/geth.ipc
$cmd = "admin.addPeer('$auditoraPeer')"
kubectl --context kind-cloud-utpl-gcp -n utpl exec geth-utpl-0 -- geth attach --exec $cmd /data/geth.ipc

$cmd = "admin.addPeer('$utplPeer')"
kubectl --context kind-cloud-ministerio-azure -n ministerio exec geth-ministerio-0 -- geth attach --exec $cmd /data/geth.ipc
$cmd = "admin.addPeer('$auditoraPeer')"
kubectl --context kind-cloud-ministerio-azure -n ministerio exec geth-ministerio-0 -- geth attach --exec $cmd /data/geth.ipc

$cmd = "admin.addPeer('$utplPeer')"
kubectl --context kind-cloud-auditora-aws -n auditora exec geth-auditora-0 -- geth attach --exec $cmd /data/geth.ipc
$cmd = "admin.addPeer('$ministerioPeer')"
kubectl --context kind-cloud-auditora-aws -n auditora exec geth-auditora-0 -- geth attach --exec $cmd /data/geth.ipc
```

Verificar peers:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl exec geth-utpl-0 -- geth attach --exec "admin.peers.length" /data/geth.ipc
kubectl --context kind-cloud-ministerio-azure -n ministerio exec geth-ministerio-0 -- geth attach --exec "admin.peers.length" /data/geth.ipc
kubectl --context kind-cloud-auditora-aws -n auditora exec geth-auditora-0 -- geth attach --exec "admin.peers.length" /data/geth.ipc
```

La conexion P2P entre clusters Kind se expone con `NodePort`:

```text
UTPL:       30311
Ministerio: 30312
Auditora:   30313
```

## 6. Desplegar contrato con Job

El contrato se despliega desde `blockchain-shared`, no desde una API institucional.

Ejemplo aplicando el Job en el cluster del Ministerio como punto de entrada RPC:

```powershell
kubectl --context kind-cloud-ministerio-azure apply -f .\blockchain-shared\kubernetes\job-deploy-contract.yaml
kubectl --context kind-cloud-ministerio-azure -n blockchain-shared logs job/deploy-registro-titulos
```

El Job imprime la direccion del contrato. Esa direccion se coloca como `CONTRACT_ADDRESS` en los secrets/configmaps de las tres APIs.

Actualizar la direccion en las tres APIs:

```powershell
$contractAddress = "0xDIRECCION_DEL_CONTRATO"

kubectl --context kind-cloud-utpl-gcp -n utpl create configmap api-universidad-config `
  --from-literal=BLOCKCHAIN_RPC_URL=http://geth-utpl:8545 `
  --from-literal=UNIVERSIDAD_NOMBRE=UTPL `
  --from-literal=CONTRACT_ADDRESS=$contractAddress `
  --dry-run=client -o yaml | kubectl --context kind-cloud-utpl-gcp apply -f -

kubectl --context kind-cloud-ministerio-azure -n ministerio create configmap api-ministerio-config `
  --from-literal=BLOCKCHAIN_RPC_URL=http://geth-ministerio:8545 `
  --from-literal=CONTRACT_ADDRESS=$contractAddress `
  --dry-run=client -o yaml | kubectl --context kind-cloud-ministerio-azure apply -f -

kubectl --context kind-cloud-auditora-aws -n auditora create configmap api-auditora-config `
  --from-literal=BLOCKCHAIN_RPC_URL=http://geth-auditora:8545 `
  --from-literal=CONTRACT_ADDRESS=$contractAddress `
  --dry-run=client -o yaml | kubectl --context kind-cloud-auditora-aws apply -f -
```

Las APIs leen la direccion desde este archivo montado por ConfigMap:

```text
/etc/registro-titulos/contract-address
```

Por eso no hace falta reconstruir imagenes ni reiniciar las APIs por codigo. Kubernetes actualiza el volumen proyectado del ConfigMap. El cambio puede tardar hasta 1 minuto.

Verificar que las tres APIs ya ven la nueva direccion:

```powershell
Start-Sleep -Seconds 60
kubectl --context kind-cloud-utpl-gcp -n utpl exec deploy/api-universidad -- sh -c "cat /etc/registro-titulos/contract-address"
kubectl --context kind-cloud-ministerio-azure -n ministerio exec deploy/api-ministerio -- sh -c "cat /etc/registro-titulos/contract-address"
kubectl --context kind-cloud-auditora-aws -n auditora exec deploy/api-auditora -- sh -c "cat /etc/registro-titulos/contract-address"
```

## 7. Acceder a Swagger

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl port-forward svc/api-universidad 8001:80
kubectl --context kind-cloud-ministerio-azure -n ministerio port-forward svc/api-ministerio 8002:80
kubectl --context kind-cloud-auditora-aws -n auditora port-forward svc/api-auditora 8003:80
```

URLs:

```text
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
```

## 8. Demo final

1. UTPL registra un titulo.
2. API Universidad guarda datos en PostgreSQL UTPL.
3. API Universidad envia transaccion a `geth-utpl`.
4. Ministerio consulta desde `geth-ministerio`.
5. Ministerio avala el titulo.
6. Auditora consulta desde `geth-auditora`.
7. Auditora verifica documento, identificacion, aval y universidad autorizada.
8. Se altera el documento.
9. Auditora demuestra que el hash ya no coincide.

## 9. Demo de recuperacion de pods

Matar una API:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl delete pod <api-universidad-pod>
kubectl --context kind-cloud-utpl-gcp -n utpl get pods -w
```

Matar PostgreSQL:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl delete pod postgres-universidad-0
```

Matar Geth:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl delete pod geth-utpl-0
```

Resultado esperado: Kubernetes recrea los pods. PostgreSQL y Geth conservan datos gracias a PVC.

## Costo

Esta practica local con Kind no genera costos cloud. Consume CPU, RAM y disco local.
