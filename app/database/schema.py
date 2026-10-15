# -*- coding: utf-8 -*-
"""Criação do schema do banco (idempotente).

Executada na inicialização do sistema: cada comando usa
CREATE ... IF NOT EXISTS, portanto em banco já existente nada
é alterado; em banco novo, tudo é criado.

Números automáticos vêm de SEQUENCEs do PostgreSQL:
  - seq_colaboradores_codigo -> colaboradores.codigo
  - seq_recargas_sequencia   -> recargas.sequencia
  - seq_saldo_conta_codigo   -> saldo_conta.codigo
eliminando a race condition do MAX()+1 em uso multiusuário.
Cada sequência é sincronizada com o maior valor já gravado
(idempotente).
"""
from app.database.database import get_connection
from app.utils.logger import get_logger

logger = get_logger("schema")

_COMANDOS = (
    # ---------------- colaboradores ----------------
    """
    CREATE TABLE IF NOT EXISTS colaboradores (
        id        SERIAL PRIMARY KEY,
        codigo    VARCHAR(20) UNIQUE NOT NULL,
        nome      VARCHAR(120) NOT NULL,
        documento VARCHAR(20) DEFAULT '',
        ativo     BOOLEAN NOT NULL DEFAULT TRUE
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
    # coluna ativo: migração idempotente de bases já existentes
    # (colaboradores antigos tornam-se ativos pelo DEFAULT)
    """
    ALTER TABLE colaboradores
        ADD COLUMN IF NOT EXISTS ativo BOOLEAN NOT NULL DEFAULT TRUE
    """,
    # ---------------- recargas (cabeçalho) ----------------
    """
    CREATE TABLE IF NOT EXISTS recargas (
        id        SERIAL PRIMARY KEY,
        sequencia INTEGER NOT NULL UNIQUE,
        data      DATE NOT NULL,
        descricao VARCHAR(120) NOT NULL DEFAULT ''
    )
    """,
    """
    CREATE SEQUENCE IF NOT EXISTS seq_recargas_sequencia
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        NO CYCLE
    """,
    """
    DO $$
    DECLARE
        v_max INTEGER;
    BEGIN
        SELECT COALESCE(MAX(sequencia), 0)
          INTO v_max
          FROM recargas;
        IF v_max > 0 THEN
            PERFORM setval('seq_recargas_sequencia', v_max, true);
        END IF;
    END $$
    """,
    # ---------------- recargas_itens ----------------
    """
    CREATE TABLE IF NOT EXISTS recargas_itens (
        id         SERIAL PRIMARY KEY,
        recarga_id INTEGER NOT NULL
                   REFERENCES recargas(id) ON DELETE CASCADE,
        nome       VARCHAR(120) NOT NULL,
        documento  VARCHAR(20) NOT NULL DEFAULT '',
        valor      NUMERIC(12,4) NOT NULL DEFAULT 0,
        beneficio  VARCHAR(120) NOT NULL DEFAULT 'Refeição',
        carga      VARCHAR(120) NOT NULL DEFAULT '',
        sem_carga  VARCHAR(120) NOT NULL DEFAULT ''
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_recargas_itens_recarga
        ON recargas_itens (recarga_id)
    """,
    # ---------------- saldo_conta (conta Biz) ----------------
    """
    CREATE TABLE IF NOT EXISTS saldo_conta (
        id     SERIAL PRIMARY KEY,
        codigo VARCHAR(20) UNIQUE NOT NULL,
        data   DATE NOT NULL,
        valor  NUMERIC(12,2) NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE SEQUENCE IF NOT EXISTS seq_saldo_conta_codigo
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        NO CYCLE
    """,
    """
    DO $$
    DECLARE
        v_max INTEGER;
    BEGIN
        SELECT COALESCE(MAX(CAST(codigo AS INTEGER)), 0)
          INTO v_max
          FROM saldo_conta
         WHERE codigo ~ '^[0-9]+$';
        IF v_max > 0 THEN
            PERFORM setval('seq_saldo_conta_codigo', v_max, true);
        END IF;
    END $$
    """,
)


def criar_schema() -> None:
    """Cria tabelas/sequências/índices que não existirem (idempotente)."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for comando in _COMANDOS:
                    cur.execute(comando)
    finally:
        conn.close()
    logger.info("Schema verificado (%s comandos)", len(_COMANDOS))
