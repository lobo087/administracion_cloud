from datetime import datetime

from pydantic import BaseModel


class TituloBlockchain(BaseModel):
    codigo_titulo_hash: str
    documento_hash: str
    identificacion_estudiante_hash: str
    universidad_emisora: str
    carrera: str
    titulo_obtenido: str
    universidad: str
    ministerio_validador: str
    estado: int
    estado_descripcion: str
    fecha_registro: int
    fecha_aval: int
    existe: bool


class TituloBlockchainConCodigo(TituloBlockchain):
    codigo_titulo: str


class AvalRespuesta(BaseModel):
    id: int
    codigo_titulo: str
    codigo_titulo_hash: str
    documento_hash: str
    identificacion_estudiante_hash: str
    universidad_emisora: str
    carrera: str
    titulo_obtenido: str
    estado: str
    contract_address: str
    tx_hash: str
    avalado_en: datetime

    model_config = {"from_attributes": True}
