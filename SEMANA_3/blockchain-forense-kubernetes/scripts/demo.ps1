$ErrorActionPreference = "Stop"
$Namespace = "blockchain-forense"
$LocalPort = 8080

Write-Host "Estado inicial:" -ForegroundColor Cyan
kubectl -n $Namespace get deployment forense-api
kubectl -n $Namespace get replicaset
kubectl -n $Namespace get pods -l app=forense-api -o wide

$portForward = Start-Process -FilePath "kubectl" `
  -ArgumentList @(
    "-n", $Namespace,
    "port-forward",
    "svc/forense-api",
    "$LocalPort`:80"
  ) -PassThru -WindowStyle Hidden

try {
  Start-Sleep -Seconds 4

  Write-Host "`nPods que responden:" -ForegroundColor Cyan
  1..6 | ForEach-Object {
    $response = Invoke-RestMethod `
      -Uri "http://localhost:$LocalPort/" `
      -Method Get `
      -Headers @{ Connection = "close" }
    Write-Host "Solicitud $_ -> $($response.pod)"
  }

  Invoke-RestMethod `
    -Uri "http://localhost:$LocalPort/health" `
    -Method Get | ConvertTo-Json

  $evidenceCode = "EV-$(Get-Date -Format 'yyyyMMddHHmmss')"
  $body = @{
    codigoEvidencia = $evidenceCode
    hashEvidencia = ("a" * 64)
    caso = "CASO-K8S-001"
  } | ConvertTo-Json

  Invoke-RestMethod `
    -Uri "http://localhost:$LocalPort/evidencias" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json

  $verifyBody = @{
    codigoEvidencia = $evidenceCode
    hashEvidencia = ("a" * 64)
  } | ConvertTo-Json

  Invoke-RestMethod `
    -Uri "http://localhost:$LocalPort/evidencias/verificar" `
    -Method Post `
    -ContentType "application/json" `
    -Body $verifyBody | ConvertTo-Json

  Invoke-RestMethod `
    -Uri "http://localhost:$LocalPort/evidencias/$evidenceCode" `
    -Method Get | ConvertTo-Json
}
finally {
  if ($portForward -and -not $portForward.HasExited) {
    Stop-Process -Id $portForward.Id -Force
  }
}

Write-Host "`nPrueba de autorrecuperación:" `
  -ForegroundColor Cyan
$pod = kubectl -n $Namespace get pod `
  -l app=forense-api `
  -o jsonpath="{.items[0].metadata.name}"
kubectl -n $Namespace delete pod $pod
Start-Sleep -Seconds 3
kubectl -n $Namespace rollout status `
  deployment/forense-api --timeout=180s
kubectl -n $Namespace get pods `
  -l app=forense-api -o wide
