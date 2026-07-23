# Despliegue real en GCP, Azure y AWS

La practica local usa Kind para evitar costos. La misma arquitectura se puede llevar a nubes reales.

| Local | Produccion |
| --- | --- |
| Kind UTPL | GKE en Google Cloud |
| Kind Ministerio | AKS en Azure |
| Kind Auditora | EKS en AWS |
| imagen local | Artifact Registry, ACR, ECR |
| PVC local | Persistent Disk, Azure Disk, EBS |
| NodePort | LoadBalancer, Ingress, DNS privado |
| Secret Kubernetes | Secret Manager, Key Vault, AWS Secrets Manager |

En nube real hay que resolver:

- conectividad segura entre nubes
- VPN, VPC peering o enlaces privados
- exposicion controlada del puerto P2P de Geth
- restriccion del RPC de Geth
- gestion segura de claves privadas
- backups de PostgreSQL
- backups o snapshots de volumenes Geth
- monitoreo y alertas
- CI/CD por institucion

La logica institucional no cambia: cada actor mantiene su API, su base y su nodo blockchain.
