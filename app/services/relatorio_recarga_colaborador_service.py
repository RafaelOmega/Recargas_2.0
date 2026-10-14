# -*- coding: utf-8 -*-
"""Service do relatório de recargas por colaborador."""
from app.models.relatorio_recarga_colaborador import ItemRecargaRelatorio
from app.repositories.relatorio_recarga_colaborador_repository import (
    RelatorioRecargaColaboradorRepository,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_recarga_colaborador_service")


class RelatorioRecargaColaboradorService:

    def __init__(self):
        self._repo = RelatorioRecargaColaboradorRepository()

    def itens_por_colaborador(self, nome: str = "",
                              documento: str = ""
                              ) -> list[ItemRecargaRelatorio]:
        """Dados prontos para o relatório (PDF/XLSX/CSV)."""
        return self._repo.itens_por_colaborador(nome.strip(),
                                                documento.strip())
