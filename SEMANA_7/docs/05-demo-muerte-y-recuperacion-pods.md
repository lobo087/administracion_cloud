# Demo de muerte y recuperacion de pods

Esta demo muestra por que Kubernetes ayuda a operar sistemas distribuidos.

## API

Las APIs tienen 2 replicas. Si una muere, el ReplicaSet crea otra.

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl delete pod <api-universidad-pod>
kubectl --context kind-cloud-utpl-gcp -n utpl get pods -w
```

## PostgreSQL

PostgreSQL usa StatefulSet y PVC.

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl delete pod postgres-universidad-0
```

El pod vuelve y conserva los datos porque el volumen persistente no se borra.

## Geth

Geth usa StatefulSet y PVC.

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl delete pod geth-utpl-0
```

El nodo vuelve con la cadena almacenada y puede resincronizarse con sus peers.

## Actualizacion del contrato sin reiniciar APIs

Las APIs leen `CONTRACT_ADDRESS` desde un archivo montado por ConfigMap:

```text
/etc/registro-titulos/contract-address
```

Despues de desplegar el contrato, se actualiza con:

```powershell
$contractAddress = "0xDIRECCION_DEL_CONTRATO"

kubectl --context kind-cloud-utpl-gcp -n utpl create configmap api-universidad-config `
  --from-literal=BLOCKCHAIN_RPC_URL=http://geth-utpl:8545 `
  --from-literal=UNIVERSIDAD_NOMBRE=UTPL `
  --from-literal=CONTRACT_ADDRESS=$contractAddress `
  --dry-run=client -o yaml | kubectl --context kind-cloud-utpl-gcp apply -f -
```

Kubernetes actualiza el volumen proyectado y la API toma la nueva direccion en la siguiente llamada.
