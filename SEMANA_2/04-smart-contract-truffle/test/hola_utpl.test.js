const HolaUTPL = artifacts.require("HolaUTPL");

contract("HolaUTPL", () => {
  it("guarda el mensaje inicial", async () => {
    const contrato = await HolaUTPL.new("Hola prueba");
    const mensaje = await contrato.mensaje();
    assert.equal(mensaje, "Hola prueba");
  });

  it("actualiza el mensaje", async () => {
    const contrato = await HolaUTPL.new("Mensaje inicial");
    await contrato.actualizarMensaje("Nuevo mensaje");
    const mensaje = await contrato.mensaje();
    assert.equal(mensaje, "Nuevo mensaje");
  });
});
