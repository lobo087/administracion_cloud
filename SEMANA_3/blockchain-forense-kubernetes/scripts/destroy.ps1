param(
  [string]$ClusterName = "blockchain-forense"
)
$ErrorActionPreference = "Stop"
kind delete cluster --name $ClusterName
Write-Host "Clúster $ClusterName eliminado." -ForegroundColor Green
