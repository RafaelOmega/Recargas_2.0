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

    @property
    def km_rodados(self) -> int:
        """Distância percorrida no trecho (nunca negativa)."""
        return max(self.km_final - self.km_inicio, 0)

    @property
    def km_por_litro(self) -> float | None:
        """Consumo do trecho em km/l.

        None quando não há litros informados (evita divisão por zero);
        o relatório exibe "—" nesse caso.
        """
        if self.litros <= 0:
            return None
        return self.km_rodados / self.litros
