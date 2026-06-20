import { network } from "hardhat";
import { keccak256, stringToHex } from "viem";

const { viem } = await network.create();

console.log("Desplegando contrato RegistroEvidenciasForenses...");

const registroEvidencias = await viem.deployContract("RegistroEvidenciasForenses");

console.log("Contrato desplegado en:", registroEvidencias.address);

const codigoEvidencia = "EVD-CASO-2026-0001";
const identificadorCaso = "CASO-FOR-2026-001";
const contenidoEvidencia =
  "Imagen forense de memoria USB Kingston 32GB incautada en el caso CASO-FOR-2026-001";

const codigoEvidenciaHash = keccak256(stringToHex(codigoEvidencia));
const evidenciaHash = keccak256(stringToHex(contenidoEvidencia));
const casoHash = keccak256(stringToHex(identificadorCaso));

console.log("Codigo de evidencia:", codigoEvidencia);
console.log("Identificador del caso:", identificadorCaso);
console.log("Hash del codigo de evidencia:", codigoEvidenciaHash);
console.log("Hash de la evidencia:", evidenciaHash);
console.log("Hash del caso:", casoHash);

console.log("Registrando evidencia en blockchain...");

const tx = await registroEvidencias.write.registrarEvidencia([
  codigoEvidenciaHash,
  evidenciaHash,
  casoHash,
]);

console.log("Transaccion enviada:", tx);

const resultado = await registroEvidencias.read.verificarEvidencia([
  codigoEvidenciaHash,
  evidenciaHash,
]);

console.log("Resultado de verificacion de integridad:");
console.log("Existe:", resultado[0]);
console.log("Evidencia coincide:", resultado[1]);

const contenidoAlterado = contenidoEvidencia + " - MODIFICADO";
const evidenciaAlteradaHash = keccak256(stringToHex(contenidoAlterado));

const resultadoAlterado = await registroEvidencias.read.verificarEvidencia([
  codigoEvidenciaHash,
  evidenciaAlteradaHash,
]);

console.log("Resultado de verificacion con evidencia alterada:");
console.log("Existe:", resultadoAlterado[0]);
console.log("Evidencia coincide:", resultadoAlterado[1]);

const evidencia = await registroEvidencias.read.obtenerEvidencia([
  codigoEvidenciaHash,
]);

console.log("Datos guardados en blockchain:");
console.log("codigoEvidenciaHash:", evidencia[0]);
console.log("evidenciaHash:", evidencia[1]);
console.log("casoHash:", evidencia[2]);
console.log("registrador:", evidencia[3]);
console.log("fechaRegistro:", evidencia[4]);
console.log("existe:", evidencia[5]);
