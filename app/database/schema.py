# -*- coding: utf-8 -*-
"""Criação do schema do banco (idempotente).

Executada na inicialização do sistema: cada comando usa
CREATE ... IF NOT EXISTS, portanto em banco já existente nada
é alterado; em banco novo, tudo é criado.

O código dos colaboradores vem de uma SEQUENCE do PostgreSQL
(seq_colaboradores_codigo), o que elimina a race condition do
MAX(codigo)+1 em uso multiusuário. A sequência é sincronizada
com o maior código numérico já gravado (idempotente).
"""
from app.database.database import get_connection
from app.utils.logger import get_logger

logger = get_logger("schema")

_COMANDOS = (
    """
    CREATE TABLE IF NOT EXISTS colaboradores (
        id        SERIAL PRIMARY KEY,
        codigo    VARCHAR(20) UNIQUE NOT NULL,
        nome      VARCHAR(120) NOT NULL,
        documento VARCHAR(20) DEFAULT ''
    )
    """,
    """
    CREATE SEQUENCE IF NOT EXISTS seq_colaboradores_codigo
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        NO CYCLE
    """,
    # sincroniza a sequência com o maior código numérico existente
    # (sem efeito em banco novo, onde a sequência já começa em 1)
    """
    DO $$
    DECLARE
        v_max INTEGER;
    BEGIN
        SELECT COALESCE(MAX(CAST(codigo AS INTEGER)), 0)
          INTO v_max
          FROM colaboradores
         WHERE codigo ~ '^[0-9]+$';
        IF v_max > 0 THEN
            PERFORM setval('seq_colaboradores_codigo', v_max, true);
        END IF;
    END $$
    """,
)


def criar_schema() -> None:
    """Cria tabelas/sequências que não existirem (idempotente)."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for comando in _COMANDOS:
                    cur.execute(comando)
    finally:
        conn.close()
    logger.info("Schema verificado (%s comandos)", len(_COMANDOS))
