# Semana 3 - Registro de Titulos con Blockchain, FastAPI, PostgreSQL y Docker Compose

Esta practica construye un primer proyecto integrador de administracion cloud. El objetivo es registrar titulos universitarios guardando los datos completos en PostgreSQL y dejando una evidencia verificable en blockchain mediante un contrato inteligente.

La practica avanza por etapas:

- Crear y probar un contrato Solidity con Hardhat.
- Ejecutar el contrato y scripts desde Docker.
- Levantar una blockchain local con Ganache usando Docker Compose.
- Desplegar el contrato en Ganache y guardar su direccion.
- Crear una API Universidad con FastAPI y Swagger.
- Guardar datos completos en PostgreSQL.
- Registrar hashes en blockchain desde la API.
- Verificar desde Swagger que el titulo existe y que el documento coincide.

## Problema Que Busca Resolver

En un sistema academico real, una universidad necesita emitir titulos y permitir que terceros verifiquen su autenticidad. Guardar toda la informacion en blockchain no es recomendable porque puede incluir datos personales y porque la blockchain no es una base de datos tradicional.

Esta solucion separa responsabilidades:

- PostgreSQL guarda los datos completos del titulo.
- Blockchain guarda evidencia verificable mediante hashes.
- FastAPI expone endpoints para registrar y verificar titulos.
- Swagger permite probar la API sin construir un frontend.
- Docker Compose orquesta todos los servicios localmente.

## Arquitectura

```text
Usuario / Swagger
      |
      v
API Universidad - FastAPI
      |
      | guarda datos completos
      v
PostgreSQL

      |
      | registra hashes
      v
Contrato RegistroTitulos
      |
      v
Ganache - blockchain local
```

Servicios usados:

- `blockchain-node`: nodo Ganache local en el puerto `8545`.
- `contract-tools`: contenedor con Hardhat para compilar y desplegar contratos.
- `postgres`: base de datos PostgreSQL.
- `api-universidad`: API FastAPI con Swagger en el puerto `8000`.

## Estructura

```text
SEMANA_3/
  README.md
  .env.example
  docker-compose.yml
  blockchain/
    Dockerfile
    hardhat.config.ts
    package.json
    contracts/
      RegistroTitulos.sol
    scripts/
      crear-titulo.ts
      deploy-registro-titulos.ts
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
```

## Requisitos

Instalar previamente:

- Docker Desktop.
- Node.js 22 o superior si se desea probar Hardhat localmente.
- PowerShell en Windows.

Verificar versiones:

```powershell
docker --version
docker compose version
node --version
npm --version
```

## Variables De Entorno

Crear un archivo `.env` dentro de `SEMANA_3` usando como base `.env.example`:

```powershell
copy .env.example .env
```

Contenido esperado:

```env
GANACHE_RPC_URL=http://blockchain-node:8545
GANACHE_PRIVATE_KEY=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d
CONTRACT_ADDRESS=0xREEMPLAZAR_CON_LA_DIRECCION_DEL_CONTRATO

POSTGRES_DB=titulos_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
```

La clave privada incluida corresponde a la primera cuenta que Ganache genera con `--wallet.deterministic`. Es solo para desarrollo local.

## 1. Crear El Proyecto Hardhat Desde Cero

Crea una nueva carpeta para trabajar en este proyecto

Crear la carpeta blockchain:

```powershell
mkdir blockchain
cd blockchain
```

Inicializar Hardhat:


```powershell
npx hardhat --init
```

Seleccionar un proyecto TypeScript con Viem.

## 2. Contrato RegistroTitulos

El contrato principal esta en:

```text
blockchain/contracts/RegistroTitulos.sol
```

Responsabilidades del contrato:

- Registrar un titulo usando `codigoTituloHash` y `documentoHash`.
- Evitar duplicados por `codigoTituloHash`.
- Guardar la direccion de la universidad que registra el titulo.
- Permitir verificar si un documento coincide con un titulo registrado.
- Emitir el evento `TituloRegistrado`.

El contrato no guarda nombres, cedulas ni documentos completos. Solo guarda hashes.

## 3. Probar Hardhat Localmente

Desde `SEMANA_3/blockchain`:

```powershell
npm install
```

Compilar el contrato:

```powershell
npx hardhat compile
```

Ejecutar el script didactico que despliega y crea un titulo en una red temporal de Hardhat:

