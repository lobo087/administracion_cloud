import os
import time

import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class MateriaIn(BaseModel):
    nombre: str = Field(min_length=1)
    horas: int = Field(gt=0)
    profesor: str = Field(min_length=1)
    carrera: str = Field(min_length=1)


app = FastAPI(title="Materias API persistente")


def get_connection():
    config = {
        "host": os.getenv("DB_HOST", "mysql"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "universidad"),
    }

    for intento in range(20):
        try:
            return mysql.connector.connect(**config)
        except mysql.connector.Error:
            if intento == 19:
                raise
            time.sleep(2)


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS materias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(160) NOT NULL,
                horas INT NOT NULL,
                profesor VARCHAR(120) NOT NULL,
                carrera VARCHAR(160) NOT NULL
            )
            """
        )
        conn.commit()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def inicio():
    return {"mensaje": "API persistente de materias con FastAPI y MySQL"}


@app.get("/materias")
def listar_materias():
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, horas, profesor, carrera FROM materias ORDER BY id")
        return cursor.fetchall()


@app.get("/materias/{materia_id}")
def obtener_materia(materia_id: int):
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, horas, profesor, carrera FROM materias WHERE id = %s",
            (materia_id,),
        )
        materia = cursor.fetchone()
        if materia is None:
            raise HTTPException(status_code=404, detail="Materia no encontrada")
        return materia


@app.post("/materias", status_code=201)
def crear_materia(materia: MateriaIn):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO materias (nombre, horas, profesor, carrera) VALUES (%s, %s, %s, %s)",
            (materia.nombre, materia.horas, materia.profesor, materia.carrera),
        )
        conn.commit()
        return {"id": cursor.lastrowid, **materia.model_dump()}
