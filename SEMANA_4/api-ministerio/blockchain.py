import json
import os
from pathlib import Path

from web3 import Web3


ABI_PATH = Path(__file__).parent / "contracts" / "RegistroTitulos.json"


def get_web3() -> Web3:
    rpc_url = os.getenv("GANACHE_RPC_URL", "http://blockchain-node:8545")
    return Web3(Web3.HTTPProvider(rpc_url))


def get_contract_address() -> str:
    contract_address = os.getenv("CONTRACT_ADDRESS")

    if not contract_address:
        raise RuntimeError("Falta configurar CONTRACT_ADDRESS")

    return Web3.to_checksum_address(contract_address)


def get_private_key() -> str:
    private_key = os.getenv("MINISTERIO_PRIVATE_KEY") or os.getenv("GANACHE_PRIVATE_KEY")

    if not private_key:
        raise RuntimeError("Falta configurar MINISTERIO_PRIVATE_KEY")

    return private_key


def get_contract():
    with ABI_PATH.open("r", encoding="utf-8") as abi_file:
        abi = json.load(abi_file)

    web3 = get_web3()
    return web3.eth.contract(address=get_contract_address(), abi=abi)


def hash_text(value: str) -> str:
    return Web3.to_hex(Web3.keccak(text=value))


def estado_titulo_to_text(estado: int) -> str:
    estados = {
        0: "NO_EXISTE",
        1: "REGISTRADO",
        2: "AVALADO",
        3: "RECHAZADO",
        4: "REVOCADO",
    }
    return estados.get(estado, "DESCONOCIDO")


def verify_contract_exists() -> bool:
    web3 = get_web3()
    code = web3.eth.get_code(get_contract_address())
    return code not in (b"", "0x")


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


def list_titles() -> list[dict]:
    contract = get_contract()
    codigos = contract.functions.listarCodigosTitulos().call()
    return [_titulo_to_dict(contract.functions.obtenerTitulo(codigo).call()) for codigo in codigos]


def get_title_by_code(codigo_titulo: str) -> dict:
    codigo_titulo_hash = hash_text(codigo_titulo)
    contract = get_contract()
    titulo = _titulo_to_dict(
        contract.functions.obtenerTitulo(Web3.to_bytes(hexstr=codigo_titulo_hash)).call()
    )
    titulo["codigo_titulo"] = codigo_titulo
    return titulo


def endorse_title(codigo_titulo_hash: str) -> str:
    web3 = get_web3()
    contract = get_contract()
    private_key = get_private_key()
    account = web3.eth.account.from_key(private_key)

    tx = contract.functions.avalarTitulo(
        Web3.to_bytes(hexstr=codigo_titulo_hash),
    ).build_transaction(
        {
            "from": account.address,
            "nonce": web3.eth.get_transaction_count(account.address),
            "chainId": web3.eth.chain_id,
            "gasPrice": web3.eth.gas_price,
        }
    )

    tx["gas"] = web3.eth.estimate_gas(tx)
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        raise RuntimeError("La transaccion fue rechazada por la blockchain")

    return Web3.to_hex(tx_hash)
