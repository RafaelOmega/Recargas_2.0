# -*- coding: utf-8 -*-
"""Controller da pesquisa de colaboradores.

Filtro por código ou nome (debounce 300ms) + radio buttons:
Ativos (padrão) / Inativos — trocar o radio refaz a pesquisa.
Ordenação padrão: coluna Nome (ascendente). Enter na grade confirma
a seleção (como o duplo clique).

Modelo, debounce, conexões, tab order e erros comuns vêm de
PesquisaBase — aqui ficam apenas as colunas, a consulta e as linhas.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from app.controllers.pesquisa_base import PesquisaBase
from app.models.colaborador import Colaborador
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras
from app.views.ui_pesquisa_colaborador import Ui_Pesquisa_Colaborador

try:
    from app.services.colaborador_service import ColaboradorService
except ImportError:
    ColaboradorService = None

logger = get_logger("pesquisa_colaborador")


class PesquisaColaboradorController(PesquisaBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Pesquisa_Colaborador()
        self.ui.setupUi(self)

        self._service = (ColaboradorService()
                         if ColaboradorService else None)

        self._grade = self.ui.tb_Colaborador
        self._colunas = ["Código", "Nome", "CPF"]
        self._coluna_padrao = 1  # Nome
        self._coluna_stretch = 1
        self._ordem_padrao = Qt.SortOrder.AscendingOrder

        self._inicializar()

    # ---------------- hooks do PesquisaBase ----------------

    def _nome_pesquisa(self) -> str:
        return "colaboradores"

    def _consultar(self) -> list[Colaborador]:
        filtro = self.ui.txt_Pesquisa.text().strip()
        ativo = self.ui.rb_Ativo.isChecked()  # True=ativos, False=inativos
        return self._service.pesquisar(filtro, ativo=ativo)

    def _popular_lista(self, colaboradores: list[Colaborador]):
        self._modelo.removeRows(0, self._modelo.rowCount())
        for colaborador in colaboradores:
            codigo_valor = (int(colaborador.codigo)
                            if colaborador.codigo.isdigit()
                            else colaborador.codigo)
            linha = [
                self._item_ordenavel(colaborador.codigo, codigo_valor),
                self._item_ordenavel(colaborador.nome, colaborador.nome),
                self._item_ordenavel(colaborador.documento,
                                     colaborador.documento),
            ]
            self._modelo.appendRow(linha)
        ajustar_larguras(self._grade, coluna_stretch=self._coluna_stretch)

    # ---------------- seleção (API consumida pelos cadastros) ----------------

    def colaborador_selecionado(self) -> Colaborador | None:
        indice = self._grade.currentIndex()
        if not indice.isValid():
            return None
        item = self._modelo.item(indice.row(), 0)
        if item is None or self._service is None:
            return None
        try:
            return self._service.buscar_por_codigo(item.text())
        except Exception as exc:
            logger.exception("Falha ao carregar colaborador selecionado")
            QMessageBox.critical(
                self, "Erro",
                f"Falha ao carregar o colaborador:\n{mensagem_erro(exc)}")
            return None
