# -*- coding: utf-8 -*-
"""Criação do schema do banco (idempotente).

Executada na inicialização do sistema: o create_all emite CREATE TABLE
apenas para tabelas que ainda não existem; em banco já existente nada
é alterado.
"""
from app.database.database import Base, get_engine
from app.utils.logger import get_logger

# Importa os modelos para que o Base.metadata conheça todas as tabelas
from app.models import (  # noqa: F401
    Funcionarios
)

logger = get_logger("schema")


def criar_schema() -> None:
    """Cria as tabelas que não existirem (idempotente)."""
    Base.metadata.create_all(get_engine())
    logger.info("Schema verificado")
