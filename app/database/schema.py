# -*- coding: utf-8 -*-
"""Criação do schema do banco (idempotente).

Executada na inicialização do sistema: cada comando usa
CREATE ... IF NOT EXISTS, portanto em banco já existente nada
é alterado; em banco novo, tudo é criado.

Números automáticos vêm de SEQUENCEs do PostgreSQL:
  - seq_colaboradores_codigo     -> colaboradores.codigo
  - seq_recargas_sequencia       -> recargas.sequencia
  - seq_abastecimentos_sequencia -> abastecimentos.sequencia
  - seq_saldo_conta_codigo       -> saldo_conta.codigo
  - seq_usuarios_codigo          -> usuarios.codigo
  - seq_caminhoes_codigo         -> caminhoes.codigo
eliminando a race condition do MAX()+1 em uso multiusuário.
Cada sequência é sincronizada com o maior valor já gravado
(idempotente).
Last-write-wins: as 4 tabelas de cadastro, as recargas e os
abastecimentos ganham atualizado_em (versão do registro) e
pelo_usuario (último escritor) — migração idempotente; registros
antigos ficam com atualizado_em NULL, que casa com a carga None
(sem falso conflito na primeira edição).

Abastecimentos: caminhão e colaborador são SNAPSHOT POR ITEM
(cada item carrega seu próprio vínculo) — o cabeçalho fica só com
sequência e data. A migração adiciona as colunas de vínculo aos
itens e remove as que existiram brevemente no cabeçalho (módulo
sem dados de produção).
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
    # last-write-wins: versão do registro + último escritor
    """
    ALTER TABLE colaboradores
        ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP,
        ADD COLUMN IF NOT EXISTS pelo_usuario VARCHAR(60) DEFAULT ''
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
    # last-write-wins: versão do registro + último escritor (recargas)
    """
    ALTER TABLE recargas
        ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP,
        ADD COLUMN IF NOT EXISTS pelo_usuario VARCHAR(60) DEFAULT ''
    """,
    # ---------------- abastecimentos (cabeçalho) ----------------
    """
    CREATE TABLE IF NOT EXISTS abastecimentos (
        id        SERIAL PRIMARY KEY,
        sequencia INTEGER NOT NULL UNIQUE,
        data      DATE NOT NULL
    )
    """,
    """
    CREATE SEQUENCE IF NOT EXISTS seq_abastecimentos_sequencia
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
          FROM abastecimentos;
        IF v_max > 0 THEN
            PERFORM setval('seq_abastecimentos_sequencia', v_max, true);
        END IF;
    END $$
    """,
    # ---------------- abastecimentos_itens ----------------
    # caminhão e colaborador são snapshot POR ITEM
    """
    CREATE TABLE IF NOT EXISTS abastecimentos_itens (
        id               SERIAL PRIMARY KEY,
        abastecimento_id INTEGER NOT NULL
                         REFERENCES abastecimentos(id)
                         ON DELETE CASCADE,
        caminhao_codigo    VARCHAR(20) NOT NULL DEFAULT '',
        caminhao_modelo    VARCHAR(120) NOT NULL DEFAULT '',
        colaborador_codigo VARCHAR(20) NOT NULL DEFAULT '',
        colaborador_nome   VARCHAR(120) NOT NULL DEFAULT '',
        destino            VARCHAR(120) NOT NULL,
        km_inicio          INTEGER NOT NULL DEFAULT 0,
        km_final           INTEGER NOT NULL DEFAULT 0,
        litros             NUMERIC(12,2) NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_abastecimentos_itens_abastecimento
        ON abastecimentos_itens (abastecimento_id)
    """,
    # migração do desenho breve com vínculos no cabeçalho: os itens
    # ganham as colunas de vínculo (idempotente — sem efeito em banco
    # novo, onde já nasceram com elas)
    """
    ALTER TABLE abastecimentos_itens
        ADD COLUMN IF NOT EXISTS caminhao_codigo VARCHAR(20)
            NOT NULL DEFAULT '',
        ADD COLUMN IF NOT EXISTS caminhao_modelo VARCHAR(120)
            NOT NULL DEFAULT '',
        ADD COLUMN IF NOT EXISTS colaborador_codigo VARCHAR(20)
            NOT NULL DEFAULT '',
        ADD COLUMN IF NOT EXISTS colaborador_nome VARCHAR(120)
            NOT NULL DEFAULT ''
    """,
    # limpeza do mesmo desenho breve: colunas de vínculo saem do
    # cabeçalho (módulo sem dados de produção)
    """
    ALTER TABLE abastecimentos
        DROP COLUMN IF EXISTS caminhao_codigo,
        DROP COLUMN IF EXISTS caminhao_modelo,
        DROP COLUMN IF EXISTS colaborador_codigo,
        DROP COLUMN IF EXISTS colaborador_nome
    """,
    # last-write-wins: versão do registro + último escritor
    # (abastecimentos)
    """
    ALTER TABLE abastecimentos
        ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP,
        ADD COLUMN IF NOT EXISTS pelo_usuario VARCHAR(60) DEFAULT ''
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
    # last-write-wins: versão do registro + último escritor
    """
    ALTER TABLE saldo_conta
        ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP,
        ADD COLUMN IF NOT EXISTS pelo_usuario VARCHAR(60) DEFAULT ''
    """,
    # ---------------- usuarios (acesso ao sistema) ----------------
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id         SERIAL PRIMARY KEY,
        codigo     VARCHAR(20) UNIQUE NOT NULL,
        nome       VARCHAR(120) NOT NULL,
        documento  VARCHAR(20) DEFAULT '',
        login      VARCHAR(60) UNIQUE NOT NULL,
        senha_hash VARCHAR(256) NOT NULL,
        ativo      BOOLEAN NOT NULL DEFAULT TRUE
    )
    """,
    """
    CREATE SEQUENCE IF NOT EXISTS seq_usuarios_codigo
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
          FROM usuarios
         WHERE codigo ~ '^[0-9]+$';
        IF v_max > 0 THEN
            PERFORM setval('seq_usuarios_codigo', v_max, true);
        END IF;
    END $$
    """,
    # documento: migração idempotente de bases criadas antes
    """
    ALTER TABLE usuarios
        ADD COLUMN IF NOT EXISTS documento VARCHAR(20) DEFAULT ''
    """,
    # last-write-wins: versão do registro + último escritor
    """
    ALTER TABLE usuarios
        ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP,
        ADD COLUMN IF NOT EXISTS pelo_usuario VARCHAR(60) DEFAULT ''
    """,
    # ---------------- caminhoes (frota) ----------------
    """
    CREATE TABLE IF NOT EXISTS caminhoes (
        id     SERIAL PRIMARY KEY,
        codigo VARCHAR(20) UNIQUE NOT NULL,
        modelo VARCHAR(120) NOT NULL,
        placa  VARCHAR(20) NOT NULL DEFAULT '',
        ativo  BOOLEAN NOT NULL DEFAULT TRUE
    )
    """,
    """
    CREATE SEQUENCE IF NOT EXISTS seq_caminhoes_codigo
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
          FROM caminhoes
         WHERE codigo ~ '^[0-9]+$';
        IF v_max > 0 THEN
            PERFORM setval('seq_caminhoes_codigo', v_max, true);
        END IF;
    END $$
    """,
    # last-write-wins: versão do registro + último escritor
    """
    ALTER TABLE caminhoes
        ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP,
        ADD COLUMN IF NOT EXISTS pelo_usuario VARCHAR(60) DEFAULT ''
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
