# -*- coding: utf-8 -*-
"""Controller da pesquisa de colaboradores."""
from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QMessageBox

from app.models.colaborador import Colaborador
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_pesquisa_colaborador import Ui_Pesquisa_Colaborador

try:
    from app.services.colaborador_service import ColaboradorService
except ImportError:
    ColaboradorService = None

logger = get_logger("pesquisa_colaborador")
COLUNAS = ["Código", "Nome", "CPF"]
COLUNA_STRETCH = 1
DEBOUNCE_MS = 300


class PesquisaColaboradorController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Pesquisa_Colaborador()
        self.ui.setupUi(self)

        self._service = (ColaboradorService()
                         if ColaboradorService else None)
        if self._service is None:
            logger.warning("ColaboradorService nao encontrado")

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS)
        self.ui.tb_Colaborador.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Colaborador,
                          coluna_stretch=COLUNA_STRETCH, ordenavel=True)

        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)

        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._pesquisar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self.ui.tb_Colaborador.doubleClicked.connect(self.accept)

        try:
            self._pesquisar()
        except Exception as exc:
            logger.exception("Falha ao carregar colaboradores na abertura")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar colaboradores:\n{exc}")

    def _agendar_filtro(self):
        self._timer_filtro.start(DEBOUNCE_MS)

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
        for colaborador in registros:
            self._modelo.appendRow([
                QStandardItem(colaborador.codigo),
                QStandardItem(colaborador.nome),
                QStandardItem(colaborador.documento or ""),
            ])
        ajustar_larguras(self.ui.tb_Colaborador, coluna_stretch=COLUNA_STRETCH)

    def colaborador_selecionado(self) -> Colaborador | None:
        indice = self.ui.tb_Colaborador.currentIndex()
        if not indice.isValid():
            return None
        linha = indice.row()
        item = self._modelo.item(linha, 0)
        if item is None or self._service is None:
            return None
        try:
            return self._service.buscar_por_codigo(item.text())
        except Exception as exc:
            logger.exception("Falha ao carregar colaborador selecionado")
            QMessageBox.critical(
                self, "Erro", f"Falha ao carregar o colaborador:\n{exc}")
            return None
