# -*- coding: utf-8 -*-
"""Criação do schema do banco (idempotente).

Executada na inicialização do sistema: cada CREATE TABLE usa
IF NOT EXISTS, então em banco já existente nada é alterado.
"""
from app.database import get_connection
from app.utils.logger import get_logger

logger = get_logger("schema")

_TABELAS = (
    """
    CREATE TABLE IF NOT EXISTS colaboradores (
        id        SERIAL PRIMARY KEY,
        codigo    VARCHAR(20) UNIQUE NOT NULL,
        nome      VARCHAR(120) NOT NULL,
        documento VARCHAR(20) DEFAULT ''
    )
    """,
)


def criar_schema() -> None:
    """Cria as tabelas que não existirem (idempotente)."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for ddl in _TABELAS:
                    cur.execute(ddl)
    finally:
        conn.close()
    logger.info("Schema verificado")
