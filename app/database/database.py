# -*- coding: utf-8 -*-
"""Configuração da conexão com PostgreSQL via SQLAlchemy.

Lê as credenciais das variáveis de ambiente do Windows:
DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
"""
import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.utils.logger import get_logger

logger = get_logger("database")

_engine = None
_SessionLocal = None


class Base(DeclarativeBase):
    """Base declarativa para todos os modelos ORM."""


def _url_banco() -> URL:
    host = os.getenv("DB_HOST", "")
    dbname = os.getenv("DB_NAME5", "")
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    port = os.getenv("DB_PORT", "5432")

    if not host or not dbname or not user:
        raise RuntimeError(
            "Variáveis de ambiente do banco não configuradas "
            "(DB_HOST, DB_NAME, DB_USER)."
        )

    return URL.create(
        "postgresql+psycopg2",
        username=user, password=password,
        host=host, port=int(port), database=dbname,
    )


def get_engine():
    """Cria a engine do SQLAlchemy uma única vez (lazy)."""
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(_url_banco(), pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
        logger.info("Engine criada para o banco %s", os.getenv("DB_NAME5"))
    return _engine


def get_session():
    """Abre uma nova sessão. Feche após o uso (ou use com `with`)."""
    if _SessionLocal is None:
        get_engine()
    return _SessionLocal()
