# Administracion Cloud UTPL

Repositorio para organizar el material practico de la materia de Administracion Cloud.

El contenido avanza por semanas, desde contenedores basicos con Docker hasta servicios orquestados con Docker Compose, contratos inteligentes, APIs, bases de datos y preparacion para escenarios multi-institucion.

## Estructura

- `SEMANA_1/`: ejercicios introductorios con Docker, imagenes, contenedores, puertos, variables de entorno y servicios simples.
- `SEMANA_2/`: ejercicios con Docker Compose, MySQL, persistencia y contratos inteligentes con Solidity usando Truffle y Hardhat.
- `SEMANA_3/`: primer proyecto integrador con blockchain local, Hardhat, Ganache, FastAPI, Swagger, PostgreSQL y Docker Compose.
- `SEMANA_4/`: evolucion del proyecto integrador con dos instituciones separadas: UTPL emite titulos y el Ministerio los avala usando blockchain.

## Proyecto Integrador

Desde `SEMANA_3` se trabaja un caso de registro y verificacion de titulos universitarios.

La evolucion es:

```text
Semana 3
API Universidad + PostgreSQL + Contrato + Ganache

Semana 4
API Universidad + PostgreSQL Universidad
API Ministerio + PostgreSQL Ministerio
Contrato compartido + Ganache
```

## Semana 3

La Semana 3 introduce el caso base:

- Una universidad registra titulos.
- PostgreSQL guarda datos completos.
- Blockchain guarda hashes como evidencia.
- FastAPI expone endpoints con Swagger.
- Docker Compose levanta Ganache, PostgreSQL, API y herramientas Hardhat.

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

Ejecutar Semana 3:

```powershell
cd SEMANA_3
copy .env.example .env
docker compose up -d --build blockchain-node
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

Luego copiar la direccion del contrato en `SEMANA_3/.env` y levantar API/base:

```powershell
docker compose up -d --build postgres api-universidad
```

Swagger Semana 3:

```text
http://localhost:8000/docs
```

Documentacion completa:

```text
SEMANA_3/README.md
```

## Semana 4

La Semana 4 extiende el caso a dos sistemas institucionales separados:

- UTPL emite y registra titulos.
- Ministerio consulta titulos desde blockchain.
- Ministerio avala titulos.
- UTPL y Ministerio tienen bases PostgreSQL separadas.
- La blockchain mantiene evidencia y estado compartido.

Arquitectura Semana 4:

```text
API Universidad UTPL
      |
      v
PostgreSQL Universidad

      |
      v
Contrato RegistroTitulos en Ganache
      ^
      |
API Ministerio
      |
      v
PostgreSQL Ministerio
```

Servicios principales:

| Servicio | Puerto | Descripcion |
| --- | --- | --- |
| `api-universidad` | `8000` | Swagger y API de UTPL |
| `api-ministerio` | `8002` | Swagger y API del Ministerio |
| `postgres` | `5432` | Base de UTPL |
| `postgres-ministerio` | `5433` | Base del Ministerio |
| `blockchain-node` | `8545` | Ganache local |

Ejecutar Semana 4 desde cero:

```powershell
cd SEMANA_4
copy .env.example .env
docker compose up -d blockchain-node
docker compose build contract-tools
docker compose run --rm contract-tools npx hardhat compile
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

Copiar la direccion desplegada en `SEMANA_4/.env`:

```env
CONTRACT_ADDRESS=0xDIRECCION_DEL_CONTRATO
```

Levantar APIs y bases:

```powershell
docker compose up -d --build postgres api-universidad postgres-ministerio api-ministerio
```

Swagger Semana 4:

```text
http://localhost:8000/docs
http://localhost:8002/docs
```

Flujo de prueba:

```text
1. Crear titulo en API Universidad.
2. Listar titulos en API Universidad.
3. Consultar titulo en API Ministerio.
4. Avalar titulo desde API Ministerio.
5. Verificar desde API Universidad que el estado es AVALADO.
```

Documentacion completa:

```text
SEMANA_4/README.md
```

## Conceptos Clave Del Proyecto

- Docker permite empaquetar cada servicio.
- Docker Compose orquesta APIs, bases de datos, Ganache y Hardhat.
- PostgreSQL guarda datos operativos de cada institucion.
- Blockchain guarda evidencia comun entre instituciones.
- El contrato no guarda cedulas en texto plano, sino hashes.
- Swagger permite probar sin construir frontend.
- Cada institucion puede evolucionar hacia su propio despliegue cloud.

## Requisitos Generales

- Docker Desktop.
- Docker Compose.
- Node.js para trabajar localmente con Hardhat si no se usa solo Docker.
- PowerShell en Windows.

## Comandos Utiles

Ver contenedores:

```powershell
docker compose ps
```

Ver logs:

```powershell
docker compose logs api-universidad
docker compose logs api-ministerio
docker compose logs blockchain-node
```

Apagar servicios sin borrar datos:

```powershell
docker compose down
```

Apagar y borrar volumenes:

```powershell
docker compose down -v
```

## Licencia

Este repositorio se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para mas informacion.
