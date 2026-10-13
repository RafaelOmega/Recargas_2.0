# -*- coding: utf-8 -*-
"""Controller da pesquisa de recargas.

Navegação (Tab) em modo Z: campo de pesquisa -> botão Confirmar
-> grade de resultados. Ordenação padrão: coluna Sequência
(DESCENDENTE — do maior para o menor, ordenação NUMÉRICA).

A coluna Data é exibida em formato brasileiro (dd/mm/aaaa) e a
coluna Descrição mostra os ITENS da recarga em uma única linha
(nomes separados por vírgula); sem itens, mostra a descrição salva.

Para a ordenação ser numérica/cronológica, o valor real fica no
EditRole do item (Sequência como int, Data como ISO YYYY-MM-DD) e o
texto exibido no DisplayRole. O sortRole do modelo é configurado
para EditRole — vale para a ordenação padrão E para o clique no
cabeçalho.
"""
from datetime import date, datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.recarga import Recarga
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_recargas import Ui_Pesquisa_Recargas

try:
    from app.services.recarga_service import RecargaService
except ImportError:
    RecargaService = None

logger = get_logger("pesquisa_recargas")
COLUNAS = ["Sequência", "Data", "Descrição"]
COLUNA_PADRAO = 0
COLUNA_STRETCH = 2
DEBOUNCE_MS = 300


class PesquisaRecargasController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Recargas()
        self.ui.setupUi(self)

        self._service = RecargaService() if RecargaService else None
        if self._service is None:
            logger.warning("RecargaService nao encontrado")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        self.ui.tb_Recargas.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Recargas,
                          coluna_stretch=COLUNA_STRETCH, ordenavel=True)
        # ordenação (padrão e clique no cabeçalho) usa o EditRole
        self._modelo.setSortRole(Qt.ItemDataRole.EditRole)
        # ordenação padrão: coluna Sequência, descendente (numérica)
        self.ui.tb_Recargas.sortByColumn(
            COLUNA_PADRAO, Qt.SortOrder.DescendingOrder)

        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)

        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._pesquisar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Recargas.doubleClicked.connect(self.accept)

        self._definir_tab_order()

        try:
            self._pesquisar()
        except Exception as exc:
            logger.exception("Falha ao carregar recargas na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar recargas:\n{exc}")

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z: pesquisa -> Confirmar -> grade."""
        self.setTabOrder(self.ui.txt_Pesquisa, self.ui.bt_Pesquisa)
        self.setTabOrder(self.ui.bt_Pesquisa, self.ui.tb_Recargas)

    def _agendar_filtro(self):
        self._timer_filtro.start(DEBOUNCE_MS)

    @staticmethod
    def _item_ordenavel(texto: str, valor_ordenacao) -> QStandardItem:
        """Item que exibe texto mas ordena pelo valor informado.

        O modelo usa sortRole = EditRole; o texto do DisplayRole
        permanece apenas para exibição.
        """
        item = QStandardItem(texto)
        item.setData(valor_ordenacao, Qt.ItemDataRole.EditRole)
        return item

    @staticmethod
    def _para_data(valor) -> date:
        """Aceita date, datetime ou texto (ISO ou brasileiro)."""
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        texto = str(valor).strip()[:10]
        try:
            return date.fromisoformat(texto)
        except ValueError:
            return datetime.strptime(texto, "%d/%m/%Y").date()

    @staticmethod
    def _descricao_itens(recarga: Recarga) -> str:
        """Itens da recarga em uma única linha (coluna Descrição)."""
        nomes = [item.nome for item in (recarga.itens or []) if item.nome]
        return ", ".join(nomes) if nomes else (recarga.descricao or "")

    def _pesquisar(self):
        self._timer_filtro.stop()
        try:
            filtro = self.ui.txt_Pesquisa.text().strip()
            registros = (self._service.pesquisar(filtro)
                         if self._service else [])
        except Exception as exc:
            logger.exception("Falha na consulta")
            QMessageBox.critical(self, "Erro", f"Falha na consulta:\n{exc}")
            return

        self._modelo.removeRows(0, self._modelo.rowCount())
        for recarga in registros:
            data = self._para_data(recarga.data)
            self._modelo.appendRow([
                # sequência como int no EditRole: ordenação numérica
                self._item_ordenavel(str(recarga.sequencia),
                                     recarga.sequencia),
                # exibição dd/mm/aaaa; ISO no EditRole: ordem cronológica
                self._item_ordenavel(
                    data.strftime("%d/%m/%Y"),
                    data.isoformat()),
                # itens em linha (nomes separados por vírgula)
                QStandardItem(self._descricao_itens(recarga)),
            ])
        # garante a ordenação padrão: Sequência, do maior para o menor
        self._modelo.sort(COLUNA_PADRAO, Qt.SortOrder.DescendingOrder)
        ajustar_larguras(self.ui.tb_Recargas, coluna_stretch=COLUNA_STRETCH)

    def recarga_selecionada(self) -> Recarga | None:
        indice = self.ui.tb_Recargas.currentIndex()
        if not indice.isValid():
            return None
        item = self._modelo.item(indice.row(), 0)
        if item is None or self._service is None:
            return None
        try:
            return self._service.buscar_por_sequencia(int(item.text()))
        except Exception as exc:
            logger.exception("Falha ao carregar recarga selecionada")
            QMessageBox.critical(
                self, "Erro", f"Falha ao carregar a recarga:\n{exc}")
            return None
