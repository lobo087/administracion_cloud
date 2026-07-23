# Semana 6 - APIs y PostgreSQL persistente en Kubernetes con Kind

Esta practica toma las APIs trabajadas hasta Semana 5 y las despliega en Kubernetes local usando Kind.

En esta semana no se despliega todavia la red blockchain con Geth. Esa parte queda para `SEMANA_7`.

## Objetivo

Levantar tres instituciones separadas, cada una en su propio cluster Kubernetes local:

```text
UTPL-GCP                 -> kind-cloud-utpl-gcp
MINISTERIO-AZURE         -> kind-cloud-ministerio-azure
AUDITORA-AWS-ESPANA      -> kind-cloud-auditora-aws
```

Cada institucion tendra:

- Una API FastAPI.
- Dos replicas de la API.
- Una base PostgreSQL propia.
- Persistencia de datos con PVC.
- Un Service para acceder a la API.
- Swagger por `port-forward`.

## Que se aprende

- Que es Kind.
- Que es un cluster Kubernetes.
- Que es un control plane.
- Que es un worker node.
- Que es un Pod.
- Que es un Deployment.
- Que es un ReplicaSet.
- Que es un Service.
- Que es un StatefulSet.
- Que es un PVC.
- Como Kubernetes recrea un pod cuando se elimina.

## Arquitectura

```text
kind-cloud-utpl-gcp
  namespace utpl
    api-universidad x2 replicas
    postgres-universidad-0 + PVC

kind-cloud-ministerio-azure
  namespace ministerio
    api-ministerio x2 replicas
    postgres-ministerio-0 + PVC

kind-cloud-auditora-aws
  namespace auditora
    api-auditora x2 replicas
    postgres-auditora-0 + PVC
```

## Instalacion de Kind en Windows

Verificar Docker:

```powershell
docker --version
docker ps
```

Instalar Kind:

```powershell
winget install Kubernetes.kind --accept-package-agreements --accept-source-agreements
```

Cerrar y abrir PowerShell, luego verificar:

```powershell
kind --version
```

Si PowerShell todavia no reconoce `kind`, agregar temporalmente la ruta de Winget:

```powershell
$env:Path = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Kubernetes.kind_Microsoft.Winget.Source_8wekyb3d8bbwe;" + $env:Path
kind --version
```

## 1. Construir imagenes de APIs

Ejecutar desde `SEMANA_6`:

```powershell
docker build -t api-universidad:semana6 .\utpl-gcp\api-universidad
docker build -t api-ministerio:semana6 .\ministerio-azure\api-ministerio
docker build -t api-auditora:semana6 .\auditora-aws-espana\api-auditora
```

## 2. Crear clusters Kind

```powershell
kind create cluster --name cloud-utpl-gcp --config .\utpl-gcp\infraestructura\kind-cluster.yaml
kind create cluster --name cloud-ministerio-azure --config .\ministerio-azure\infraestructura\kind-cluster.yaml
kind create cluster --name cloud-auditora-aws --config .\auditora-aws-espana\infraestructura\kind-cluster.yaml
```

Los clusters usan `kindest/node:v1.30.13`, fijada en cada `kind-cluster.yaml` para evitar cambios inesperados de la imagen por defecto de Kind.

## 3. Verificar clusters

```powershell
kubectl config get-contexts
kubectl --context kind-cloud-utpl-gcp get nodes
kubectl --context kind-cloud-ministerio-azure get nodes
kubectl --context kind-cloud-auditora-aws get nodes
```

## 4. Cargar imagenes en Kind

```powershell
kind load docker-image api-universidad:semana6 --name cloud-utpl-gcp
kind load docker-image api-ministerio:semana6 --name cloud-ministerio-azure
kind load docker-image api-auditora:semana6 --name cloud-auditora-aws
```

## 5. Desplegar APIs y bases de datos

Primero crear los namespaces:

```powershell
kubectl --context kind-cloud-utpl-gcp apply -f .\utpl-gcp\kubernetes\namespace.yaml
kubectl --context kind-cloud-ministerio-azure apply -f .\ministerio-azure\kubernetes\namespace.yaml
kubectl --context kind-cloud-auditora-aws apply -f .\auditora-aws-espana\kubernetes\namespace.yaml
```

Luego desplegar los recursos de cada institucion:

```powershell
kubectl --context kind-cloud-utpl-gcp apply -f .\utpl-gcp\kubernetes
kubectl --context kind-cloud-ministerio-azure apply -f .\ministerio-azure\kubernetes
kubectl --context kind-cloud-auditora-aws apply -f .\auditora-aws-espana\kubernetes
```

## 6. Ver pods

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl get pods
kubectl --context kind-cloud-ministerio-azure -n ministerio get pods
kubectl --context kind-cloud-auditora-aws -n auditora get pods
```

Resultado esperado por institucion:

```text
api x2 pods
postgres x1 pod
```

## 7. Ver PVC

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl get pvc
kubectl --context kind-cloud-ministerio-azure -n ministerio get pvc
kubectl --context kind-cloud-auditora-aws -n auditora get pvc
```

Cada PostgreSQL debe tener un PVC en estado `Bound`.

## 8. Abrir Swagger

Importante: los Services de Kubernetes son internos al cluster. Antes de abrir `localhost` en el navegador, se debe crear un tunel con `kubectl port-forward`.

Abrir tres terminales y dejar estos comandos corriendo. No cerrar esas terminales mientras se usa Swagger.

Terminal 1:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl port-forward svc/api-universidad 8001:80
```

Terminal 2:

```powershell
kubectl --context kind-cloud-ministerio-azure -n ministerio port-forward svc/api-ministerio 8002:80
```

Terminal 3:

```powershell
kubectl --context kind-cloud-auditora-aws -n auditora port-forward svc/api-auditora 8003:80
```

Abrir:

```text
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
```

Si aparece `ERR_CONNECTION_REFUSED`, significa que el `port-forward` no esta activo o se cerro la terminal donde estaba corriendo.

## 9. Probar health

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/health"
Invoke-RestMethod -Uri "http://localhost:8002/health"
Invoke-RestMethod -Uri "http://localhost:8003/health"
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

## 10. Matar un pod de API

Ver pods de UTPL:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl get pods
```

Eliminar uno de los pods de `api-universidad`:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl delete pod NOMBRE_DEL_POD
```

Observar recuperacion:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl get pods -w
```

Kubernetes debe crear automaticamente otro pod para volver a tener 2 replicas.

## 11. Probar persistencia de PostgreSQL

Eliminar el pod de PostgreSQL:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl delete pod postgres-universidad-0
```

Ver que vuelve:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl get pods -w
```

El pod se recrea con el mismo PVC.

## 12. Apagar todo

```powershell
kind delete cluster --name cloud-utpl-gcp
kind delete cluster --name cloud-ministerio-azure
kind delete cluster --name cloud-auditora-aws
```

## Siguiente clase

En `SEMANA_7` se agrega:

- Nodos Geth.
- Red blockchain privada.
- Peers entre instituciones.
- Contrato desplegado con Job.
- Flujo completo UTPL -> Ministerio -> Auditora.
