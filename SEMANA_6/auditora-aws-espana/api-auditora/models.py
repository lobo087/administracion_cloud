from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class AuditoriaTitulo(Base):
    __tablename__ = "auditorias_titulos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo_titulo: Mapped[str] = mapped_column(String(100), index=True)
    codigo_titulo_hash: Mapped[str] = mapped_column(String(66), index=True)
    documento_hash_presentado: Mapped[str] = mapped_column(String(66), index=True)
    identificacion_estudiante_hash_presentado: Mapped[str] = mapped_column(String(66), index=True)
    documento_coincide: Mapped[bool] = mapped_column(Boolean)
    identificacion_coincide: Mapped[bool] = mapped_column(Boolean)
    estado_blockchain: Mapped[str] = mapped_column(String(50))
    universidad_emisora: Mapped[str] = mapped_column(String(200))
    universidad_address: Mapped[str] = mapped_column(String(42))
    universidad_autorizada: Mapped[bool] = mapped_column(Boolean)
    ministerio_validador: Mapped[str] = mapped_column(String(42))
    apto_para_admision: Mapped[bool] = mapped_column(Boolean)
    motivo_resultado: Mapped[str] = mapped_column(String(500))
    contract_address: Mapped[str] = mapped_column(String(42))
    auditado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
