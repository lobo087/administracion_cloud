# Administracion Cloud UTPL

Repositorio para organizar el material practico de la materia de Administracion Cloud.

El contenido avanza por semanas, desde contenedores basicos con Docker hasta servicios orquestados con Docker Compose, contratos inteligentes, APIs, bases de datos y preparacion para Kubernetes.

## Estructura

- `SEMANA_1/`: ejercicios introductorios con Docker, imagenes, contenedores y servicios simples.
- `SEMANA_2/`: ejercicios con Docker Compose, MySQL, persistencia y contratos inteligentes con Solidity usando Truffle y Hardhat.
- `SEMANA_3/`: proyecto integrador con blockchain local, Hardhat, Ganache, FastAPI, Swagger, PostgreSQL y Docker Compose.

## Proyecto Integrador

Desde `SEMANA_3` se trabaja un caso de registro y verificacion de titulos universitarios.

La idea principal es separar responsabilidades:

- PostgreSQL guarda los datos completos del titulo.
- Blockchain guarda hashes como evidencia verificable.
- FastAPI expone la API de la universidad.
- Swagger permite probar la API sin construir un frontend.
- Docker Compose levanta todos los servicios necesarios.

Arquitectura base:

```text
FastAPI Universidad
      |
      | datos completos
      v
PostgreSQL

      |
      | hashes/evidencia
      v
Contrato Solidity en Ganache
```

Para ejecutar la practica de Semana 3:

```powershell
cd SEMANA_3
copy .env.example .env
docker compose up -d --build blockchain-node
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

Luego se copia la direccion del contrato en `SEMANA_3/.env` y se levantan la API y la base de datos:

```powershell
docker compose up -d --build postgres api-universidad
```

Swagger queda disponible en:

```text
http://localhost:8000/docs
```

La documentacion completa de esta practica esta en:

```text
SEMANA_3/README.md
```

## Requisitos Generales

- Docker Desktop.
- Docker Compose.
- Node.js para trabajar localmente con Hardhat.
- PowerShell en Windows.

## Licencia

Este repositorio se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para mas informacion.
