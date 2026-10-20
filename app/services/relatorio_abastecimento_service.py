# -*- coding: utf-8 -*-
"""Serviço do relatório de abastecimento por caminhão."""
from app.repositories.relatorio_abastecimento_repository import (
    RelatorioAbastecimentoRepository,
)


class RelatorioAbastecimentoService:

    def __init__(self, repo=None):
        self._repo = repo or RelatorioAbastecimentoRepository()

    def itens_por_caminhao(self, caminhao="", data_inicial=None,
                           data_final=None):
        return self._repo.itens_por_caminhao(
            caminhao, data_inicial, data_final)
