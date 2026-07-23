from datetime import datetime

from pydantic import BaseModel, Field


class VerificacionCrear(BaseModel):
    codigo_titulo: str = Field(examples=["UTPL-SIS-2026-0002"])
    identificacion_estudiante: str = Field(examples=["1100000002"])
    contenido_documento: str = Field(
        examples=["Titulo de Maria Loja como Ingeniera en Sistemas emitido por UTPL"]
    )


class TituloBlockchain(BaseModel):
    codigo_titulo: str
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
    universidad_autorizada: bool


class AuditoriaRespuesta(BaseModel):
    id: int
    codigo_titulo: str
    codigo_titulo_hash: str
    documento_hash_presentado: str
    identificacion_estudiante_hash_presentado: str
    documento_coincide: bool
    identificacion_coincide: bool
    estado_blockchain: str
    universidad_emisora: str
    universidad_address: str
    universidad_autorizada: bool
    ministerio_validador: str
    apto_para_admision: bool
    motivo_resultado: str
    contract_address: str
    auditado_en: datetime

    model_config = {"from_attributes": True}
