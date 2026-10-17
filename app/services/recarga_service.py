# -*- coding: utf-8 -*-
"""Service de recargas: regras de negócio."""
from app.models.recarga import Recarga
from app.repositories.recarga_repository import RecargaRepository
from app.utils.exportacao_csv import exportar_recarga_csv
from app.utils.logger import get_logger

logger = get_logger("recarga_service")


class RecargaService:
    def __init__(self):
        self._repo = RecargaRepository()

    def salvar(self, dados: dict) -> Recarga:
        recarga = self._repo.salvar(Recarga.from_dict(dados))
        self._exportar_csv(recarga)
        return recarga

    def atualizar(self, dados: dict) -> bool:
        recarga = Recarga.from_dict(dados)
        atualizado = self._repo.atualizar(recarga)
        if atualizado:
            self._exportar_csv(recarga)
        return atualizado

    def excluir(self, sequencia: int) -> bool:
        return self._repo.excluir(sequencia)

    def buscar_por_sequencia(self, sequencia: int) -> Recarga | None:
        return self._repo.buscar_por_sequencia(sequencia)

    def pesquisar(self, filtro: str = "") -> list[Recarga]:
        return self._repo.pesquisar(filtro)

    def _exportar_csv(self, recarga: Recarga) -> None:
        """Regra 001: CSV na área de trabalho a cada salvamento.

        Falha de exportação nunca cancela o salvamento — fica no log.
        """
        try:
            exportar_recarga_csv(recarga)
        except Exception:
            logger.exception(
                "Falha ao exportar CSV da recarga seq %s",
                recarga.sequencia)
