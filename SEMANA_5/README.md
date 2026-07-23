# Semana 5 - Auditoria internacional y roles en blockchain

Esta practica evoluciona la Semana 4 agregando un tercer actor: una universidad auditora extranjera que verifica titulos academicos antes de admitir estudiantes.

## Objetivo

Demostrar un flujo donde:

- El Ministerio regula que universidades pueden registrar titulos.
- Universidades autorizadas como UTPL o UDLA registran titulos.
- El Ministerio avala titulos registrados.
- La Auditora verifica documento, identificacion del estudiante, aval ministerial y autorizacion de la universidad emisora.
- La Auditora guarda historial local de cada verificacion.

## Actores

| Actor | API | Puerto | Responsabilidad |
| --- | --- | --- | --- |
| Universidad emisora | `api-universidad` | `8000` | Registrar titulos si esta autorizada |
| Ministerio | `api-ministerio` | `8002` | Autorizar universidades y avalar titulos |
| Universidad auditora extranjera | `api-auditora` | `8003` | Verificar titulos y guardar historial |

## Regla clave

El contrato se despliega una sola vez. Si llega una nueva universidad, no se redespliega el contrato. El Ministerio ejecuta una transaccion para autorizarla:

```text
Ministerio -> autorizarUniversidad(UDLA)
```

Desde ese momento UDLA puede registrar titulos en el mismo contrato.

## Contrato

Archivo:

```text
blockchain/contracts/RegistroTitulos.sol
```

El contrato tiene:

- `ministerioPrincipal`.
- `mapping(address => UniversidadAutorizada)`.
- `autorizarUniversidad(address universidad, string nombre)`.
- `revocarUniversidad(address universidad)`.
- `registrarTitulo(...)` protegido para universidades autorizadas.
- `avalarTitulo(...)` protegido para el Ministerio.
- funciones publicas de consulta para la Auditora.

## Flujo principal

```text
1. Se despliega el contrato con Ministerio principal y UTPL inicial.
2. UTPL registra un titulo.
3. Ministerio consulta y avala el titulo.
4. Auditora verifica el titulo presentado por el estudiante.
5. Auditora guarda el resultado en PostgreSQL propio.
6. Ministerio autoriza UDLA sin redesplegar contrato.
7. UDLA puede registrar titulos en el mismo contrato.
```

## Variables de entorno

Crear `.env` desde `.env.example`:

```powershell
copy .env.example .env
```

Variables principales:

```env
GANACHE_RPC_URL=http://blockchain-node:8545
GANACHE_PRIVATE_KEY=...
MINISTERIO_PRIVATE_KEY=...
UDLA_PRIVATE_KEY=...

UNIVERSIDAD_ADDRESS=...
UNIVERSIDAD_NOMBRE=UTPL
MINISTERIO_ADDRESS=...
UDLA_ADDRESS=...
UDLA_NOMBRE=UDLA

CONTRACT_ADDRESS=0xREEMPLAZAR_CON_LA_DIRECCION_DEL_CONTRATO
```

## Despliegue desde cero

Ejecutar desde `SEMANA_5`.

### 1. Levantar Ganache

```powershell
docker compose up -d blockchain-node
```

### 2. Compilar y desplegar contrato

```powershell
docker compose build contract-tools
docker compose run --rm contract-tools npx hardhat compile
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

Copiar la direccion impresa en `.env`:

```env
CONTRACT_ADDRESS=0x...
```

### 3. Levantar APIs y bases

```powershell
docker compose up -d --build postgres-universidad api-universidad postgres-ministerio api-ministerio postgres-auditora api-auditora
```

Swagger:

```text
http://localhost:8000/docs
http://localhost:8002/docs
http://localhost:8003/docs
```

## Autorizar una nueva universidad

Desde API Ministerio:

```http
POST http://localhost:8002/universidades
```

Body:

```json
{
  "nombre": "UDLA",
  "address": "0x22d491bde2303f2f43325b2108c7e439c87a1243"
}
```

Tambien se puede usar Hardhat con la red `ganacheMinisterio`:

```powershell
docker compose run --rm contract-tools npx hardhat run scripts/autorizar-universidad.ts --network ganacheMinisterio
```

## Registrar titulo

API Universidad:

```http
POST http://localhost:8000/titulos
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

## Avalar titulo

API Ministerio:

```http
POST http://localhost:8002/titulos/UTPL-SIS-2026-0002/avalar
```

## Verificar desde la Auditora

API Auditora:

```http
POST http://localhost:8003/verificar
```

Body:

```json
{
  "codigo_titulo": "UTPL-SIS-2026-0002",
  "identificacion_estudiante": "1100000002",
  "contenido_documento": "Titulo de Maria Loja como Ingeniera en Sistemas emitido por UTPL"
}
```

La auditora calcula hashes localmente y valida:

- El titulo existe.
- El documento coincide.
- La identificacion del estudiante coincide.
- El estado es `AVALADO`.
- Existe un Ministerio validador.
- La universidad emisora esta autorizada.

Si todo cumple, devuelve `apto_para_admision = true` y guarda el historial en `auditorias_titulos`.

## Pruebas negativas esperadas

- Si el documento cambia, `documento_coincide = false`.
- Si la identificacion cambia, `identificacion_coincide = false`.
- Si el titulo no esta avalado, `apto_para_admision = false`.
- Si una universidad fue revocada, no puede registrar nuevos titulos.
- Si el Ministerio intenta registrar titulos, el contrato rechaza.
- Si la Universidad intenta avalar titulos, el contrato rechaza.

## Resultado final

Semana 5 deja implementada una red academica con tres actores, control de roles en blockchain, universidades autorizadas dinamicamente por el Ministerio y auditoria internacional con historial local.
