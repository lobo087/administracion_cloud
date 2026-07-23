# Semana 4 - UTPL emite titulos y Ministerio los avala con blockchain

Esta practica continua el proyecto de Semana 3 y lo convierte en un escenario con dos instituciones separadas:

- La `API Universidad` representa a la UTPL y emite titulos academicos.
- La `API Ministerio` representa al Ministerio de Educacion y avala titulos emitidos.
- Cada API tiene su propia base PostgreSQL.
- Ambas APIs consultan el mismo contrato inteligente desplegado en Ganache.
- La blockchain guarda evidencia verificable y estado del titulo, no datos personales completos.

El objetivo minimo de la Semana 4 es demostrar este flujo:

```text
UTPL emite un titulo
      |
      v
Contrato RegistroTitulos guarda evidencia
      |
      v
Ministerio consulta el titulo desde blockchain
      |
      v
Ministerio avala el titulo
      |
      v
UTPL y Ministerio ven el estado AVALADO
```

## Que Se Hizo En Esta Semana

Se partio copiando el proyecto de `SEMANA_3` dentro de `SEMANA_4` y luego se hicieron estos cambios:

- Se agrego `GET /titulos` a la API Universidad.
- Se redisenio el contrato `RegistroTitulos.sol` para soportar estados y aval del Ministerio.
- Se agrego hash de identificacion del estudiante para no publicar cedulas en blockchain.
- Se agregaron datos academicos visibles en blockchain: universidad emisora, carrera y titulo obtenido.
- Se agrego listado de titulos desde el contrato con `listarCodigosTitulos()`.
- Se adapto `api-universidad` al contrato nuevo.
- Se creo `api-ministerio` como API independiente.
- Se creo una base de datos PostgreSQL separada para el Ministerio.
- Se actualizo `docker-compose.yml` para levantar ambas APIs, ambas bases, Ganache y herramientas de contrato.
- Se actualizo `.env` para incluir claves de UTPL, Ministerio y credenciales de ambas bases.
- Se ajusto `hardhat.config.ts` para compilar con `evmVersion: "paris"` por compatibilidad con Ganache.

## Arquitectura

```text
Usuario / Swagger UTPL
        |
        v
API Universidad - FastAPI
        |
        | guarda datos completos del titulo
        v
PostgreSQL Universidad

        |
        | registra evidencia y datos academicos minimos
        v
Contrato RegistroTitulos
        |
        v
Ganache - blockchain local
        ^
        |
        | consulta titulos y avala
        |
API Ministerio - FastAPI
        |
        | guarda avales propios
        v
PostgreSQL Ministerio
```

## Servicios Docker Compose

| Servicio | Funcion | Puerto local |
| --- | --- | --- |
| `blockchain-node` | Nodo Ganache local | `8545` |
| `contract-tools` | Herramientas Hardhat para compilar/desplegar contrato | No expone puerto |
| `postgres` | Base de datos de UTPL | `5432` |
| `api-universidad` | API FastAPI de UTPL | `8000` |
| `postgres-ministerio` | Base de datos del Ministerio | `5433` |
| `api-ministerio` | API FastAPI del Ministerio | `8002` |

## Estructura Del Proyecto

```text
SEMANA_4/
  README.md
  .env.example
  .env
  docker-compose.yml

  blockchain/
    Dockerfile
    hardhat.config.ts
    package.json
    tsconfig.json
    contracts/
      RegistroTitulos.sol
    scripts/
      deploy-registro-titulos.ts
      crear-titulo.ts

  api-universidad/
    Dockerfile
    requirements.txt
    main.py
    database.py
    models.py
    schemas.py
    blockchain.py
    contracts/
      RegistroTitulos.json

  api-ministerio/
    Dockerfile
    requirements.txt
    main.py
    database.py
    models.py
    schemas.py
    blockchain.py
    contracts/
      RegistroTitulos.json
```

## Requisitos

Instalar previamente:

- Docker Desktop.
- Docker Compose.
- PowerShell en Windows.
- Node.js 22 o superior solo si se desea ejecutar Hardhat fuera de Docker.

Verificar:

```powershell
docker --version
docker compose version
node --version
npm --version
```

## Variables De Entorno

Crear `.env` desde `.env.example`:

```powershell
cd SEMANA_4
copy .env.example .env
```

Contenido base:

```env
GANACHE_RPC_URL=http://blockchain-node:8545
GANACHE_PRIVATE_KEY=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d
MINISTERIO_PRIVATE_KEY=0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1
CONTRACT_ADDRESS=0xREEMPLAZAR_CON_LA_DIRECCION_DEL_CONTRATO

POSTGRES_DB=titulos_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123

POSTGRES_MINISTERIO_DB=ministerio_db
POSTGRES_MINISTERIO_USER=ministerio
POSTGRES_MINISTERIO_PASSWORD=ministerio123
```

