# -*- coding: utf-8 -*-
"""Configuração da conexão com PostgreSQL.

Lê as credenciais das variáveis de ambiente do Windows:
DB_HOST, DB_NAME5, DB_PASSWORD, DB_PORT, DB_USER
"""
import os

import psycopg2

from app.utils.logger import get_logger

logger = get_logger("database")

# timeout de conexão (s): evita travar o app por minutos quando o
# servidor está inacessível (rede fora, PostgreSQL parado)
_TIMEOUT_CONEXAO_S = 5


def _config() -> dict:
    return {
        "host": os.getenv("DB_HOST", ""),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME5", ""),
        "user": os.getenv("DB_USER", ""),
        "password": os.getenv("DB_PASSWORD", ""),
        "connect_timeout": _TIMEOUT_CONEXAO_S,
    }


def get_connection():
    """Retorna uma conexão ativa com o PostgreSQL."""
    cfg = _config()
    if not cfg["host"] or not cfg["dbname"] or not cfg["user"]:
        raise RuntimeError(
            "Variáveis de ambiente do banco não configuradas "
            "(DB_HOST, DB_NAME5, DB_USER)."
        )

    logger.info("Conectando ao banco %s em %s", cfg["dbname"], cfg["host"])
    return psycopg2.connect(**cfg)
