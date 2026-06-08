const fs = require("fs");

async function main() {
  const deployment = JSON.parse(fs.readFileSync("deployment.json", "utf8"));
  const contrato = await ethers.getContractAt("HolaUTPL", deployment.address);

  const mensajeInicial = await contrato.mensaje();
  console.log("Mensaje inicial:", mensajeInicial);

  const tx = await contrato.actualizarMensaje("Mensaje actualizado desde Hardhat");
  await tx.wait();

  const mensajeActualizado = await contrato.mensaje();
  console.log("Mensaje actualizado:", mensajeActualizado);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
