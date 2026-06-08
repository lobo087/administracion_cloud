const { expect } = require("chai");

describe("HolaUTPL", function () {
  it("guarda el mensaje inicial", async function () {
    const HolaUTPL = await ethers.getContractFactory("HolaUTPL");
    const contrato = await HolaUTPL.deploy("Hola prueba");
    await contrato.waitForDeployment();

    expect(await contrato.mensaje()).to.equal("Hola prueba");
  });

  it("actualiza el mensaje", async function () {
    const HolaUTPL = await ethers.getContractFactory("HolaUTPL");
    const contrato = await HolaUTPL.deploy("Mensaje inicial");
    await contrato.waitForDeployment();

    await contrato.actualizarMensaje("Nuevo mensaje");
    expect(await contrato.mensaje()).to.equal("Nuevo mensaje");
  });
});