```powershell
npx hardhat run scripts/crear-titulo.ts
```

Este script hace lo siguiente:

- Crea una red temporal de Hardhat.
- Despliega `RegistroTitulos`.
- Calcula hashes de un titulo de prueba.
- Llama a `registrarTitulo`.
- Llama a `verificarTitulo`.
- Imprime el resultado en consola.

La red temporal desaparece cuando termina el script.

## 4. Probar El Dockerfile De Blockchain

El Dockerfile de `blockchain` crea una imagen con Hardhat y los contratos.

Desde `proyecto/blockchain`:

```powershell
docker build -t registro-titulos .
```

Ejecutar el comando por defecto de la imagen:

```powershell
docker run --rm registro-titulos
```

El comando por defecto es:

```dockerfile
CMD ["npx", "hardhat", "compile"]
```

Tambien se puede reemplazar el comando por defecto:

```powershell
docker run --rm registro-titulos npx hardhat run scripts/crear-titulo.ts
```

Esto permite usar la imagen como herramienta de desarrollo para compilar o ejecutar scripts.

## 5. Levantar Ganache Con Docker Compose

Ganache es una blockchain local de desarrollo. Mantiene contratos, bloques y transacciones mientras el servicio conserva su estado.

Desde `proyecto`:

```powershell
docker compose up -d blockchain-node
```

Verificar el servicio:

```powershell
docker compose ps
```

Ver logs de Ganache:

```powershell
docker compose logs blockchain-node
```

Ganache queda disponible en:

```text
http://localhost:8545
```

Dentro de Docker Compose, los otros servicios lo consumen con:

```text
http://blockchain-node:8545
```

## 6. Desplegar El Contrato En Ganache

Desde `proyecto`:

```powershell
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

Salida esperada:

```text
Desplegando contrato RegistroTitulos...
Contrato desplegado correctamente
Direccion del contrato: 0x...
```

Copiar la direccion y reemplazarla en `.env`:

```env
CONTRACT_ADDRESS=0xDIRECCION_DEL_CONTRATO
```

## 7. Verificar Que El Contrato Existe En Ganache

Entrar a la consola de Hardhat conectada a Ganache:

```powershell
docker compose run --rm contract-tools npx hardhat console --network ganache
```

Dentro de la consola:

```javascript
const { viem } = await network.create()
const publicClient = await viem.getPublicClient()
await publicClient.getCode({ address: "0xDIRECCION_DEL_CONTRATO" })
```

Si devuelve algo como `0x608060...`, el contrato existe.

Si devuelve `0x` o `undefined`, no existe contrato en esa direccion.

Salir de la consola:

```javascript
.exit
```

## 8. Persistencia De Ganache

Ganache usa un volumen Docker:

```yaml
volumes:
  - ganache_data:/data
```

Y arranca con:

```yaml
--database.dbPath /data
```

Esto permite conservar el estado de la blockchain local entre reinicios normales.

Apagar sin borrar volumen:

```powershell
docker compose down
```

Levantar otra vez:

```powershell
docker compose up -d blockchain-node
```

Volver a verificar el bytecode del contrato con Hardhat console. Si el bytecode sigue apareciendo, el contrato persistio.

No usar este comando si se desea conservar el contrato:

```powershell
docker compose down -v
```

El parametro `-v` borra los volumenes.

## 9. Levantar PostgreSQL Y FastAPI

Desde `proyecto`:

```powershell
docker compose up -d --build blockchain-node postgres api-universidad
```

Verificar servicios:

```powershell
docker compose ps
```

Servicios esperados:

```text
blockchain-node   Up   8545
postgres          Up   5432
api-universidad   Up   8000
```

Swagger queda disponible en:

```text
http://localhost:8000/docs
```

## 10. API Universidad

La API esta en:

```text
api-universidad/
```

Componentes principales:

- `main.py`: define endpoints FastAPI.
- `database.py`: conexion SQLAlchemy a PostgreSQL.
- `models.py`: modelo `Titulo` y tabla `titulos`.
- `schemas.py`: modelos Pydantic para entrada y salida.
- `blockchain.py`: cliente Web3 para Ganache y contrato.
- `contracts/RegistroTitulos.json`: ABI minimo del contrato.

FastAPI crea la tabla automaticamente al iniciar:

```python
Base.metadata.create_all(bind=engine)
```

## 11. Endpoints Disponibles

Verificar API:

```http
GET /health
```

Verificar contrato configurado:

```http
GET /blockchain/contract
```

Crear titulo:

```http
POST /titulos
```

Consultar titulo desde PostgreSQL:

```http
GET /titulos/{codigo_titulo}
```

Verificar titulo contra blockchain:

```http
GET /titulos/{codigo_titulo}/verificar
```

## 12. Probar La API Con PowerShell

Verificar salud:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

Verificar contrato:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/blockchain/contract"
```

