import express from "express";
import os from "node:os";
import {
  createPublicClient,
  createWalletClient,
  defineChain,
  http,
  isAddress,
  keccak256,
  toHex,
} from "viem";
import { privateKeyToAccount } from "viem/accounts";

const PORT = Number(process.env.PORT || 3000);
const RPC_URL = process.env.BLOCKCHAIN_RPC_URL || "http://geth-utpl:8545";
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS || "";
const PRIVATE_KEY = process.env.API_PRIVATE_KEY || "";
const CHAIN_ID = Number(process.env.CHAIN_ID || 202606);

const chain = defineChain({
  id: CHAIN_ID,
  name: "Red Forense Privada",
  nativeCurrency: { name: "Forensic Ether", symbol: "FETH", decimals: 18 },
  rpcUrls: { default: { http: [RPC_URL] } },
});

const publicClient = createPublicClient({ chain, transport: http(RPC_URL) });
const account = PRIVATE_KEY ? privateKeyToAccount(PRIVATE_KEY) : undefined;
const walletClient = account
  ? createWalletClient({ account, chain, transport: http(RPC_URL) })
  : undefined;

const contractAbi = [
  {
    type: "function",
    name: "registrarEvidencia",
    stateMutability: "nonpayable",
    inputs: [
      { name: "codigoEvidenciaHash", type: "bytes32" },
      { name: "evidenciaHash", type: "bytes32" },
      { name: "casoHash", type: "bytes32" },
    ],
    outputs: [],
  },
  {
    type: "function",
    name: "verificarEvidencia",
    stateMutability: "view",
    inputs: [
      { name: "codigoEvidenciaHash", type: "bytes32" },
      { name: "evidenciaHash", type: "bytes32" },
    ],
    outputs: [
      { name: "existe", type: "bool" },
      { name: "evidenciaCoincide", type: "bool" },
    ],
  },
  {
    type: "function",
    name: "obtenerEvidencia",
    stateMutability: "view",
    inputs: [{ name: "codigoEvidenciaHash", type: "bytes32" }],
    outputs: [
      { name: "codigo", type: "bytes32" },
      { name: "hash", type: "bytes32" },
      { name: "caso", type: "bytes32" },
      { name: "registrador", type: "address" },
      { name: "fechaRegistro", type: "uint256" },
      { name: "existe", type: "bool" },
    ],
  },
];

function asBytes32(value, fieldName) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${fieldName} es obligatorio`);
  }
  const clean = value.trim();
  if (/^0x[0-9a-fA-F]{64}$/.test(clean)) return clean;
  if (/^[0-9a-fA-F]{64}$/.test(clean)) return `0x${clean}`;
  return keccak256(toHex(clean));
}

function requireContract() {
  if (!isAddress(CONTRACT_ADDRESS)) {
    throw new Error("CONTRACT_ADDRESS no está configurada correctamente");
  }
}

const app = express();
app.use(express.json({ limit: "256kb" }));

app.get("/", (_req, res) => {
  res.json({
    service: "forense-api",
    pod: os.hostname(),
    replicas: 3,
    rpc: RPC_URL,
  });
});

app.get("/health", async (_req, res) => {
  try {
    const blockNumber = await publicClient.getBlockNumber();
    const chainId = await publicClient.getChainId();
    res.json({
      status: "ok",
      pod: os.hostname(),
      chainId,
      blockNumber: blockNumber.toString(),
      contractConfigured: isAddress(CONTRACT_ADDRESS),
      signerConfigured: Boolean(account),
    });
  } catch (error) {
    res.status(503).json({
      status: "error",
      pod: os.hostname(),
      error: error.message,
    });
  }
});

app.post("/evidencias", async (req, res) => {
  try {
    requireContract();
    if (!walletClient || !account) {
      throw new Error("API_PRIVATE_KEY no está configurada");
    }

    const codigoHash = asBytes32(
      req.body.codigoEvidencia,
      "codigoEvidencia"
    );
    const evidenciaHash = asBytes32(
      req.body.hashEvidencia,
      "hashEvidencia"
    );
    const casoHash = asBytes32(req.body.caso, "caso");

    const simulation = await publicClient.simulateContract({
      address: CONTRACT_ADDRESS,
      abi: contractAbi,
      functionName: "registrarEvidencia",
      args: [codigoHash, evidenciaHash, casoHash],
      account,
    });

    const transactionHash = await walletClient.writeContract(
      simulation.request
    );
    const receipt = await publicClient.waitForTransactionReceipt({
      hash: transactionHash,
    });

    res.status(201).json({
      message: "Evidencia registrada",
      pod: os.hostname(),
      transactionHash,
      blockNumber: receipt.blockNumber.toString(),
      codigoEvidenciaHash: codigoHash,
      evidenciaHash,
      casoHash,
    });
  } catch (error) {
    res.status(400).json({ error: error.message, pod: os.hostname() });
  }
});

app.post("/evidencias/verificar", async (req, res) => {
  try {
    requireContract();
    const codigoHash = asBytes32(
      req.body.codigoEvidencia,
      "codigoEvidencia"
    );
    const evidenciaHash = asBytes32(
      req.body.hashEvidencia,
      "hashEvidencia"
    );

    const [existe, evidenciaCoincide] = await publicClient.readContract({
      address: CONTRACT_ADDRESS,
      abi: contractAbi,
      functionName: "verificarEvidencia",
      args: [codigoHash, evidenciaHash],
    });

    res.json({ existe, evidenciaCoincide, pod: os.hostname() });
  } catch (error) {
    res.status(400).json({ error: error.message, pod: os.hostname() });
  }
});

app.get("/evidencias/:codigo", async (req, res) => {
  try {
    requireContract();
    const codigoHash = asBytes32(req.params.codigo, "codigo");

    const result = await publicClient.readContract({
      address: CONTRACT_ADDRESS,
      abi: contractAbi,
      functionName: "obtenerEvidencia",
      args: [codigoHash],
    });

    res.json({
      codigoEvidenciaHash: result[0],
      evidenciaHash: result[1],
      casoHash: result[2],
      registrador: result[3],
      fechaRegistroUnix: result[4].toString(),
      fechaRegistroISO: result[5]
        ? new Date(Number(result[4]) * 1000).toISOString()
        : null,
      existe: result[5],
      pod: os.hostname(),
    });
  } catch (error) {
    res.status(400).json({ error: error.message, pod: os.hostname() });
  }
});

app.use((error, _req, res, _next) => {
  res.status(400).json({ error: error.message, pod: os.hostname() });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`forense-api escuchando en ${PORT}; pod=${os.hostname()}`);
});
