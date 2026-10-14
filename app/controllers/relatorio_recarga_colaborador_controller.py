# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Recargas por Colaborador.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via
RelatorioRecargaColaboradorService.

Filtros: período (data inicial/final) + colaborador (nome livre ou
selecionado na pesquisa de colaboradores via "...").
"""
from PySide6.QtWidgets import QMessageBox, QWidget

from app.services.relatorio_recarga_colaborador_service import (
    RelatorioRecargaColaboradorService,
)
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.views.ui_relatorio_recarga_colaborador import (
    Ui_Rel_Recarga_Colaborador,
)

logger = get_logger("relatorio_recarga_colaborador")


class RelRecargaColaboradorController(QWidget):
    """Tela de filtros do relatório de recargas por colaborador."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Rel_Recarga_Colaborador()
        self.ui.setupUi(self)

        self._service = RelatorioRecargaColaboradorService()
        self._colaborador = None  # seleção vinda da pesquisa ("...")

        self.ui.bt_Pesquisar_Colaborador.clicked.connect(
            self._pesquisar_colaborador)
        self.ui.txt_Colaborador.textEdited.connect(
            self._colaborador_digitado)
        self.ui.bt_Filtrar.clicked.connect(self._gerar_relatorio)

        self._definir_tab_order()

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda→direita, cima→baixo)."""
        self.setTabOrder(self.ui.dt_Data_Inicial, self.ui.dt_Data_Final)
        self.setTabOrder(self.ui.dt_Data_Final, self.ui.txt_Colaborador)
        self.setTabOrder(self.ui.txt_Colaborador,
                         self.ui.bt_Pesquisar_Colaborador)
        self.setTabOrder(self.ui.bt_Pesquisar_Colaborador,
                         self.ui.bt_Filtrar)

    # ---------------- filtros ----------------

    def _colaborador_digitado(self):
        """Usuário digitou outro nome: invalida a seleção anterior."""
        self._colaborador = None

    def _pesquisar_colaborador(self):
        """Abre a pesquisa de colaboradores e copia o nome."""
        from app.controllers.pesquisa_colaborador_controller import (
            PesquisaColaboradorController,
        )
        dialogo = PesquisaColaboradorController(self)
        if dialogo.exec():
            colaborador = dialogo.colaborador_selecionado()
            if colaborador:
                self._colaborador = colaborador
                self.ui.txt_Colaborador.setText(colaborador.nome)

    # ---------------- geração ----------------

    def _gerar_relatorio(self):
        nome = self.ui.txt_Colaborador.text().strip()
        documento = (self._colaborador.documento or ""
                     if self._colaborador else "")
        if not nome:
            QMessageBox.warning(self, "Relatório", "Informe o colaborador.")
            self.ui.txt_Colaborador.setFocus()
            return

        data_inicial = self.ui.dt_Data_Inicial.date().toPyDate()
        data_final = self.ui.dt_Data_Final.date().toPyDate()
        if data_inicial > data_final:
            QMessageBox.warning(
                self, "Relatório",
                "Data inicial maior que a data final.")
            self.ui.dt_Data_Inicial.setFocus()
            return

        try:
            registros = self._service.itens_por_colaborador(
                nome=nome, documento=documento,
                data_inicial=data_inicial, data_final=data_final)
        except Exception as exc:
            QMessageBox.critical(self, "Relatório", self._mensagem_erro(exc))
            return

        if not registros:
            QMessageBox.information(
                self, "Relatório",
                "Nenhum item de recarga encontrado para este colaborador "
                "no período informado.")
            return

        # pré-visualização: mesmo layout do PDF, com PDF/XLSX/CSV
        from app.controllers.relatorio_recarga_colaborador_preview_controller import (
            RelRecargaColaboradorPreviewController,
        )
        dialogo = RelRecargaColaboradorPreviewController(
            registros, self._subtitulo(nome, documento,
                                       data_inicial, data_final), self)
        dialogo.exec()

    @staticmethod
    def _subtitulo(nome: str, documento: str,
                   data_inicial, data_final) -> str:
        doc = "".join(c for c in (documento or "") if c.isdigit())
        if len(doc) == 11:
            colaborador = (f"Colaborador: {nome} "
                           f"(CPF {doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]})")
        else:
            colaborador = f"Colaborador: {nome}"
        periodo = (f"Período: {data_inicial.strftime('%d/%m/%Y')} a "
                   f"{data_final.strftime('%d/%m/%Y')}")
        return f"{colaborador}    {periodo}"

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(exc, prefixo="Erro ao gerar o relatório")
