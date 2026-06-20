import { network } from "hardhat";

const { viem } = await network.create();

console.log("Desplegando contrato RegistroEvidenciasForenses...");

const registroEvidencias = await viem.deployContract("RegistroEvidenciasForenses");

console.log("Contrato desplegado correctamente");
console.log("Direccion del contrato:", registroEvidencias.address);
