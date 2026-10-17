# -*- coding: utf-8 -*-
"""Controller da pesquisa de lançamentos de saldo da conta Biz.

Colunas: Código, Data, Valor. Ordenação padrão: Código DESCENDENTE
(numérica). Duplo clique, Enter na grade ou Confirmar devolvem o
registro selecionado (saldo_selecionado()).

Modelo, debounce, conexões, tab order e erros comuns vêm de
PesquisaBase — aqui ficam apenas as colunas, a consulta e as linhas.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from app.controllers.pesquisa_base import PesquisaBase
from app.models.saldo_conta import SaldoConta
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras
from app.views.ui_pesquisa_saldo_conta import Ui_Pesquisa_Saldo_Conta

try:
    from app.services.saldo_conta_service import SaldoContaService
except ImportError:
    SaldoContaService = None

logger = get_logger("pesquisa_saldo_conta")


class PesquisaSaldoContaController(PesquisaBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Pesquisa_Saldo_Conta()
        self.ui.setupUi(self)

        self._service = (SaldoContaService()
                         if SaldoContaService else None)

        self._grade = self.ui.tb_Saldo
        self._colunas = ["Código", "Data", "Valor"]
        self._coluna_padrao = 0  # Código
        self._coluna_stretch = 2
        self._ordem_padrao = Qt.SortOrder.DescendingOrder

        self._inicializar()

    # ---------------- hooks do PesquisaBase ----------------

    def _nome_pesquisa(self) -> str:
        return "lançamentos de saldo"

    def _consultar(self) -> list[SaldoConta]:
        filtro = self.ui.txt_Pesquisa.text().strip()
        return self._service.pesquisar(filtro)

    def _popular_lista(self, saldos: list[SaldoConta]):
        self._modelo.removeRows(0, self._modelo.rowCount())
        for saldo in saldos:
            codigo_valor = (int(saldo.codigo)
                            if saldo.codigo.isdigit()
                            else saldo.codigo)
            linha = [
                self._item_ordenavel(saldo.codigo, codigo_valor),
                self._item_ordenavel(
                    _para_data_texto(saldo.data),
                    saldo.data.isoformat() if saldo.data else ""),
                self._item_ordenavel(
                    _para_valor_texto(saldo.valor), saldo.valor),
            ]
            self._modelo.appendRow(linha)
        ajustar_larguras(self._grade, coluna_stretch=self._coluna_stretch)

    # ---------------- seleção (API consumida pelos cadastros) ----------------

    def saldo_selecionado(self) -> SaldoConta | None:
        indice = self._grade.currentIndex()
        if not indice.isValid():
            return None
        item = self._modelo.item(indice.row(), 0)
        if item is None or self._service is None:
            return None
        try:
            return self._service.buscar_por_codigo(item.text())
        except Exception as exc:
            logger.exception("Falha ao carregar saldo selecionado")
            QMessageBox.critical(
                self, "Erro",
                f"Falha ao carregar o lançamento:\n{mensagem_erro(exc)}")
            return None


# ---------------- auxiliares ----------------

def _para_data_texto(data) -> str:
    return data.strftime("%d/%m/%Y") if data else "—"


def _para_valor_texto(valor: float) -> str:
    """Float -> '1.234,56' (padrão brasileiro, sem prefixo)."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",")
    return texto.replace("X", ".")
