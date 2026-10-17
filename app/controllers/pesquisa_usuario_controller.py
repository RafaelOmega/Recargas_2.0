# -*- coding: utf-8 -*-
"""Controller da pesquisa de usuários.

Filtro por código, nome, CPF ou login (debounce 300ms) + radio
buttons: Ativos (padrão) / Inativos — trocar o radio refaz a
pesquisa. Ordenação padrão: coluna Nome (ascendente). Enter na grade
confirma a seleção (como o duplo clique).

Modelo, debounce, conexões, tab order e erros comuns vêm de
PesquisaBase — aqui ficam apenas as colunas, a consulta e as linhas.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from app.controllers.pesquisa_base import PesquisaBase
from app.models.usuario import Usuario
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras
from app.views.ui_pesquisa_usuario import Ui_Pesquisa_Usuario

try:
    from app.services.usuario_service import UsuarioService
except ImportError:
    UsuarioService = None

logger = get_logger("pesquisa_usuario")


class PesquisaUsuarioController(PesquisaBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Pesquisa_Usuario()
        self.ui.setupUi(self)

        # compat: UI gerada antes da renomeação usa tb_Colaborador
        if not hasattr(self.ui, "tb_Usuario"):
            self.ui.tb_Usuario = self.ui.tb_Colaborador

        self._service = (UsuarioService()
                         if UsuarioService else None)

        self._grade = self.ui.tb_Usuario
        self._colunas = ["Código", "Nome", "Login"]
        self._coluna_padrao = 1  # Nome
        self._coluna_stretch = 1
        self._ordem_padrao = Qt.SortOrder.AscendingOrder

        self._inicializar()

    # ---------------- hooks do PesquisaBase ----------------

    def _nome_pesquisa(self) -> str:
        return "usuários"

    def _consultar(self) -> list[Usuario]:
        filtro = self.ui.txt_Pesquisa.text().strip()
        ativo = self.ui.rb_Ativo.isChecked()  # True=ativos, False=inativos
        return self._service.pesquisar(filtro, ativo=ativo)

    def _popular_lista(self, usuarios: list[Usuario]):
        self._modelo.removeRows(0, self._modelo.rowCount())
        for usuario in usuarios:
            codigo_valor = (int(usuario.codigo)
                            if usuario.codigo.isdigit()
                            else usuario.codigo)
            linha = [
                self._item_ordenavel(usuario.codigo, codigo_valor),
                self._item_ordenavel(usuario.nome, usuario.nome),
                self._item_ordenavel(usuario.login, usuario.login),
            ]
            self._modelo.appendRow(linha)
        ajustar_larguras(self._grade, coluna_stretch=self._coluna_stretch)

    # ---------------- seleção (API consumida pelos cadastros) ----------------

    def usuario_selecionado(self) -> Usuario | None:
        indice = self._grade.currentIndex()
        if not indice.isValid():
            return None
        item = self._modelo.item(indice.row(), 0)
        if item is None or self._service is None:
            return None
        try:
            return self._service.buscar_por_codigo(item.text())
        except Exception as exc:
            logger.exception("Falha ao carregar usuário selecionado")
            QMessageBox.critical(
                self, "Erro",
                f"Falha ao carregar o usuário:\n{mensagem_erro(exc)}")
            return None
