# Red blockchain distribuida

La red blockchain no vive en una API ni en una sola nube.

La red existe porque estos nodos estan conectados:

```text
geth-utpl
geth-ministerio
geth-auditora
```

Cada API usa su nodo local:

```text
api-universidad -> geth-utpl
api-ministerio  -> geth-ministerio
api-auditora    -> geth-auditora
```

No hay nodo maestro blockchain. Hay nodos pares y validadores. Kubernetes tiene control plane por cluster, pero ese control plane no administra la blockchain.

En la practica local, los peers se conectan obteniendo el `enode` de cada nodo y ejecutando `admin.addPeer`.

Ejemplo para obtener enodes:

```powershell
$utplRaw = kubectl --context kind-cloud-utpl-gcp -n utpl exec geth-utpl-0 -- geth attach --exec "admin.nodeInfo.enode" /data/geth.ipc
$ministerioRaw = kubectl --context kind-cloud-ministerio-azure -n ministerio exec geth-ministerio-0 -- geth attach --exec "admin.nodeInfo.enode" /data/geth.ipc
$auditoraRaw = kubectl --context kind-cloud-auditora-aws -n auditora exec geth-auditora-0 -- geth attach --exec "admin.nodeInfo.enode" /data/geth.ipc
```

Luego se construyen peers usando `host.docker.internal:30311`, `host.docker.internal:30312` y `host.docker.internal:30313`, y se agregan con:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl exec geth-utpl-0 -- geth attach --exec "admin.addPeer('enode://...')" /data/geth.ipc
```

Verificacion:

```powershell
kubectl --context kind-cloud-utpl-gcp -n utpl exec geth-utpl-0 -- geth attach --exec "admin.peers.length" /data/geth.ipc
```
