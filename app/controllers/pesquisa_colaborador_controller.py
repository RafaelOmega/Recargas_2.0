# -*- coding: utf-8 -*-
"""Controller da tela de pesquisa de colaboradores.

QDialog modal: filtra por código/nome e devolve o código do registro
selecionado em `codigo_selecionado` quando aceito (duplo clique ou
botão Confirmar).
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog

from app.services.colaborador_service import ColaboradorService
from app.utils.logger import get_logger
from app.views.ui_pesquisa_colaborador import Ui_Pesquisa_Colaborador

logger = get_logger("pesquisa_colaborador")

_COLUNAS = ["Código", "Nome", "CPF"]


class PesquisaColaboradorController(QDialog):
    """Tela de pesquisa de colaboradores (modal)."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Colaborador()
        self.ui.setupUi(self)

        self._service = ColaboradorService()
        self.codigo_selecionado: str | None = None

        self._montar_tabela()
        self._conectar_botoes()
        self._definir_tab_order()
        self.pesquisar("")  # lista tudo ao abrir

        logger.info("Pesquisa de colaboradores iniciada")

    # ---------------- configuração ----------------

    def _montar_tabela(self):
        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(_COLUNAS)
        self.ui.tb_Colaborador.setModel(self._modelo)
        self.ui.tb_Colaborador.setSelectionBehavior(
            self.ui.tb_Colaborador.SelectionBehavior.SelectRows)
        self.ui.tb_Colaborador.setSelectionMode(
            self.ui.tb_Colaborador.SelectionMode.SingleSelection)
        self.ui.tb_Colaborador.setEditTriggers(
            self.ui.tb_Colaborador.EditTrigger.NoEditTriggers)
        self.ui.tb_Colaborador.horizontalHeader().setStretchLastSection(True)
        self.ui.tb_Colaborador.doubleClicked.connect(self._confirmar)

    def _conectar_botoes(self):
        self.ui.bt_Pesquisa.clicked.connect(self._ao_pesquisar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._ao_pesquisar)

    def _definir_tab_order(self):
        """Ordem de tabulação: campo de pesquisa -> Confirmar -> grade."""
        self.setTabOrder(self.ui.txt_Pesquisa, self.ui.bt_Pesquisa)
        self.setTabOrder(self.ui.bt_Pesquisa, self.ui.tb_Colaborador)

    # ---------------- eventos ----------------

    def _ao_pesquisar(self):
        self.pesquisar(self.ui.txt_Pesquisa.text())

    def _confirmar(self, indice):
        """Duplo clique na grade: seleciona e fecha com Accepted."""
        linha = indice.row()
        self.codigo_selecionado = self._modelo.item(linha, 0).text()
        self.accept()

    # ---------------- apoio ----------------

    def pesquisar(self, filtro: str = ""):
        """Consulta o service e preenche a grade."""
        try:
            registros = self._service.pesquisar(filtro)
        except Exception as exc:
            logger.exception("Falha ao pesquisar colaboradores")
            registros = []

        self._modelo.setRowCount(0)
        for r in registros:
            linha = [
                QStandardItem(r["codigo"]),
                QStandardItem(r["nome"]),
                QStandardItem(r["documento"] or ""),
            ]
            for item in linha:
                item.setEditable(False)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft
                    | Qt.AlignmentFlag.AlignVCenter)
            self._modelo.appendRow(linha)
