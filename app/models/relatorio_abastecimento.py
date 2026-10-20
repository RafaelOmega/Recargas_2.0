# -*- coding: utf-8 -*-
"""Modelos de domínio do relatório de abastecimento por caminhão."""
from dataclasses import dataclass
from datetime import date


@dataclass
class ItemAbastecimentoRelatorio:
    sequencia: int = 0
    data: date | None = None
    caminhao_codigo: str = ""
    caminhao_modelo: str = ""
    placa: str = ""
    colaborador_nome: str = ""
    destino: str = ""
    km_inicio: int = 0
    km_final: int = 0
    litros: float = 0.0
