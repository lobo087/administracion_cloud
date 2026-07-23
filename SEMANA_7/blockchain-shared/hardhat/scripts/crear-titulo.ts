import { network } from "hardhat";
import { keccak256, stringToHex } from "viem";

const { viem } = await network.create();

const contractAddress = process.env.CONTRACT_ADDRESS;

if (!contractAddress) {
  throw new Error("Falta configurar CONTRACT_ADDRESS");
}

const registroTitulos = await viem.getContractAt("RegistroTitulos", contractAddress as `0x${string}`);

const codigoTitulo = "UTPL-SIS-2026-0001";
const identificacionEstudiante = "1100000001";
const contenidoDocumento =
  "Titulo de Juan Perez como Ingeniero en Sistemas emitido por UTPL";
const universidadEmisora = "UTPL";
const carrera = "Sistemas";
const tituloObtenido = "Ingeniero en Sistemas";

const codigoTituloHash = keccak256(stringToHex(codigoTitulo));
const documentoHash = keccak256(stringToHex(contenidoDocumento));
const identificacionEstudianteHash = keccak256(stringToHex(identificacionEstudiante));

console.log("Codigo del titulo:", codigoTitulo);
console.log("Hash del codigo:", codigoTituloHash);
console.log("Hash del documento:", documentoHash);
console.log("Hash de identificacion:", identificacionEstudianteHash);

console.log("Registrando titulo en blockchain...");

const tx = await registroTitulos.write.registrarTitulo([
  codigoTituloHash,
  documentoHash,
  identificacionEstudianteHash,
  universidadEmisora,
  carrera,
  tituloObtenido,
]);

console.log("Transaccion enviada:", tx);

const resultado = await registroTitulos.read.verificarTitulo([
  codigoTituloHash,
  documentoHash,
  identificacionEstudianteHash,
]);

console.log("Resultado de verificacion:");
console.log("Existe:", resultado[0]);
console.log("Documento coincide:", resultado[1]);
console.log("Identificacion coincide:", resultado[2]);
console.log("Estado:", resultado[3]);

const titulo = await registroTitulos.read.obtenerTitulo([codigoTituloHash]);

console.log("Datos guardados en blockchain:");
console.log("codigoTituloHash:", titulo.codigoTituloHash);
console.log("documentoHash:", titulo.documentoHash);
console.log("identificacionEstudianteHash:", titulo.identificacionEstudianteHash);
console.log("universidadEmisora:", titulo.universidadEmisora);
console.log("universidad:", titulo.universidad);
console.log("estado:", titulo.estado);
console.log("fechaRegistro:", titulo.fechaRegistro);
console.log("existe:", titulo.existe);
