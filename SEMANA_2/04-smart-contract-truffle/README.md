# Ejercicio 4: Smart Contract con Truffle y Docker

Este ejercicio contiene un contrato Solidity simple usando Truffle. Esta preparado para ejecutarse con Docker Compose y para construir una imagen que se pueda subir a Docker Hub.

## Contrato

`contracts/HolaUTPL.sol` permite:

- Consultar el mensaje publico `mensaje`.
- Actualizar el mensaje con `actualizarMensaje`.
- Emitir el evento `MensajeActualizado`.

## Comandos locales

Levantar Ganache:

```bash
docker compose up -d ganache
```

Compilar:

```bash
docker compose run --rm truffle npx truffle compile
```

Ejecutar pruebas:

```bash
docker compose run --rm truffle npx truffle test
```

Desplegar el contrato en Ganache:

```bash
docker compose run --rm truffle npx truffle migrate --network development
```

Interactuar con el contrato desplegado:

```bash
docker compose run --rm truffle npx truffle exec scripts/interact.js --network development
```

Detener servicios:

```bash
docker compose down
```

Limpiar volumen de dependencias si se desea empezar desde cero:

```bash
docker compose down -v
```

## Imagen para Docker Hub

Construir imagen:

```bash
docker build -t TU_USUARIO_DOCKERHUB/smart-contract-truffle-docker:1.0.0 .
```

Iniciar sesion:

```bash
docker login
```

Subir imagen:

```bash
docker push TU_USUARIO_DOCKERHUB/smart-contract-truffle-docker:1.0.0
```

Probar imagen descargada:

```bash
docker pull TU_USUARIO_DOCKERHUB/smart-contract-truffle-docker:1.0.0
docker run --rm TU_USUARIO_DOCKERHUB/smart-contract-truffle-docker:1.0.0
```

El comando anterior compila el contrato dentro del contenedor. Para probar, migrar e interactuar con Ganache se recomienda usar `docker compose`.
