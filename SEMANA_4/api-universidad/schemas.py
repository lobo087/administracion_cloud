from datetime import date, datetime

from pydantic import BaseModel, Field


class TituloCrear(BaseModel):
    codigo_titulo: str = Field(examples=["UTPL-SIS-2026-0001"])
    nombre_estudiante: str = Field(examples=["Juan Perez"])
    identificacion_estudiante: str = Field(examples=["1100000001"])
    carrera: str = Field(examples=["Sistemas"])
    titulo_obtenido: str = Field(examples=["Ingeniero en Sistemas"])
    universidad: str = Field(default="UTPL", examples=["UTPL"])
    fecha_emision: date = Field(examples=["2026-06-15"])
    contenido_documento: str = Field(
        examples=["Titulo de Juan Perez como Ingeniero en Sistemas emitido por UTPL"]
    )


class TituloRespuesta(BaseModel):
    id: int
    codigo_titulo: str
    nombre_estudiante: str
    identificacion_estudiante: str
    carrera: str
    titulo_obtenido: str
    universidad: str
    fecha_emision: date
    codigo_titulo_hash: str
    documento_hash: str
    contract_address: str
    tx_hash: str | None
    creado_en: datetime

    model_config = {"from_attributes": True}


class VerificacionRespuesta(BaseModel):
    codigo_titulo: str
    codigo_titulo_hash: str
    documento_hash: str
    identificacion_estudiante_hash: str
    existe_en_blockchain: bool
    documento_coincide: bool
    identificacion_coincide: bool
    estado: int
    estado_descripcion: str
    contract_address: str
