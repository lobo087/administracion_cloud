# Blockchain - RegistroTitulos

Proyecto Hardhat 3 usado en la Semana 3 para compilar, probar y desplegar el contrato `RegistroTitulos`.

## Comandos

Instalar dependencias:

```powershell
npm install
```

Compilar:

```powershell
npx hardhat compile
```

Ejecutar demo local con red temporal de Hardhat:

```powershell
npx hardhat run scripts/crear-titulo.ts
```

Desplegar en Ganache desde `SEMANA_3`:

```powershell
docker compose run --rm contract-tools npx hardhat run scripts/deploy-registro-titulos.ts --network ganache
```

La documentacion completa de la practica esta en `SEMANA_3/README.md`.
