# -*- coding: utf-8 -*-
"""Service de recargas: regras de negócio."""
from app.models.recarga import Recarga
from app.repositories.recarga_repository import RecargaRepository
from app.utils.logger import get_logger

logger = get_logger("recarga_service")


class RecargaService:

    def __init__(self):
        self._repo = RecargaRepository()

    def salvar(self, dados: dict) -> Recarga:
        return self._repo.salvar(Recarga.from_dict(dados))

    def atualizar(self, dados: dict) -> bool:
        return self._repo.atualizar(Recarga.from_dict(dados))

    def excluir(self, sequencia: int) -> bool:
        return self._repo.excluir(sequencia)

    def buscar_por_sequencia(self, sequencia: int) -> Recarga | None:
        return self._repo.buscar_por_sequencia(sequencia)

    def pesquisar(self, filtro: str = "") -> list[Recarga]:
        return self._repo.pesquisar(filtro)
