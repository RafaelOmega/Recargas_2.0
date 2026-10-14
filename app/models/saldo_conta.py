# -*- coding: utf-8 -*-
"""Modelo de domínio do saldo da conta Biz."""
from dataclasses import dataclass
from datetime import date


@dataclass
class SaldoConta:
    id: int | None = None
    codigo: str = ""      # automático (SEQUENCE), como colaboradores
    data: date | None = None
    valor: float = 0.0
