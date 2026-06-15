import { network } from "hardhat";
import { keccak256, stringToHex } from "viem";

const { viem } = await network.create();

console.log("Desplegando contrato RegistroTitulos...");

const registroTitulos = await viem.deployContract("RegistroTitulos");

console.log("Contrato desplegado en:", registroTitulos.address);

const codigoTitulo = "UTPL-SIS-2026-0001";
const contenidoDocumento =
  "Titulo de Juan Perez como Ingeniero en Sistemas emitido por UTPL";

const codigoTituloHash = keccak256(stringToHex(codigoTitulo));
const documentoHash = keccak256(stringToHex(contenidoDocumento));

console.log("Codigo del titulo:", codigoTitulo);
console.log("Hash del codigo:", codigoTituloHash);
console.log("Hash del documento:", documentoHash);

console.log("Registrando titulo en blockchain...");

const tx = await registroTitulos.write.registrarTitulo([
  codigoTituloHash,
  documentoHash,
]);

console.log("Transaccion enviada:", tx);

const resultado = await registroTitulos.read.verificarTitulo([
  codigoTituloHash,
  documentoHash,
]);

console.log("Resultado de verificacion:");
console.log("Existe:", resultado[0]);
console.log("Documento coincide:", resultado[1]);

const titulo = await registroTitulos.read.obtenerTitulo([codigoTituloHash]);

console.log("Datos guardados en blockchain:");
console.log("codigoTituloHash:", titulo[0]);
console.log("documentoHash:", titulo[1]);
console.log("universidad:", titulo[2]);
console.log("fechaRegistro:", titulo[3]);
console.log("existe:", titulo[4]);