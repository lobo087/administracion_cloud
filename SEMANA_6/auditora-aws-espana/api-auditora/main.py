from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import blockchain
import models
from database import Base, engine, get_db, wait_for_database
from schemas import AuditoriaRespuesta, TituloBlockchain, VerificacionCrear


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Auditora - Verificacion Internacional de Titulos",
    description="API didactica de una universidad extranjera que verifica titulos avalados y guarda historial local.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok", "actor": "auditora"}


@app.get("/blockchain/contract")
def blockchain_contract():
    try:
        exists = blockchain.verify_contract_exists()
        return {
            "contract_address": blockchain.get_contract_address(),
            "existe_en_blockchain": exists,
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/titulos/{codigo_titulo}", response_model=TituloBlockchain)
def obtener_titulo(codigo_titulo: str):
    try:
        titulo = blockchain.get_title_by_code(codigo_titulo)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    if not titulo["existe"]:
        raise HTTPException(status_code=404, detail="Titulo no encontrado en blockchain")

    return titulo


@app.post("/verificar", response_model=AuditoriaRespuesta, status_code=status.HTTP_201_CREATED)
def verificar_titulo(payload: VerificacionCrear, db: Session = Depends(get_db)):
    try:
        resultado = blockchain.verify_title(
            payload.codigo_titulo,
            payload.contenido_documento,
            payload.identificacion_estudiante,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    auditoria = models.AuditoriaTitulo(
        codigo_titulo=payload.codigo_titulo,
        codigo_titulo_hash=resultado["codigo_titulo_hash"],
        documento_hash_presentado=resultado["documento_hash_presentado"],
        identificacion_estudiante_hash_presentado=resultado["identificacion_estudiante_hash_presentado"],
        documento_coincide=resultado["documento_coincide"],
        identificacion_coincide=resultado["identificacion_coincide"],
        estado_blockchain=resultado["estado_descripcion"],
        universidad_emisora=resultado["universidad_emisora"],
        universidad_address=resultado["universidad"],
        universidad_autorizada=resultado["universidad_autorizada"],
        ministerio_validador=resultado["ministerio_validador"],
        apto_para_admision=resultado["apto_para_admision"],
        motivo_resultado=resultado["motivo_resultado"],
        contract_address=blockchain.get_contract_address(),
    )
    db.add(auditoria)
    db.commit()
    db.refresh(auditoria)
    return auditoria


@app.get("/auditorias", response_model=list[AuditoriaRespuesta])
def listar_auditorias(db: Session = Depends(get_db)):
    return db.query(models.AuditoriaTitulo).order_by(models.AuditoriaTitulo.id).all()


@app.get("/auditorias/{auditoria_id}", response_model=AuditoriaRespuesta)
def obtener_auditoria(auditoria_id: int, db: Session = Depends(get_db)):
    auditoria = db.query(models.AuditoriaTitulo).filter(models.AuditoriaTitulo.id == auditoria_id).first()

    if auditoria is None:
        raise HTTPException(status_code=404, detail="Auditoria no encontrada")

    return auditoria
