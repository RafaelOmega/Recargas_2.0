# -*- coding: utf-8 -*-
"""Service de colaboradores: regras de negócio."""
from app.models.colaborador import Colaborador
from app.repositories.colaborador_repository import ColaboradorRepository
from app.utils.logger import get_logger

logger = get_logger("colaborador_service")


class ColaboradorService:

    def __init__(self):
        self._repo = ColaboradorRepository()

    def salvar(self, dados: dict) -> Colaborador:
        return self._repo.salvar(Colaborador.from_dict(dados))

    def atualizar(self, dados: dict) -> bool:
        return self._repo.atualizar(Colaborador.from_dict(dados))

    def excluir(self, codigo: str) -> bool:
        return self._repo.excluir(codigo)

    def buscar_por_codigo(self, codigo: str) -> Colaborador | None:
        return self._repo.buscar_por_codigo(codigo)

    def pesquisar(self, filtro: str = "") -> list[Colaborador]:
        return self._repo.pesquisar(filtro)
