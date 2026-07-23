import os
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://admin:admin123@postgres:5432/titulos_db",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_database(max_attempts: int = 20, delay_seconds: int = 2):
    last_error = None

    for _ in range(max_attempts):
        try:
            with engine.connect():
                return
        except Exception as error:  # pragma: no cover - startup resilience
            last_error = error
            time.sleep(delay_seconds)

    raise RuntimeError(f"No se pudo conectar a PostgreSQL: {last_error}")
