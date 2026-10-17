# -*- coding: utf-8 -*-
"""Controller da pesquisa de caminhões.

Filtro por código, modelo ou placa (debounce 300ms) + radio buttons:
Ativos (padrão) / Inativos — trocar o radio refaz a pesquisa.
Ordenação padrão: coluna Código (descendente, numérica — valor real
guardado no Qt.UserRole). Enter na grade confirma a seleção (como o
duplo clique).

Modelo, debounce, conexões, tab order e erros comuns vêm de
PesquisaBase — aqui ficam apenas as colunas, a consulta e as linhas.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMessageBox

from app.controllers.pesquisa_base import PesquisaBase
from app.models.caminhao import Caminhao
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras
from app.views.ui_pesquisa_caminhoes import Ui_Pesquisa_Caminhoes

try:
    from app.services.caminhao_service import CaminhaoService
except ImportError:
    CaminhaoService = None

logger = get_logger("pesquisa_caminhoes")


class PesquisaCaminhoesController(PesquisaBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Pesquisa_Caminhoes()
        self.ui.setupUi(self)

        self._service = (CaminhaoService()
                         if CaminhaoService else None)

        self._grade = self.ui.tb_Caminhoes
        self._colunas = ["Código", "Modelo", "Placa"]
        self._coluna_padrao = 0  # Código
        self._coluna_stretch = 1  # Modelo
        self._ordem_padrao = Qt.SortOrder.DescendingOrder

        self._inicializar()

    # ---------------- hooks do PesquisaBase ----------------

    def _nome_pesquisa(self) -> str:
        return "caminhões"

    def _consultar(self) -> list[Caminhao]:
        ativo = self.ui.rb_Ativo.isChecked()
        filtro = self.ui.txt_Pesquisa.text().strip()
        return self._service.pesquisar(filtro, ativo=ativo)

    def _popular_lista(self, caminhoes: list[Caminhao]):
        self._modelo.removeRows(0, self._modelo.rowCount())
        for caminhao in caminhoes:
            codigo_valor = (int(caminhao.codigo)
                            if caminhao.codigo.isdigit()
                            else caminhao.codigo)
            linha = [
                self._item_ordenavel(caminhao.codigo, codigo_valor),
                self._item_ordenavel(caminhao.modelo, caminhao.modelo),
                self._item_ordenavel(caminhao.placa, caminhao.placa),
            ]
            self._modelo.appendRow(linha)
        ajustar_larguras(self._grade, coluna_stretch=self._coluna_stretch)

    def _item_ordenavel(self, texto: str, valor) -> QStandardItem:
        # itens da grade não são editáveis (padrão próprio desta tela)
        item = QStandardItem(texto)
        item.setEditable(False)
        item.setData(valor, Qt.ItemDataRole.UserRole)
        return item

    # ---------------- seleção (API consumida pelos cadastros) ----------------

    def caminhao_selecionado(self) -> Caminhao | None:
        indice = self._grade.currentIndex()
        if not indice.isValid() or self._service is None:
            return None
        codigo = indice.siblingAtColumn(0).data(
            Qt.ItemDataRole.DisplayRole)
        if not codigo:
            return None
        try:
            return self._service.buscar_por_codigo(str(codigo))
        except Exception:
            logger.exception("Falha ao carregar caminhão %s", codigo)
            return None
