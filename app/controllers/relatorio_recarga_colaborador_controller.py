# -*- coding: utf-8 -*-
"""Controller da tela de Relatório de Recargas por Colaborador.

Responsabilidade: APENAS controle de tela (filtros, botões).
Ao filtrar, abre a pré-visualização (mesmo layout do PDF), de onde
o usuário gera PDF, XLSX ou CSV. Dados via
RelatorioRecargaColaboradorService.
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
        try:
            registros = self._service.itens_por_colaborador(
                nome=nome, documento=documento)
        except Exception as exc:
            QMessageBox.critical(self, "Relatório", self._mensagem_erro(exc))
            return

        if not registros:
            QMessageBox.information(
                self, "Relatório",
                "Nenhum item de recarga encontrado para este colaborador.")
            return

        # pré-visualização: mesmo layout do PDF, com PDF/XLSX/CSV
        from app.controllers.relatorio_recarga_colaborador_preview_controller import (
            RelRecargaColaboradorPreviewController,
        )
        dialogo = RelRecargaColaboradorPreviewController(
            registros, self._subtitulo(nome, documento), self)
        dialogo.exec()

    @staticmethod
    def _subtitulo(nome: str, documento: str) -> str:
        doc = "".join(c for c in (documento or "") if c.isdigit())
        if len(doc) == 11:
            return (f"Colaborador: {nome} "
                    f"(CPF {doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]})")
        return f"Colaborador: {nome}"

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(exc, prefixo="Erro ao gerar o relatório")
