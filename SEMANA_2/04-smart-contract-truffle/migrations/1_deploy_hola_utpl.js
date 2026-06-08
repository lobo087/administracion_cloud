const HolaUTPL = artifacts.require("HolaUTPL");

module.exports = function (deployer) {
  deployer.deploy(HolaUTPL, "Hola desde Truffle en Docker");
};
