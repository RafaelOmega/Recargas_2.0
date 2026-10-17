# -*- coding: utf-8 -*-
"""Service de saldo da conta Biz: regras de negócio."""
from app.models.saldo_conta import SaldoConta
from app.repositories.saldo_conta_repository import SaldoContaRepository
from app.utils.logger import get_logger

logger = get_logger("saldo_conta_service")


class SaldoContaService:

    def __init__(self):
        self._repo = SaldoContaRepository()

    def salvar(self, dados: dict) -> SaldoConta:
        """Insere o lançamento (código gerado automaticamente)."""
        return self._repo.salvar(SaldoConta(
            data=dados["data"], valor=dados["valor"]))

    def atualizar(self, dados: dict) -> bool:
        return self._repo.atualizar(SaldoConta(
            codigo=dados["codigo"], data=dados["data"],
            valor=dados["valor"],
            atualizado_em=dados.get("atualizado_em")))

    def excluir(self, codigo: str) -> bool:
        return self._repo.excluir(codigo)

    def saldo_atual(self) -> float:
        """Saldo da conta Biz: soma das recargas - soma dos saldos."""
        return self._repo.saldo_atual()

    def buscar_por_codigo(self, codigo: str) -> SaldoConta | None:
        return self._repo.buscar_por_codigo(codigo)

    def pesquisar(self, filtro: str = "") -> list[SaldoConta]:
        return self._repo.pesquisar(filtro.strip())
