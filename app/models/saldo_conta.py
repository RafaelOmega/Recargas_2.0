# -*- coding: utf-8 -*-
"""Modelo de domínio do saldo da conta Biz."""
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class SaldoConta:
    id: int | None = None
    codigo: str = ""      # automático (SEQUENCE), como colaboradores
    data: date | None = None
    valor: float = 0.0
    # last-write-wins: versão do registro (None = nunca atualizado)
    atualizado_em: datetime | None = None
    pelo_usuario: str = ""
