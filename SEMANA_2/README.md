# Semana 2: Docker Compose, persistencia y contratos inteligentes

Esta semana trabaja Docker Compose desde ejemplos simples hasta un primer acercamiento a contratos inteligentes con Solidity. El objetivo es comprender servicios, redes internas, bases de datos efimeras, volumenes persistentes y herramientas blockchain ejecutadas en contenedores.

## Contenido

| Ejercicio | Tema | Persistencia | Puerto principal |
| --- | --- | --- | --- |
| `01-nginx-hola-mundo` | Nginx con HTML simple | No aplica | `8080` |
| `02-fastapi-mysql-efimero` | FastAPI + MySQL estudiantes | No persistente | `8000` |
| `03-fastapi-mysql-persistente` | FastAPI + MySQL materias | Volumen Docker | `8001` |
| `04-smart-contract-truffle` | Solidity con Truffle + Ganache | Blockchain local efimera | `8545` |
| `05-smart-contract-hardhat` | Solidity con Hardhat | Blockchain local efimera | `8546` |

## Comandos generales de Docker Compose

Levantar servicios en primer plano:

```bash
docker compose up --build
```

Levantar servicios en segundo plano:

```bash
docker compose up -d --build
```

Ver servicios activos:

```bash
docker compose ps
```

Ver logs:

```bash
docker compose logs
```

Ver logs de un servicio especifico:

```bash
docker compose logs api
docker compose logs mysql
```

Detener y eliminar contenedores del proyecto:

```bash
docker compose down
```

Detener y eliminar contenedores junto con volumenes del proyecto:

```bash
docker compose down -v
```

Listar volumenes Docker:

```bash
docker volume ls
```

Inspeccionar un volumen:

```bash
docker volume inspect NOMBRE_DEL_VOLUMEN
```

Eliminar un volumen especifico:

```bash
docker volume rm NOMBRE_DEL_VOLUMEN
```

Ver uso de espacio de Docker:

```bash
docker system df
```

Limpiar recursos no usados:

```bash
docker container prune
docker image prune
docker volume prune
docker system prune
```

Usa `docker volume prune` y `docker system prune` con cuidado porque pueden eliminar recursos no usados de otros proyectos.

## Ejercicio 1: Nginx Hola Mundo

Carpeta:

```bash
cd SEMANA_2/01-nginx-hola-mundo
```

Este ejercicio levanta una pagina HTML sencilla usando Nginx. Sirve para introducir un servicio simple de Docker Compose y el mapeo de puertos.

Levantar el servicio:

```bash
docker compose up --build
```

Abrir en el navegador:

```text
http://localhost:8080
```

Detener:

```bash
docker compose down
```

## Ejercicio 2: FastAPI + MySQL efimero

Carpeta:

```bash
cd SEMANA_2/02-fastapi-mysql-efimero
```

Este ejercicio levanta dos servicios: una API con FastAPI y una base MySQL. La base de datos no usa volumen, por lo que los datos se pierden cuando el proyecto se elimina con `docker compose down`.

Base de datos:

```text
universidad
```

Tabla:

```text
estudiantes(id, nombre, carrera, nota_promedio)
```

Levantar servicios:

```bash
docker compose up --build
```

Levantar en segundo plano:

```bash
docker compose up -d --build
```

Ver servicios:

```bash
docker compose ps
```

Ver logs:

```bash
docker compose logs api
docker compose logs mysql
```

### Endpoints para Postman

Listar estudiantes:

```text
GET http://localhost:8000/estudiantes
```

Obtener estudiante por ID:

```text
GET http://localhost:8000/estudiantes/1
```

Crear estudiante:

```text
POST http://localhost:8000/estudiantes
```

Body JSON:

```json
{
  "nombre": "Ana Torres",
  "carrera": "Sistemas de Informacion",
  "nota_promedio": 9.25
}
```

Otro ejemplo:

```json
{
  "nombre": "Luis Perez",
  "carrera": "Blockchain y Arquitectura en la Nube",
  "nota_promedio": 8.75
}
```

### Consultas SQL internas

Entrar al contenedor MySQL:

```bash
docker compose exec mysql mysql -u root -p
```

Cuando solicite clave, usar:

```text
root
```

Sentencias SQL:

```sql
USE universidad;
SHOW TABLES;
DESCRIBE estudiantes;
SELECT * FROM estudiantes;
SELECT nombre, carrera, nota_promedio FROM estudiantes;
```

Salir de MySQL:

```sql
exit;
```

### Demostracion de base efimera

1. Levantar servicios:

```bash
docker compose up -d --build
```

2. Crear estudiantes desde Postman usando `POST http://localhost:8000/estudiantes`.

3. Confirmar datos en MySQL:

```bash
docker compose exec mysql mysql -u root -p
```

```sql
USE universidad;
SELECT * FROM estudiantes;
```

4. Detener y eliminar contenedores:

```bash
docker compose down
```

5. Levantar nuevamente:

```bash
docker compose up -d --build
```

6. Consultar otra vez:

```bash
docker compose exec mysql mysql -u root -p
```

```sql
USE universidad;
SELECT * FROM estudiantes;
```

Resultado esperado: la tabla existe porque la API la crea al iniciar, pero los registros anteriores ya no estan.

Detener al finalizar:

```bash
docker compose down
```

## Ejercicio 3: FastAPI + MySQL persistente

Carpeta:

```bash
cd SEMANA_2/03-fastapi-mysql-persistente
```

