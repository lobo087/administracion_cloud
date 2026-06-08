import os
import time
from decimal import Decimal

import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class EstudianteIn(BaseModel):
    nombre: str = Field(min_length=1)
    carrera: str = Field(min_length=1)
    nota_promedio: Decimal = Field(ge=0, le=10)


app = FastAPI(title="Estudiantes API efimera")


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
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(120) NOT NULL,
                carrera VARCHAR(160) NOT NULL,
                nota_promedio DECIMAL(4,2) NOT NULL
            )
            """
        )
        conn.commit()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def inicio():
    return {"mensaje": "API efimera de estudiantes con FastAPI y MySQL"}


@app.get("/estudiantes")
def listar_estudiantes():
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, carrera, nota_promedio FROM estudiantes ORDER BY id")
        return cursor.fetchall()


@app.get("/estudiantes/{estudiante_id}")
def obtener_estudiante(estudiante_id: int):
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, carrera, nota_promedio FROM estudiantes WHERE id = %s",
            (estudiante_id,),
        )
        estudiante = cursor.fetchone()
        if estudiante is None:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return estudiante


@app.post("/estudiantes", status_code=201)
def crear_estudiante(estudiante: EstudianteIn):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO estudiantes (nombre, carrera, nota_promedio) VALUES (%s, %s, %s)",
            (estudiante.nombre, estudiante.carrera, estudiante.nota_promedio),
        )
        conn.commit()
        return {"id": cursor.lastrowid, **estudiante.model_dump()}
