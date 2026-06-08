const HolaUTPL = artifacts.require("HolaUTPL");

module.exports = async function (callback) {
  try {
    const contrato = await HolaUTPL.deployed();
    const mensajeInicial = await contrato.mensaje();
    console.log("Mensaje inicial:", mensajeInicial);

    await contrato.actualizarMensaje("Mensaje actualizado desde Truffle");
    const mensajeActualizado = await contrato.mensaje();
    console.log("Mensaje actualizado:", mensajeActualizado);

    callback();
  } catch (error) {
    callback(error);
  }
};
