# -*- coding: utf-8 -*-
"""Service de abastecimentos: regras de negócio.

Delega ao repository (cabeçalho + itens na mesma transação).
ConflitoEdicaoError atravessa até o controller, que avisa e
recarrega a versão mais recente (padrão last-write-wins).
"""
from app.models.abastecimento import Abastecimento
from app.repositories.abastecimento_repository import (
    AbastecimentoRepository,
)
from app.utils.logger import get_logger

logger = get_logger("abastecimento_service")


class AbastecimentoService:
    def __init__(self):
        self._repo = AbastecimentoRepository()

    def salvar(self, dados: dict) -> Abastecimento:
        return self._repo.salvar(Abastecimento.from_dict(dados))

    def atualizar(self, dados: dict) -> bool:
        return self._repo.atualizar(Abastecimento.from_dict(dados))

    def excluir(self, sequencia: int) -> bool:
        return self._repo.excluir(sequencia)

    def buscar_por_sequencia(self, sequencia: int) -> Abastecimento | None:
        return self._repo.buscar_por_sequencia(sequencia)

    def pesquisar(self, filtro: str = "") -> list[Abastecimento]:
        return self._repo.pesquisar(filtro)
