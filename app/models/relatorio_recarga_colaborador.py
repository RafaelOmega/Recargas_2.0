# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de recargas por colaborador."""
from dataclasses import dataclass
from datetime import date


@dataclass
class ItemRecargaRelatorio:
    sequencia: int = 0
    data: date | None = None
    nome: str = ""
    documento: str = ""
    carga: str = ""
    sem_carga: str = ""
    valor: float = 0.0
    beneficio: str = ""
