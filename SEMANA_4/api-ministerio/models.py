from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class AvalMinisterio(Base):
    __tablename__ = "avales_ministerio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo_titulo: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    codigo_titulo_hash: Mapped[str] = mapped_column(String(66), index=True)
    documento_hash: Mapped[str] = mapped_column(String(66), index=True)
    identificacion_estudiante_hash: Mapped[str] = mapped_column(String(66), index=True)
    universidad_emisora: Mapped[str] = mapped_column(String(200))
    carrera: Mapped[str] = mapped_column(String(200))
    titulo_obtenido: Mapped[str] = mapped_column(String(200))
    estado: Mapped[str] = mapped_column(String(50))
    contract_address: Mapped[str] = mapped_column(String(42))
    tx_hash: Mapped[str] = mapped_column(String(66))
    avalado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