Las claves privadas corresponden a cuentas deterministicas de Ganache cuando se usa `--wallet.deterministic`.

Uso didactico de claves:

- `GANACHE_PRIVATE_KEY`: cuenta de la UTPL para emitir titulos.
- `MINISTERIO_PRIVATE_KEY`: cuenta del Ministerio para avalar titulos.

No usar estas claves en produccion.

## Docker Compose

El archivo `docker-compose.yml` levanta todos los servicios necesarios.

Partes importantes:

```yaml
blockchain-node:
  image: trufflesuite/ganache
  ports:
    - "8545:8545"
  command:
    - --host
    - 0.0.0.0
    - --chain.chainId
    - "1337"
    - --wallet.deterministic
    - --database.dbPath
    - /data
  volumes:
    - ganache_data:/data
```

Ganache usa volumen para conservar contratos y transacciones mientras no se borren volumenes.

```yaml
postgres:
  image: postgres:16-alpine
  ports:
    - "5432:5432"
```

Base de datos de UTPL.

```yaml
postgres-ministerio:
  image: postgres:16-alpine
  ports:
    - "5433:5432"
```

Base de datos independiente del Ministerio.

```yaml
api-universidad:
  ports:
    - "8000:8000"
```

API de UTPL.

```yaml
api-ministerio:
  ports:
    - "8002:8000"
```

API del Ministerio. Internamente escucha en `8000`, pero desde la maquina se accede por `8002`.

## Dockerfile De Las APIs

Tanto `api-universidad` como `api-ministerio` usan un Dockerfile simple:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Este Dockerfile hace lo siguiente:

- Usa Python 3.12 en una imagen liviana.
- Copia `requirements.txt`.
- Instala FastAPI, Uvicorn, SQLAlchemy, psycopg y Web3.
- Copia el codigo de la API.
- Ejecuta Uvicorn escuchando en `0.0.0.0:8000`.

## Dockerfile De Blockchain

El Dockerfile de `blockchain/` crea una imagen con Node.js, Hardhat, contratos y scripts.

Se usa como herramienta para:

- Compilar Solidity.
- Desplegar el contrato en Ganache.
- Ejecutar scripts de prueba.

Esto evita instalar Hardhat directamente en la maquina del estudiante.

## Cambio En hardhat.config.ts: evmVersion paris

En `blockchain/hardhat.config.ts` se agrego:

```ts
settings: {
  evmVersion: "paris",
}
```

Motivo:

Hardhat estaba compilando el contrato con target EVM `cancun`. Al desplegar y ejecutar ese contrato sobre la imagen `trufflesuite/ganache`, Ganache devolvio errores como `invalid opcode` al llamar funciones del contrato.

Para esta practica se usa Ganache como blockchain local. Por compatibilidad, se fijo `evmVersion: "paris"`, que genera bytecode compatible con el entorno de Ganache usado en Docker.

Este cambio no altera la logica del contrato. Solo define para que version de la EVM se genera el bytecode.

## Contrato RegistroTitulos.sol

Ubicacion:

```text
blockchain/contracts/RegistroTitulos.sol
```

El contrato fue ampliado para representar el flujo de Semana 4.

Estados:

```solidity
enum EstadoTitulo {
    NO_EXISTE,
    REGISTRADO,
    AVALADO,
    RECHAZADO,
    REVOCADO
}
```

Datos guardados por titulo:

```text
codigoTituloHash
documentoHash
identificacionEstudianteHash
universidadEmisora
carrera
tituloObtenido
universidad
ministerioValidador
estado
fechaRegistro
fechaAval
existe
```

Por que se guarda la identificacion como hash:

- La cedula es dato personal.
- Blockchain es compartida e inmutable.
- No conviene publicar datos sensibles directamente.
- Un auditor puede verificar una cedula calculando localmente el mismo hash y comparando contra blockchain.

Ejemplo conceptual:

```text
cedula presentada: 1100000001
hash local: keccak256("1100000001")
hash blockchain: identificacionEstudianteHash
resultado: coincide o no coincide
```

Funciones principales:

```solidity
registrarTitulo(...)
avalarTitulo(bytes32 codigoTituloHash)
verificarTitulo(...)
obtenerTitulo(bytes32 codigoTituloHash)
listarCodigosTitulos()
totalTitulos()
```

Eventos:

```solidity
TituloRegistrado
TituloAvalado
```

## API Universidad

Ubicacion:

```text
api-universidad/
```

Responsabilidades:

