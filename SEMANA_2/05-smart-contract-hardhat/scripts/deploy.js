const fs = require("fs");

async function main() {
  const HolaUTPL = await ethers.getContractFactory("HolaUTPL");
  const contrato = await HolaUTPL.deploy("Hola desde Hardhat en Docker");
  await contrato.waitForDeployment();

  const address = await contrato.getAddress();
  fs.writeFileSync("deployment.json", JSON.stringify({ address }, null, 2));

  console.log("Contrato desplegado en:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
