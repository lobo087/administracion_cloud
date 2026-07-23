import json
import os
from pathlib import Path

from web3 import Web3


ABI_PATH = Path(__file__).parent / "contracts" / "RegistroTitulos.json"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def get_web3() -> Web3:
    rpc_url = os.getenv("GANACHE_RPC_URL", "http://blockchain-node:8545")
    return Web3(Web3.HTTPProvider(rpc_url))


def get_contract_address() -> str:
    contract_address = os.getenv("CONTRACT_ADDRESS")

    if not contract_address:
        raise RuntimeError("Falta configurar CONTRACT_ADDRESS")

    return Web3.to_checksum_address(contract_address)


def get_contract():
    with ABI_PATH.open("r", encoding="utf-8") as abi_file:
        artifact = json.load(abi_file)

    abi = artifact.get("abi", artifact) if isinstance(artifact, dict) else artifact

    web3 = get_web3()
    return web3.eth.contract(address=get_contract_address(), abi=abi)


def hash_text(value: str) -> str:
    return Web3.to_hex(Web3.keccak(text=value))


def verify_contract_exists() -> bool:
    web3 = get_web3()
    code = web3.eth.get_code(get_contract_address())
    return code not in (b"", "0x")


def estado_titulo_to_text(estado: int) -> str:
    estados = {
        0: "NO_EXISTE",
        1: "REGISTRADO",
        2: "AVALADO",
        3: "RECHAZADO",
        4: "REVOCADO",
    }
    return estados.get(estado, "DESCONOCIDO")


def _bytes_to_hex(value: bytes) -> str:
    return Web3.to_hex(value)


def _titulo_to_dict(titulo) -> dict:
    estado = int(titulo[8])
    return {
        "codigo_titulo_hash": _bytes_to_hex(titulo[0]),
        "documento_hash": _bytes_to_hex(titulo[1]),
        "identificacion_estudiante_hash": _bytes_to_hex(titulo[2]),
        "universidad_emisora": titulo[3],
        "carrera": titulo[4],
        "titulo_obtenido": titulo[5],
        "universidad": titulo[6],
        "ministerio_validador": titulo[7],
        "estado": estado,
        "estado_descripcion": estado_titulo_to_text(estado),
        "fecha_registro": int(titulo[9]),
        "fecha_aval": int(titulo[10]),
        "existe": bool(titulo[11]),
    }


def get_title_by_code(codigo_titulo: str) -> dict:
    codigo_titulo_hash = hash_text(codigo_titulo)
    contract = get_contract()
    titulo = _titulo_to_dict(
        contract.functions.obtenerTitulo(Web3.to_bytes(hexstr=codigo_titulo_hash)).call()
    )
    titulo["codigo_titulo"] = codigo_titulo
    titulo["universidad_autorizada"] = False

    if titulo["existe"]:
        titulo["universidad_autorizada"] = bool(
            contract.functions.esUniversidadAutorizada(titulo["universidad"]).call()
        )

    return titulo


def verify_title(codigo_titulo: str, contenido_documento: str, identificacion_estudiante: str) -> dict:
    codigo_titulo_hash = hash_text(codigo_titulo)
    documento_hash = hash_text(contenido_documento)
    identificacion_hash = hash_text(identificacion_estudiante)
    contract = get_contract()

    existe, documento_coincide, identificacion_coincide, estado = contract.functions.verificarTitulo(
        Web3.to_bytes(hexstr=codigo_titulo_hash),
        Web3.to_bytes(hexstr=documento_hash),
        Web3.to_bytes(hexstr=identificacion_hash),
    ).call()

    titulo = get_title_by_code(codigo_titulo)
    ministerio_validador = titulo["ministerio_validador"]
    avalado_por_ministerio = ministerio_validador.lower() != ZERO_ADDRESS.lower()
    apto = bool(
        existe
        and documento_coincide
        and identificacion_coincide
        and int(estado) == 2
        and avalado_por_ministerio
        and titulo["universidad_autorizada"]
    )

    motivos = []
    if not existe:
        motivos.append("titulo no existe")
    if not documento_coincide:
        motivos.append("documento no coincide")
    if not identificacion_coincide:
        motivos.append("identificacion no coincide")
    if int(estado) != 2:
        motivos.append("titulo no avalado")
    if not avalado_por_ministerio:
        motivos.append("sin ministerio validador")
    if not titulo["universidad_autorizada"]:
        motivos.append("universidad emisora no autorizada")

    return {
        **titulo,
        "codigo_titulo_hash": codigo_titulo_hash,
        "documento_hash_presentado": documento_hash,
        "identificacion_estudiante_hash_presentado": identificacion_hash,
        "documento_coincide": bool(documento_coincide),
        "identificacion_coincide": bool(identificacion_coincide),
        "estado": int(estado),
        "estado_descripcion": estado_titulo_to_text(int(estado)),
        "avalado_por_ministerio": avalado_por_ministerio,
        "apto_para_admision": apto,
        "motivo_resultado": "apto para admision" if apto else "; ".join(motivos),
    }
