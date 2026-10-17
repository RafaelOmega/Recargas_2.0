# -*- coding: utf-8 -*-
"""Controller da pesquisa de recargas.

Ordenação padrão: coluna Sequência (DESCENDENTE — do maior para o
menor, ordenação NUMÉRICA). A coluna Data é exibida em formato
brasileiro (dd/mm/aaaa) e a coluna Descrição mostra os ITENS da
recarga em uma única linha (nomes separados por vírgula); sem itens,
mostra a descrição salva. Enter na grade confirma a seleção (como o
duplo clique).

Modelo, debounce, conexões, tab order e erros comuns vêm de
PesquisaBase — aqui ficam apenas as colunas, a consulta e as linhas.
"""
from datetime import date, datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from app.controllers.pesquisa_base import PesquisaBase
from app.models.recarga import Recarga
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras
from app.views.ui_pesquisa_recargas import Ui_Pesquisa_Recargas

try:
    from app.services.recarga_service import RecargaService
except ImportError:
    RecargaService = None

logger = get_logger("pesquisa_recargas")


class PesquisaRecargasController(PesquisaBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Pesquisa_Recargas()
        self.ui.setupUi(self)

        self._service = RecargaService() if RecargaService else None

        self._grade = self.ui.tb_Recargas
        self._colunas = ["Sequência", "Data", "Descrição"]
        self._coluna_padrao = 0  # Sequência
        self._coluna_stretch = 2
        self._ordem_padrao = Qt.SortOrder.DescendingOrder

        self._inicializar()

    # ---------------- hooks do PesquisaBase ----------------

    def _nome_pesquisa(self) -> str:
        return "recargas"

    def _consultar(self) -> list[Recarga]:
        filtro = self.ui.txt_Pesquisa.text().strip()
        return self._service.pesquisar(filtro)

    def _popular_lista(self, registros: list[Recarga]):
        self._modelo.removeRows(0, self._modelo.rowCount())
        for recarga in registros:
            data = self._para_data(recarga.data)
            descricao = self._descricao_itens(recarga)
            self._modelo.appendRow([
                # sequência como int no UserRole: ordenação numérica
                self._item_ordenavel(str(recarga.sequencia),
                                     recarga.sequencia),
                # exibição dd/mm/aaaa; ISO no UserRole: ordem cronológica
                self._item_ordenavel(
                    data.strftime("%d/%m/%Y"),
                    data.isoformat()),
                # itens em linha; ordena pelo próprio texto
                self._item_ordenavel(descricao, descricao),
            ])
        # garante a ordenação padrão: Sequência, do maior para o menor
        self._modelo.sort(self._coluna_padrao, self._ordem_padrao)
        ajustar_larguras(self._grade, coluna_stretch=self._coluna_stretch)

    # ---------------- seleção (API consumida pelos cadastros) ----------------

    def recarga_selecionada(self) -> Recarga | None:
        indice = self._grade.currentIndex()
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
                self, "Erro",
                f"Falha ao carregar a recarga:\n{mensagem_erro(exc)}")
            return None

    # ---------------- auxiliares ----------------

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
