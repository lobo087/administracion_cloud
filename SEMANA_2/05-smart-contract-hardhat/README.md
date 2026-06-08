# Ejercicio 5: Smart Contract con Hardhat y Docker

Este ejercicio contiene el mismo contrato simple de Truffle, pero usando Hardhat.

## Comandos

Compilar:

```bash
docker compose run --rm hardhat npx hardhat compile
```

Ejecutar pruebas:

```bash
docker compose run --rm hardhat npx hardhat test
```

Levantar nodo local Hardhat:

```bash
docker compose up -d hardhat-node
```

Desplegar en el nodo local:

```bash
docker compose run --rm hardhat npx hardhat run scripts/deploy.js --network localhost
```

Interactuar con el contrato desplegado:

```bash
docker compose run --rm hardhat npx hardhat run scripts/interact.js --network localhost
```

Detener servicios:

```bash
docker compose down
```

Limpiar dependencias y archivos generados:

```bash
docker compose down -v
```
