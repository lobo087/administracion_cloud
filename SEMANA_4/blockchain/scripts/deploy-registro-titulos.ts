import { network } from "hardhat";

const { viem } = await network.create();

console.log("Desplegando contrato RegistroTitulos...");

const registroTitulos = await viem.deployContract("RegistroTitulos");

console.log("Contrato desplegado correctamente");
console.log("Direccion del contrato:", registroTitulos.address);