Crear titulo:

```powershell
$body = @{
  codigo_titulo = "UTPL-SIS-2026-API-0001"
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

Consultar titulo:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/titulos/UTPL-SIS-2026-API-0001"
```

Verificar contra blockchain:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/titulos/UTPL-SIS-2026-API-0001/verificar"
```

Respuesta esperada:

```text
existe_en_blockchain : True
documento_coincide   : True
```

## 13. Probar Desde Swagger

Abrir:

```text
http://localhost:8000/docs
```

Probar en este orden:

- `GET /health`
- `GET /blockchain/contract`
- `POST /titulos`
- `GET /titulos/{codigo_titulo}`
- `GET /titulos/{codigo_titulo}/verificar`

Ejemplo de body para `POST /titulos`:

```json
{
  "codigo_titulo": "UTPL-SIS-2026-API-0002",
  "nombre_estudiante": "Carlos Zamora",
  "identificacion_estudiante": "1100000003",
  "carrera": "Computacion",
  "titulo_obtenido": "Ingeniero en Computacion",
  "universidad": "UTPL",
  "fecha_emision": "2026-06-15",
  "contenido_documento": "Titulo de Carlos Zamora como Ingeniero en Computacion emitido por UTPL"
}
```

## 14. Que Se Guarda En PostgreSQL

La tabla `titulos` guarda:

- Codigo del titulo.
- Nombre del estudiante.
- Identificacion del estudiante.
- Carrera.
- Titulo obtenido.
- Universidad.
- Fecha de emision.
- Contenido del documento usado para calcular el hash.
- Hash del codigo del titulo.
- Hash del documento.
- Direccion del contrato.
- Hash de la transaccion blockchain.

Consultar la base desde Docker:

```powershell
docker compose exec postgres psql -U admin -d titulos_db
```

Dentro de `psql`:

```sql
SELECT id, codigo_titulo, codigo_titulo_hash, documento_hash, tx_hash FROM titulos;
```

Salir:

```sql
\q
```

## 15. Que Se Guarda En Blockchain

El contrato guarda:

- `codigoTituloHash`
- `documentoHash`
- `universidad`
- `fechaRegistro`
- `existe`

No guarda datos personales completos.

Esto permite verificar integridad sin exponer datos sensibles directamente en blockchain.

## 16. Comandos Utiles

Levantar toda la practica:

```powershell
docker compose up -d --build blockchain-node postgres api-universidad
```

Desplegar contrato:

```powershell
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

Ver logs de API:

```powershell
docker compose logs api-universidad
```

Ver logs de Ganache:

```powershell
docker compose logs blockchain-node
```

Ver logs de PostgreSQL:

```powershell
docker compose logs postgres
```

Apagar servicios sin borrar datos:

```powershell
docker compose down
```

Apagar y borrar volumenes:

```powershell
docker compose down -v
```

Usar `down -v` solo cuando se quiera reiniciar todo desde cero.

## 17. Flujo Completo Desde Cero

Desde `proyecto`:

```powershell
copy .env.example .env
docker compose up -d --build blockchain-node
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

Copiar la direccion del contrato en `.env`:

```env
CONTRACT_ADDRESS=0xDIRECCION_DEL_CONTRATO
```

Levantar API y base de datos:

```powershell
docker compose up -d --build postgres api-universidad
```

Abrir Swagger:

```text
http://localhost:8000/docs
```

Crear y verificar titulos desde Swagger.

## 18. Resultado Final

Al finalizar, se tiene un sistema local compuesto por:

- Una blockchain local persistente con Ganache.
- Un contrato Solidity desplegado en esa blockchain.
- Una API FastAPI documentada con Swagger.
- Una base PostgreSQL para los datos completos.
- Evidencia blockchain para verificar autenticidad e integridad.

Este proyecto sirve como base para continuar en las siguientes semanas con Kubernetes local, persistencia con PVC, jobs de despliegue de contratos y simulacion multi-cloud con clusters separados.
