import { network } from "hardhat";

const { viem } = await network.create();

const contractAddress = process.env.CONTRACT_ADDRESS;
const universidadAddress = process.env.NUEVA_UNIVERSIDAD_ADDRESS || process.env.UDLA_ADDRESS;
const universidadNombre = process.env.NUEVA_UNIVERSIDAD_NOMBRE || process.env.UDLA_NOMBRE || "UDLA";

if (!contractAddress) {
  throw new Error("Falta configurar CONTRACT_ADDRESS");
}

if (!universidadAddress) {
  throw new Error("Falta configurar NUEVA_UNIVERSIDAD_ADDRESS o UDLA_ADDRESS");
}

const [ministerio] = await viem.getWalletClients();
const registroTitulos = await viem.getContractAt("RegistroTitulos", contractAddress as `0x${string}`);

console.log("Autorizando universidad desde Ministerio:", ministerio.account.address);
console.log("Universidad:", universidadNombre, universidadAddress);

const txHash = await registroTitulos.write.autorizarUniversidad([
  universidadAddress as `0x${string}`,
  universidadNombre,
]);

console.log("Universidad autorizada correctamente");
console.log("Tx hash:", txHash);
