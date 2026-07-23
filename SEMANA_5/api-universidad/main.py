from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import blockchain
import models
from database import Base, engine, get_db, wait_for_database
from schemas import TituloCrear, TituloRespuesta, VerificacionRespuesta


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Universidad - Registro de Titulos",
    description="API didactica para registrar titulos en PostgreSQL y guardar evidencia en blockchain.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


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


@app.post("/titulos", response_model=TituloRespuesta, status_code=status.HTTP_201_CREATED)
def crear_titulo(payload: TituloCrear, db: Session = Depends(get_db)):
    codigo_titulo_hash = blockchain.hash_text(payload.codigo_titulo)
    documento_hash = blockchain.hash_text(payload.contenido_documento)
    identificacion_estudiante_hash = blockchain.hash_text(payload.identificacion_estudiante)

    titulo = models.Titulo(
        codigo_titulo=payload.codigo_titulo,
        nombre_estudiante=payload.nombre_estudiante,
        identificacion_estudiante=payload.identificacion_estudiante,
        carrera=payload.carrera,
        titulo_obtenido=payload.titulo_obtenido,
        universidad=payload.universidad,
        fecha_emision=payload.fecha_emision,
        contenido_documento=payload.contenido_documento,
        codigo_titulo_hash=codigo_titulo_hash,
        documento_hash=documento_hash,
        contract_address=blockchain.get_contract_address(),
    )

    db.add(titulo)

    try:
        tx_hash = blockchain.register_title(
            codigo_titulo_hash,
            documento_hash,
            identificacion_estudiante_hash,
            payload.universidad,
            payload.carrera,
            payload.titulo_obtenido,
        )
        titulo.tx_hash = tx_hash
        db.commit()
        db.refresh(titulo)
        return titulo
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un titulo con ese codigo",
        ) from error
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/titulos", response_model=list[TituloRespuesta])
def listar_titulos(db: Session = Depends(get_db)):
    return db.query(models.Titulo).order_by(models.Titulo.id).all()


@app.get("/titulos/{codigo_titulo}", response_model=TituloRespuesta)
def obtener_titulo(codigo_titulo: str, db: Session = Depends(get_db)):
    titulo = db.query(models.Titulo).filter(models.Titulo.codigo_titulo == codigo_titulo).first()

    if titulo is None:
        raise HTTPException(status_code=404, detail="Titulo no encontrado")

    return titulo


@app.get("/titulos/{codigo_titulo}/verificar", response_model=VerificacionRespuesta)
def verificar_titulo(codigo_titulo: str, db: Session = Depends(get_db)):
    titulo = db.query(models.Titulo).filter(models.Titulo.codigo_titulo == codigo_titulo).first()

    if titulo is None:
        raise HTTPException(status_code=404, detail="Titulo no encontrado")

    try:
        identificacion_estudiante_hash = blockchain.hash_text(titulo.identificacion_estudiante)
        existe, documento_coincide, identificacion_coincide, estado = blockchain.verify_title(
            titulo.codigo_titulo_hash,
            titulo.documento_hash,
            identificacion_estudiante_hash,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return VerificacionRespuesta(
        codigo_titulo=titulo.codigo_titulo,
        codigo_titulo_hash=titulo.codigo_titulo_hash,
        documento_hash=titulo.documento_hash,
        identificacion_estudiante_hash=identificacion_estudiante_hash,
        existe_en_blockchain=existe,
        documento_coincide=documento_coincide,
        identificacion_coincide=identificacion_coincide,
        estado=estado,
        estado_descripcion=blockchain.estado_titulo_to_text(estado),
        contract_address=titulo.contract_address,
    )
