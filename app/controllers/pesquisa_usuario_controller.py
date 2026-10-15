# -*- coding: utf-8 -*-
"""Controller da pesquisa de usuários.

Filtro por código, nome, CPF ou login (debounce 300ms) + radio
buttons: Ativos (padrão) / Inativos — trocar o radio refaz a
pesquisa. Navegação (Tab) em modo Z: pesquisa -> Ativos -> Inativos
-> Confirmar -> grade. Ordenação padrão: coluna Nome (ascendente).
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.usuario import Usuario
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_usuario import Ui_Pesquisa_Usuario

try:
    from app.services.usuario_service import UsuarioService
except ImportError:
    UsuarioService = None

logger = get_logger("pesquisa_usuario")

COLUNAS = ["Código", "Nome", "Login"]
COLUNA_PADRAO = 1  # Nome
COLUNA_STRETCH = 1
DEBOUNCE_MS = 300


class PesquisaUsuarioController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Usuario()
        self.ui.setupUi(self)

        # compat: UI gerada antes da renomeação usa tb_Colaborador
        if not hasattr(self.ui, "tb_Usuario"):
            self.ui.tb_Usuario = self.ui.tb_Colaborador

        self._service = (UsuarioService()
                         if UsuarioService else None)
        if self._service is None:
            logger.warning("UsuarioService nao encontrado")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        self.ui.tb_Usuario.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Usuario,
                          coluna_stretch=COLUNA_STRETCH, ordenavel=True)
        # ordenação (padrão e clique no cabeçalho) usa o UserRole —
        # EditRole no QStandardItem sobrescreve o texto exibido
        self._modelo.setSortRole(Qt.ItemDataRole.UserRole)
        # ordenação padrão: coluna Nome, ascendente
        self.ui.tb_Usuario.sortByColumn(
            COLUNA_PADRAO, Qt.SortOrder.AscendingOrder)

        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)
        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        # trocar o radio refaz a pesquisa (debounce)
        self.ui.rb_Ativo.toggled.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._confirmar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Usuario.doubleClicked.connect(self.accept)

        self._definir_tab_order()

        try:
            self._pesquisar()
        except Exception as exc:
            logger.exception("Falha ao carregar usuários na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar usuários:\n{exc}")

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z: pesquisa -> Ativos -> Inativos
        -> Confirmar -> grade."""
        self.setTabOrder(self.ui.txt_Pesquisa, self.ui.rb_Ativo)
        self.setTabOrder(self.ui.rb_Ativo, self.ui.rb_Inativo)
        self.setTabOrder(self.ui.rb_Inativo, self.ui.bt_Pesquisa)
        self.setTabOrder(self.ui.bt_Pesquisa, self.ui.tb_Usuario)

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
        ativo = self.ui.rb_Ativo.isChecked()  # True=ativos, False=inativos
        try:
            usuarios = self._service.pesquisar(filtro, ativo=ativo)
        except Exception as exc:
            logger.exception("Falha ao pesquisar usuários")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível pesquisar:\n{exc}")
            return
        self._popular_lista(usuarios)

    def _confirmar(self):
        """Confirmar: com seleção, devolve o registro;
        sem seleção, apenas pesquisa."""
        if self.ui.tb_Usuario.currentIndex().isValid():
            self.accept()
        else:
            self._pesquisar()

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
        ajustar_larguras(self.ui.tb_Usuario,
                         coluna_stretch=COLUNA_STRETCH)

    def usuario_selecionado(self) -> Usuario | None:
        indice = self.ui.tb_Usuario.currentIndex()
        if not indice.isValid():
            return None
        linha = indice.row()
        item = self._modelo.item(linha, 0)
        if item is None or self._service is None:
            return None
        try:
            return self._service.buscar_por_codigo(item.text())
        except Exception as exc:
            logger.exception("Falha ao carregar usuário selecionado")
            QMessageBox.critical(
                self, "Erro",
                f"Falha ao carregar o usuário:\n{exc}")
            return None