- Recibir datos completos del titulo.
- Guardar datos completos en su propia base PostgreSQL.
- Calcular hashes.
- Registrar evidencia en blockchain.
- Listar y consultar titulos de su base.
- Verificar contra blockchain si el titulo existe, si documento coincide y si identificacion coincide.

Base de datos:

```text
Servicio: postgres
Base: titulos_db
Tabla: titulos
Puerto local: 5432
```

Datos guardados en PostgreSQL Universidad:

```text
codigo_titulo
nombre_estudiante
identificacion_estudiante
carrera
titulo_obtenido
universidad
fecha_emision
contenido_documento
codigo_titulo_hash
documento_hash
contract_address
tx_hash
creado_en
```

Endpoints:

```http
GET /health
GET /blockchain/contract
POST /titulos
GET /titulos
GET /titulos/{codigo_titulo}
GET /titulos/{codigo_titulo}/verificar
```

Swagger:

```text
http://localhost:8000/docs
```

## API Ministerio

Ubicacion:

```text
api-ministerio/
```

Responsabilidades:

- Consultar titulos desde blockchain.
- Listar titulos registrados en el contrato.
- Avalar titulos llamando `avalarTitulo`.
- Guardar en su propia base los avales realizados.
- No consultar directamente la base de UTPL.

Base de datos:

```text
Servicio: postgres-ministerio
Base: ministerio_db
Tabla: avales_ministerio
Puerto local: 5433
```

Datos guardados en PostgreSQL Ministerio:

```text
codigo_titulo
codigo_titulo_hash
documento_hash
identificacion_estudiante_hash
universidad_emisora
carrera
titulo_obtenido
estado
contract_address
tx_hash
avalado_en
```

Endpoints:

```http
GET /health
GET /blockchain/contract
GET /titulos
GET /titulos/{codigo_titulo}
POST /titulos/{codigo_titulo}/avalar
GET /avales
```

Swagger:

```text
http://localhost:8002/docs
```

## Flujo Reproducible Desde Cero

Ejecutar desde la carpeta `SEMANA_4`.

### 1. Crear .env

```powershell
copy .env.example .env
```

### 2. Levantar Ganache

```powershell
docker compose up -d blockchain-node
```

Verificar:

```powershell
docker compose ps
docker compose logs blockchain-node
```

En los logs de Ganache aparecen las cuentas y claves privadas deterministicas. La cuenta 0 se usa para UTPL y la cuenta 1 para Ministerio.

### 3. Compilar y desplegar contrato

```powershell
docker compose build contract-tools
docker compose run --rm contract-tools npx hardhat compile
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

La salida mostrara algo como:

```text
Desplegando contrato RegistroTitulos...
Contrato desplegado correctamente
Direccion del contrato: 0x...
```

Copiar esa direccion en `.env`:

```env
CONTRACT_ADDRESS=0xDIRECCION_DEL_CONTRATO
```

### 4. Levantar bases y APIs

```powershell
docker compose up -d --build postgres api-universidad postgres-ministerio api-ministerio
```

Verificar:

```powershell
docker compose ps
```

Servicios esperados:

```text
blockchain-node
postgres
api-universidad
postgres-ministerio
api-ministerio
```

### 5. Verificar APIs

UTPL:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
Invoke-RestMethod -Uri "http://localhost:8000/blockchain/contract"
```

Ministerio:

```powershell
Invoke-RestMethod -Uri "http://localhost:8002/health"
Invoke-RestMethod -Uri "http://localhost:8002/blockchain/contract"
```

Ambos endpoints `/blockchain/contract` deben devolver:

```json
{
  "existe_en_blockchain": true
}
```

### 6. Crear titulo desde API Universidad

PowerShell:

```powershell
$body = @{
  codigo_titulo = "UTPL-SIS-2026-0002"
  nombre_estudiante = "Maria Loja"
  identificacion_estudiante = "1100000002"
  carrera = "Sistemas"
  titulo_obtenido = "Ingeniera en Sistemas"
  universidad = "UTPL"
  fecha_emision = "2026-06-15"
  contenido_documento = "Titulo de Maria Loja como Ingeniera en Sistemas emitido por UTPL"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/titulos" -Method Post -ContentType "application/json" -Body $body
```

Desde Swagger:

```text
http://localhost:8000/docs
```

Endpoint:

```http
POST /titulos
```

Body:

```json
{
  "codigo_titulo": "UTPL-SIS-2026-0002",
  "nombre_estudiante": "Maria Loja",
  "identificacion_estudiante": "1100000002",
  "carrera": "Sistemas",
  "titulo_obtenido": "Ingeniera en Sistemas",
  "universidad": "UTPL",
  "fecha_emision": "2026-06-15",
  "contenido_documento": "Titulo de Maria Loja como Ingeniera en Sistemas emitido por UTPL"
}
```

