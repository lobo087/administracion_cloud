# Blockchain shared

Esta carpeta contiene los artefactos compartidos de la red blockchain academica.

No representa una institucion. Representa los acuerdos tecnicos comunes:

- `genesis.json`
- proyecto Hardhat
- Job Kubernetes para desplegar el contrato

La fuente unica del contrato esta dentro del proyecto Hardhat:

```text
hardhat/contracts/RegistroTitulos.sol
```

El contrato se despliega una sola vez y queda registrado en la red blockchain privada formada por `geth-utpl`, `geth-ministerio` y `geth-auditora`.
