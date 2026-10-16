# -*- coding: utf-8 -*-
"""Controller da pesquisa de lançamentos de saldo da conta Biz.

Colunas: Código, Data, Valor. Ordenação padrão: Código DESCENDENTE
(numérica). O valor de ordenação fica no Qt.UserRole (papel livre,
separado do texto) e o sortRole do modelo aponta para ele:
exibição no DisplayRole, ordenação (padrão e clique no cabeçalho)
pelo UserRole. Duplo clique, Enter na grade ou Confirmar devolvem
o registro selecionado (saldo_selecionado()).
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (QKeySequence, QShortcut, QStandardItem,
                           QStandardItemModel)
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.saldo_conta import SaldoConta
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_saldo_conta import Ui_Pesquisa_Saldo_Conta

try:
    from app.services.saldo_conta_service import SaldoContaService
except ImportError:
    SaldoContaService = None

logger = get_logger("pesquisa_saldo_conta")

COLUNAS = ["Código", "Data", "Valor"]
COLUNA_PADRAO = 0
COLUNA_STRETCH = 2
DEBOUNCE_MS = 300


class PesquisaSaldoContaController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Saldo_Conta()
        self.ui.setupUi(self)

        self._service = (SaldoContaService()
                         if SaldoContaService else None)
        if self._service is None:
            logger.warning("SaldoContaService nao encontrado")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        self.ui.tb_Saldo.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Saldo,
                          coluna_stretch=COLUNA_STRETCH, ordenavel=True)
        # ordenação (padrão e clique no cabeçalho) usa o UserRole —
        # EditRole no QStandardItem sobrescreve o texto exibido
        self._modelo.setSortRole(Qt.ItemDataRole.UserRole)
        # ordenação padrão: coluna Código, descendente (numérica)
        self.ui.tb_Saldo.sortByColumn(
            COLUNA_PADRAO, Qt.SortOrder.DescendingOrder)

        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)
        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._confirmar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Saldo.doubleClicked.connect(self.accept)
        # Enter na grade confirma como o duplo clique
        self._at_enter_grade = QShortcut(
            QKeySequence(Qt.Key.Key_Return), self.ui.tb_Saldo)
        self._at_enter_grade.activated.connect(self._confirmar)

        self._definir_tab_order()

        try:
            self._pesquisar()
        except Exception as exc:
            logger.exception("Falha ao carregar saldos na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar os lançamentos:\n{exc}")

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z: pesquisa -> Confirmar -> grade."""
        self.setTabOrder(self.ui.txt_Pesquisa, self.ui.bt_Pesquisa)
        self.setTabOrder(self.ui.bt_Pesquisa, self.ui.tb_Saldo)

    def _agendar_filtro(self):
        self._timer_filtro.start(DEBOUNCE_MS)

    @staticmethod
    def _item_ordenavel(texto: str, valor_ordenacao) -> QStandardItem:
        """Item que exibe texto mas ordena pelo valor informado."""
        item = QStandardItem(texto)
        item.setData(valor_ordenacao, Qt.ItemDataRole.UserRole)
        return item

    def _pesquisar(self):
        if self._service is None:
            return
        filtro = self.ui.txt_Pesquisa.text().strip()
        try:
            saldos = self._service.pesquisar(filtro)
        except Exception as exc:
            logger.exception("Falha ao pesquisar saldos")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível pesquisar:\n{exc}")
            return
        self._popular_lista(saldos)

    def _confirmar(self):
        """Confirmar: com seleção, devolve o registro;
        sem seleção, apenas pesquisa."""
        if self.ui.tb_Saldo.currentIndex().isValid():
            self.accept()
        else:
            self._pesquisar()

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
        ajustar_larguras(self.ui.tb_Saldo, coluna_stretch=COLUNA_STRETCH)

    def saldo_selecionado(self) -> SaldoConta | None:
        indice = self.ui.tb_Saldo.currentIndex()
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
                f"Falha ao carregar o lançamento:\n{exc}")
            return None


# ---------------- auxiliares ----------------

def _para_data_texto(data) -> str:
    return data.strftime("%d/%m/%Y") if data else "—"


def _para_valor_texto(valor: float) -> str:
    """Float -> '1.234,56' (padrão brasileiro, sem prefixo)."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",")
    return texto.replace("X", ".")
