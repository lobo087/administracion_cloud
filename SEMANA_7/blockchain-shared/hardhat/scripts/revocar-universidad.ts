import { network } from "hardhat";

const { viem } = await network.create();

const contractAddress = process.env.CONTRACT_ADDRESS;
const universidadAddress = process.env.NUEVA_UNIVERSIDAD_ADDRESS || process.env.UDLA_ADDRESS;

if (!contractAddress) {
  throw new Error("Falta configurar CONTRACT_ADDRESS");
}

if (!universidadAddress) {
  throw new Error("Falta configurar NUEVA_UNIVERSIDAD_ADDRESS o UDLA_ADDRESS");
}

const [ministerio] = await viem.getWalletClients();
const registroTitulos = await viem.getContractAt("RegistroTitulos", contractAddress as `0x${string}`);

console.log("Revocando universidad desde Ministerio:", ministerio.account.address);
console.log("Universidad:", universidadAddress);

const txHash = await registroTitulos.write.revocarUniversidad([universidadAddress as `0x${string}`]);

console.log("Universidad revocada correctamente");
console.log("Tx hash:", txHash);
