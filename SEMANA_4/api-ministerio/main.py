from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import blockchain
import models
from database import Base, engine, get_db, wait_for_database
from schemas import AvalRespuesta, TituloBlockchain, TituloBlockchainConCodigo


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Ministerio - Aval de Titulos",
    description="API didactica del Ministerio para consultar titulos en blockchain y avalarlos con base propia.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok", "actor": "ministerio"}


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


@app.get("/titulos", response_model=list[TituloBlockchain])
def listar_titulos_blockchain():
    try:
        return blockchain.list_titles()
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/titulos/{codigo_titulo}", response_model=TituloBlockchainConCodigo)
def obtener_titulo_blockchain(codigo_titulo: str):
    try:
        titulo = blockchain.get_title_by_code(codigo_titulo)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    if not titulo["existe"]:
        raise HTTPException(status_code=404, detail="Titulo no encontrado en blockchain")

    return titulo


@app.post("/titulos/{codigo_titulo}/avalar", response_model=AvalRespuesta, status_code=status.HTTP_201_CREATED)
def avalar_titulo(codigo_titulo: str, db: Session = Depends(get_db)):
    try:
        titulo = blockchain.get_title_by_code(codigo_titulo)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    if not titulo["existe"]:
        raise HTTPException(status_code=404, detail="Titulo no encontrado en blockchain")

    try:
        tx_hash = blockchain.endorse_title(titulo["codigo_titulo_hash"])
        titulo_actualizado = blockchain.get_title_by_code(codigo_titulo)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    aval = models.AvalMinisterio(
        codigo_titulo=codigo_titulo,
        codigo_titulo_hash=titulo_actualizado["codigo_titulo_hash"],
        documento_hash=titulo_actualizado["documento_hash"],
        identificacion_estudiante_hash=titulo_actualizado["identificacion_estudiante_hash"],
        universidad_emisora=titulo_actualizado["universidad_emisora"],
        carrera=titulo_actualizado["carrera"],
        titulo_obtenido=titulo_actualizado["titulo_obtenido"],
        estado=titulo_actualizado["estado_descripcion"],
        contract_address=blockchain.get_contract_address(),
        tx_hash=tx_hash,
    )

    db.add(aval)

    try:
        db.commit()
        db.refresh(aval)
        return aval
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El Ministerio ya registro un aval para ese codigo de titulo",
        ) from error


@app.get("/avales", response_model=list[AvalRespuesta])
def listar_avales(db: Session = Depends(get_db)):
    return db.query(models.AvalMinisterio).order_by(models.AvalMinisterio.id).all()