### 7. Listar y verificar desde UTPL

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/titulos"
Invoke-RestMethod -Uri "http://localhost:8000/titulos/UTPL-SIS-2026-0002"
Invoke-RestMethod -Uri "http://localhost:8000/titulos/UTPL-SIS-2026-0002/verificar"
```

Antes del aval, la verificacion debe mostrar:

```json
{
  "existe_en_blockchain": true,
  "documento_coincide": true,
  "identificacion_coincide": true,
  "estado": 1,
  "estado_descripcion": "REGISTRADO"
}
```

### 8. Consultar desde Ministerio

```powershell
Invoke-RestMethod -Uri "http://localhost:8002/titulos"
Invoke-RestMethod -Uri "http://localhost:8002/titulos/UTPL-SIS-2026-0002"
```

El Ministerio no lee la base de UTPL. Lee el contrato en blockchain.

### 9. Avalar desde Ministerio

```powershell
Invoke-RestMethod -Uri "http://localhost:8002/titulos/UTPL-SIS-2026-0002/avalar" -Method Post
```

Respuesta esperada:

```json
{
  "codigo_titulo": "UTPL-SIS-2026-0002",
  "estado": "AVALADO",
  "tx_hash": "0x..."
}
```

### 10. Verificar estado avalado

Desde Ministerio:

```powershell
Invoke-RestMethod -Uri "http://localhost:8002/titulos/UTPL-SIS-2026-0002"
Invoke-RestMethod -Uri "http://localhost:8002/avales"
```

Desde UTPL:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/titulos/UTPL-SIS-2026-0002/verificar"
```

Resultado esperado:

```json
{
  "estado": 2,
  "estado_descripcion": "AVALADO"
}
```

## Consultar Bases De Datos

Base UTPL:

```powershell
docker compose exec postgres psql -U admin -d titulos_db
```

Consulta:

```sql
SELECT id, codigo_titulo, codigo_titulo_hash, documento_hash, contract_address, tx_hash FROM titulos;
```

Base Ministerio:

```powershell
docker compose exec postgres-ministerio psql -U ministerio -d ministerio_db
```

Consulta:

```sql
SELECT id, codigo_titulo, estado, contract_address, tx_hash FROM avales_ministerio;
```

Salir de `psql`:

```sql
\q
```

## Comandos Utiles

Ver servicios:

```powershell
docker compose ps
```

Ver logs de UTPL:

```powershell
docker compose logs api-universidad
```

Ver logs del Ministerio:

```powershell
docker compose logs api-ministerio
```

Ver logs de Ganache:

```powershell
docker compose logs blockchain-node
```

Reconstruir APIs:

```powershell
docker compose build api-universidad api-ministerio
docker compose up -d --force-recreate api-universidad api-ministerio
```

Apagar sin borrar datos:

```powershell
docker compose down
```

Apagar y borrar volumenes:

```powershell
docker compose down -v
```

Usar `down -v` solo si se desea reiniciar todo desde cero, porque borra:

- Estado de Ganache.
- Base de UTPL.
- Base del Ministerio.

## Problemas Comunes

### /blockchain/contract devuelve false

La direccion `CONTRACT_ADDRESS` no corresponde a un contrato desplegado en el Ganache actual.

Solucion:

```powershell
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

Copiar la nueva direccion en `.env` y reiniciar APIs:

```powershell
docker compose up -d --force-recreate api-universidad api-ministerio
```

### El Ministerio no puede avalar por fondos insuficientes

La clave `MINISTERIO_PRIVATE_KEY` no corresponde a una cuenta financiada de Ganache.

Solucion:

```powershell
docker compose logs blockchain-node
```

Copiar una clave privada de la seccion `Private Keys` que tenga `1000 ETH` y usarla como `MINISTERIO_PRIVATE_KEY`.

### invalid opcode al registrar o avalar

El contrato puede estar compilado para una EVM no compatible con Ganache.

Solucion aplicada en esta practica:

```ts
evmVersion: "paris"
```

Luego recompilar y redesplegar:

```powershell
docker compose build contract-tools
docker compose run --rm contract-tools npx hardhat compile
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

## Resultado Final

Al finalizar la Semana 4 se tiene:

- Una blockchain local con Ganache.
- Un contrato Solidity con estados de titulo.
- Una API UTPL que emite titulos.
- Una base PostgreSQL propia de UTPL.
- Una API Ministerio que consulta blockchain y avala titulos.
- Una base PostgreSQL propia del Ministerio.
- Swagger para probar ambas APIs.
- Flujo completo `REGISTRADO -> AVALADO`.

Esta practica prepara el camino para semanas posteriores, donde se puede agregar una API auditora, Kubernetes, clusters separados y despliegues tipo multi-cloud.
