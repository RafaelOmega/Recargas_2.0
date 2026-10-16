# -*- coding: utf-8 -*-
"""Controller da pesquisa de caminhões.

Filtro por código, modelo ou placa (debounce 300ms) + radio buttons:
Ativos (padrão) / Inativos — trocar o radio refaz a pesquisa.
Navegação (Tab) em modo Z: pesquisa -> Ativos -> Inativos
-> Confirmar -> grade. Ordenação padrão: coluna Código (descendente,
numérica — valor real guardado no Qt.UserRole).
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.caminhao import Caminhao
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_caminhoes import Ui_Pesquisa_Caminhoes

try:
    from app.services.caminhao_service import CaminhaoService
except ImportError:
    CaminhaoService = None

logger = get_logger("pesquisa_caminhoes")

COLUNAS = ["Código", "Modelo", "Placa"]
COLUNA_PADRAO = 0  # Código
COLUNA_STRETCH = 1  # Modelo
DEBOUNCE_MS = 300


class PesquisaCaminhoesController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Caminhoes()
        self.ui.setupUi(self)

        self._service = (CaminhaoService()
                         if CaminhaoService else None)
        if self._service is None:
            logger.warning("CaminhaoService nao encontrado")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        # ordenação usa o valor real guardado no Qt.UserRole
        self._modelo.setSortRole(Qt.ItemDataRole.UserRole)
        self.ui.tb_Caminhoes.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Caminhoes,
                          coluna_stretch=COLUNA_STRETCH, ordenavel=True)
        # ordenação padrão: Código descendente (numérica)
        self.ui.tb_Caminhoes.sortByColumn(
            COLUNA_PADRAO, Qt.SortOrder.DescendingOrder)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(DEBOUNCE_MS)
        self._timer.timeout.connect(self._pesquisar)

        self._conectar_eventos()
        self._pesquisar()

    # ---------------- conexões ----------------

    def _conectar_eventos(self):
        self.ui.txt_Pesquisa.textChanged.connect(self._timer.start)
        self.ui.rb_Ativo.toggled.connect(self._pesquisar)
        self.ui.bt_Pesquisa.clicked.connect(self._confirmar)
        self.ui.tb_Caminhoes.doubleClicked.connect(self._confirmar)

    # ---------------- ações ----------------

    def _confirmar(self):
        if self.ui.tb_Caminhoes.currentIndex().isValid():
            self.accept()
        else:
            self._pesquisar()

    def _pesquisar(self):
        if self._service is None:
            return
        ativo = self.ui.rb_Ativo.isChecked()
        filtro = self.ui.txt_Pesquisa.text().strip()
        try:
            caminhoes = self._service.pesquisar(filtro, ativo=ativo)
        except Exception as exc:
            logger.exception("Falha ao pesquisar caminhões")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível pesquisar:\n{mensagem_erro(exc)}")
            return
        self._popular_lista(caminhoes)

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
        ajustar_larguras(self.ui.tb_Caminhoes,
                         coluna_stretch=COLUNA_STRETCH)

    def _item_ordenavel(self, texto: str, valor) -> QStandardItem:
        item = QStandardItem(texto)
        item.setEditable(False)
        item.setData(valor, Qt.ItemDataRole.UserRole)
        return item

    def caminhao_selecionado(self) -> Caminhao | None:
        indice = self.ui.tb_Caminhoes.currentIndex()
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
