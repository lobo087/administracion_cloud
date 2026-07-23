import { network } from "hardhat";

const { viem } = await network.create();

const ministerioAddress = process.env.MINISTERIO_ADDRESS;
const universidadInicialAddress = process.env.UNIVERSIDAD_ADDRESS;
const universidadInicialNombre = process.env.UNIVERSIDAD_NOMBRE || "UTPL";

if (!ministerioAddress) {
  throw new Error("Falta configurar MINISTERIO_ADDRESS");
}

if (!universidadInicialAddress) {
  throw new Error("Falta configurar UNIVERSIDAD_ADDRESS");
}

console.log("Desplegando contrato RegistroTitulos...");
console.log("Ministerio principal:", ministerioAddress);
console.log("Universidad inicial:", universidadInicialNombre, universidadInicialAddress);

const registroTitulos = await viem.deployContract("RegistroTitulos", [
  ministerioAddress as `0x${string}`,
  universidadInicialAddress as `0x${string}`,
  universidadInicialNombre,
]);

console.log("Contrato desplegado correctamente");
console.log("Direccion del contrato:", registroTitulos.address);
