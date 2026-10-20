# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Abastecimento.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via
RelatorioAbastecimentoService.

Filtros: período (data inicial/final) + placa do caminhão (texto
livre ou selecionada na pesquisa de caminhões via "..."). Padrão do
período: do primeiro dia do mês corrente até hoje. Placa vazia traz
TODOS os caminhões.
"""
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox, QWidget

from app.controllers.relatorio_abastecimento_preview_controller import (
    RelatorioAbastecimentoPreviewController,
)
from app.services.relatorio_abastecimento_service import (
    RelatorioAbastecimentoService,
)
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.views.ui_relatorio_abastecimento import Ui_Rel_Abastecimento

logger = get_logger("relatorio_abastecimento")


class RelatorioAbastecimentoController(QWidget):
    """Tela de filtros do relatório de abastecimento."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Abastecimento()
        self.ui.setupUi(self)

        self._service = RelatorioAbastecimentoService()

        # período padrão: primeiro dia do mês corrente até hoje
        hoje = QDate.currentDate()
        self.ui.dt_Data_Inicial.setDate(
            QDate(hoje.year(), hoje.month(), 1))
        self.ui.dt_Data_Final.setDate(hoje)

        self.ui.bt_Pesquisar_Abastecimento.clicked.connect(
            self._pesquisar_caminhao)
        self.ui.bt_Filtrar.clicked.connect(self._gerar)

        self._definir_tab_order()

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda->direita, cima->baixo)."""
        self.setTabOrder(self.ui.dt_Data_Inicial, self.ui.dt_Data_Final)
        self.setTabOrder(self.ui.dt_Data_Final, self.ui.txt_PLaca)
        self.setTabOrder(self.ui.txt_PLaca,
                         self.ui.bt_Pesquisar_Abastecimento)
        self.setTabOrder(self.ui.bt_Pesquisar_Abastecimento,
                         self.ui.bt_Filtrar)

    # ---------------- filtros ----------------

    def _pesquisar_caminhao(self):
        """'...' abre a pesquisa de caminhões e copia a placa."""
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
            self.ui.txt_PLaca.setText(
                caminhao.placa or caminhao.codigo or "")

    # ---------------- geração ----------------

    def _gerar(self):
        placa = self.ui.txt_PLaca.text().strip()

        # PySide6: QDate.toPython() devolve datetime.date
        inicial = self.ui.dt_Data_Inicial.date().toPython()
        final = self.ui.dt_Data_Final.date().toPython()
        if inicial > final:
            QMessageBox.warning(
                self, "Atenção",
                "A data inicial não pode ser maior que a final.")
            self.ui.dt_Data_Inicial.setFocus()
            return

        try:
            itens = self._service.itens_por_caminhao(placa, inicial, final)
        except Exception as exc:
            logger.exception("Falha ao gerar relatório de abastecimento")
            QMessageBox.critical(
                self, "Relatório", mensagem_erro(exc))
            return
        if not itens:
            QMessageBox.information(
                self, "Relatório",
                "Nenhum abastecimento encontrado para os filtros.")
            return

        preview = RelatorioAbastecimentoPreviewController(
            itens, parent=self)
        preview.exec()
