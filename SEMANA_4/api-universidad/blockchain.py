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
    private_key = os.getenv("GANACHE_PRIVATE_KEY")

    if not private_key:
        raise RuntimeError("Falta configurar GANACHE_PRIVATE_KEY")

    return private_key


def get_contract():
    with ABI_PATH.open("r", encoding="utf-8") as abi_file:
        abi = json.load(abi_file)

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


def register_title(
    codigo_titulo_hash: str,
    documento_hash: str,
    identificacion_estudiante_hash: str,
    universidad: str,
    carrera: str,
    titulo_obtenido: str,
) -> str:
    web3 = get_web3()
    contract = get_contract()
    private_key = get_private_key()
    account = web3.eth.account.from_key(private_key)

    tx = contract.functions.registrarTitulo(
        Web3.to_bytes(hexstr=codigo_titulo_hash),
        Web3.to_bytes(hexstr=documento_hash),
        Web3.to_bytes(hexstr=identificacion_estudiante_hash),
        universidad,
        carrera,
        titulo_obtenido,
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


def verify_title(
    codigo_titulo_hash: str,
    documento_hash: str,
    identificacion_estudiante_hash: str,
) -> tuple[bool, bool, bool, int]:
    contract = get_contract()
    existe, documento_coincide, identificacion_coincide, estado = contract.functions.verificarTitulo(
        Web3.to_bytes(hexstr=codigo_titulo_hash),
        Web3.to_bytes(hexstr=documento_hash),
        Web3.to_bytes(hexstr=identificacion_estudiante_hash),
    ).call()
    return bool(existe), bool(documento_coincide), bool(identificacion_coincide), int(estado)
