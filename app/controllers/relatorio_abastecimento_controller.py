# -*- coding: utf-8 -*-
"""Controller do relatório de abastecimento por caminhão.

Filtros: período (padrão 1º dia do mês → hoje) + caminhão (código,
modelo ou placa livre, ou "..."); vazio = Todos. Valida data inicial
≤ final. Abre o preview (QDialog) com os dados.
"""
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox, QWidget

from app.controllers.relatorio_abastecimento_preview_controller import (
    RelatorioAbastecimentoPreviewController,
)
from app.services.relatorio_abastecimento_service import (
    RelatorioAbastecimentoService,
)
from app.utils.logger import get_logger
from app.views.ui_relatorio_abastecimento import Ui_Rel_Abastecimento

logger = get_logger("relatorio_abastecimento")


class RelatorioAbastecimentoController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Abastecimento()
        self.ui.setupUi(self)

        self._service = RelatorioAbastecimentoService()

        hoje = QDate.currentDate()
        primeiro = QDate(hoje.year(), hoje.month(), 1)
        self.ui.dt_Data_Inicial.setDate(primeiro)
        self.ui.dt_Data_Final.setDate(hoje)

        self.ui.bt_Pesquisar.clicked.connect(self._pesquisar_caminhao)
        self.ui.bt_Gerar.clicked.connect(self._gerar)

    def _pesquisar_caminhao(self):
        """'...' abre a pesquisa de caminhões e aplica o escolhido."""
        from app.controllers.pesquisa_caminhoes_controller import (
            PesquisaCaminhoesController,
        )
        try:
            dialogo = PesquisaCaminhoesController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa de caminhões")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() != dialogo.DialogCode.Accepted:
            return
        caminhao = dialogo.caminhao_selecionado()
        if caminhao:
            self.ui.txt_Pesquisa.setText(
                caminhao.placa or caminhao.codigo or "")

    def _gerar(self):
        inicial = self.ui.dt_Data_Inicial.date().toPython()
        final = self.ui.dt_Data_Final.date().toPython()
        if inicial > final:
            QMessageBox.warning(
                self, "Atenção",
                "A data inicial não pode ser maior que a final.")
            return
        caminhao = self.ui.txt_Pesquisa.text().strip()
        try:
            itens = self._service.itens_por_caminhao(
                caminhao, inicial, final)
        except Exception as exc:
            logger.exception("Falha ao gerar relatório de abastecimento")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível gerar o relatório:\n{exc}")
            return
        if not itens:
            QMessageBox.information(
                self, "Relatório",
                "Nenhum abastecimento encontrado para os filtros.")
            return
        preview = RelatorioAbastecimentoPreviewController(
            itens, parent=self)
        preview.exec()
