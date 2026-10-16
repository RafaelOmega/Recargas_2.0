# -*- coding: utf-8 -*-
"""Service de caminhões: regras de negócio."""
from app.models.caminhao import Caminhao
from app.repositories.caminhao_repository import CaminhaoRepository
from app.utils.logger import get_logger

logger = get_logger("caminhao_service")


class CaminhaoService:

    def __init__(self):
        self._repo = CaminhaoRepository()

    def salvar(self, dados: dict) -> Caminhao:
        return self._repo.salvar(Caminhao.from_dict(dados))

    def atualizar(self, dados: dict) -> bool:
        return self._repo.atualizar(Caminhao.from_dict(dados))

    def excluir(self, codigo: str) -> bool:
        return self._repo.excluir(codigo)

    def buscar_por_codigo(self, codigo: str) -> Caminhao | None:
        return self._repo.buscar_por_codigo(codigo)

    def pesquisar(self, filtro: str = "",
                  ativo: bool | None = None) -> list[Caminhao]:
        return self._repo.pesquisar(filtro, ativo=ativo)