Este ejercicio repite la arquitectura FastAPI + MySQL, pero ahora MySQL usa un volumen llamado `mysql_materias_data`. Esto permite que los datos sobrevivan aunque los contenedores se eliminen.

Base de datos:

```text
universidad
```

Tabla:

```text
materias(id, nombre, horas, profesor, carrera)
```

Levantar servicios:

```bash
docker compose up --build
```

Levantar en segundo plano:

```bash
docker compose up -d --build
```

Ver volumenes:

```bash
docker volume ls
```

### Endpoints para Postman

Listar materias:

```text
GET http://localhost:8001/materias
```

Obtener materia por ID:

```text
GET http://localhost:8001/materias/1
```

Crear materia:

```text
POST http://localhost:8001/materias
```

Body JSON:

```json
{
  "nombre": "Arquitectura en la Nube",
  "horas": 48,
  "profesor": "Jonathan Rosero",
  "carrera": "Blockchain y Arquitectura en la Nube"
}
```

Otro ejemplo:

```json
{
  "nombre": "Contratos Inteligentes",
  "horas": 32,
  "profesor": "Docente UTPL",
  "carrera": "Sistemas de Informacion"
}
```

### Consultas SQL internas

Entrar al contenedor MySQL:

```bash
docker compose exec mysql mysql -u root -p
```

Clave:

```text
root
```

Sentencias SQL:

```sql
USE universidad;
SHOW TABLES;
DESCRIBE materias;
SELECT * FROM materias;
SELECT nombre, horas, profesor, carrera FROM materias;
```

Salir:

```sql
exit;
```

### Demostracion de persistencia

1. Levantar servicios:

```bash
docker compose up -d --build
```

2. Crear materias desde Postman usando `POST http://localhost:8001/materias`.

3. Confirmar datos en MySQL:

```bash
docker compose exec mysql mysql -u root -p
```

```sql
USE universidad;
SELECT * FROM materias;
```

4. Detener y eliminar contenedores, sin borrar volumenes:

```bash
docker compose down
```

5. Levantar nuevamente:

```bash
docker compose up -d --build
```

6. Consultar otra vez:

```bash
docker compose exec mysql mysql -u root -p
```

```sql
USE universidad;
SELECT * FROM materias;
```

Resultado esperado: los registros siguen existiendo porque MySQL guarda los datos en el volumen.

### Limpiar datos persistentes

Eliminar contenedores y volumenes del proyecto:

```bash
docker compose down -v
```

Verificar volumenes:

```bash
docker volume ls
```

Si se desea eliminar manualmente un volumen especifico:

```bash
docker volume rm NOMBRE_DEL_VOLUMEN
```

Revisar espacio ocupado por Docker:

```bash
docker system df
```

Limpieza general de volumenes no usados:

```bash
docker volume prune
```

## Ejercicio 4: Smart Contract con Truffle

Carpeta:

```bash
cd SEMANA_2/04-smart-contract-truffle
```

Este ejercicio usa Solidity, Truffle y Ganache. Ganache simula una blockchain local Ethereum. Truffle compila, prueba, despliega e interactua con el contrato.

Contrato:

```text
contracts/HolaUTPL.sol
```

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

Desplegar contrato:

```bash
docker compose run --rm truffle npx truffle migrate --network development
```

Interactuar con el contrato:

```bash
docker compose run --rm truffle npx truffle exec scripts/interact.js --network development
```

Ver servicios:

```bash
docker compose ps
```

Ver logs de Ganache:

```bash
docker compose logs ganache
```

Detener:

```bash
docker compose down
```

Limpiar dependencias generadas en volumen:

```bash
docker compose down -v
```

### Preparar imagen para Docker Hub

Construir imagen con nombre local:

```bash
docker build -t smart-contract-truffle-docker:1.0.0 .
```

Construir imagen con usuario de Docker Hub:

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

Descargar y probar imagen:

```bash
docker pull TU_USUARIO_DOCKERHUB/smart-contract-truffle-docker:1.0.0
docker run --rm TU_USUARIO_DOCKERHUB/smart-contract-truffle-docker:1.0.0
```

La imagen ejecuta `truffle compile` por defecto. Para pruebas, migraciones e interaccion con Ganache, usar los comandos con `docker compose`.

## Ejercicio 5: Smart Contract con Hardhat

Carpeta:

```bash
cd SEMANA_2/05-smart-contract-hardhat
```

Este ejercicio usa el mismo contrato, pero con Hardhat. Permite comparar el flujo de trabajo de Hardhat con Truffle.

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

Desplegar contrato en el nodo local:

```bash
docker compose run --rm hardhat npx hardhat run scripts/deploy.js --network localhost
```

Interactuar con el contrato desplegado:

```bash
docker compose run --rm hardhat npx hardhat run scripts/interact.js --network localhost
```

Ver logs del nodo:

```bash
docker compose logs hardhat-node
```

Detener:

```bash
docker compose down
```

Limpiar volumen de dependencias:

```bash
docker compose down -v
```

## Idea clave sobre blockchain en contenedores

Contenerizar herramientas blockchain es muy util para aprendizaje porque evita instalar Node.js, Truffle, Hardhat, Ganache o compiladores Solidity directamente en la maquina. Tambien permite que todos los estudiantes ejecuten el mismo entorno.

Para produccion se debe tener mas cuidado con persistencia, claves privadas, monitoreo, backups, redes, rendimiento y seguridad. En esta semana el objetivo es didactico: comprobar que se puede compilar, probar, desplegar e interactuar con contratos inteligentes usando contenedores.
