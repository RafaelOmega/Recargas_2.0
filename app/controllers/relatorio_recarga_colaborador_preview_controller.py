# -*- coding: utf-8 -*-
"""Pré-visualização do relatório de recargas por colaborador.

Mostra os dados no mesmo layout do PDF e permite gerar PDF, XLSX ou CSV.
Aberta pelo botão Filtrar da tela de relatório (a tela de filtros não muda).

O QTextBrowser usa folha de estilo própria (fundo branco, "papel"),
pois o tema escuro global do sistema torna o HTML claro ilegível.
"""
from datetime import datetime

from PySide6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QMessageBox,
                               QPushButton, QTextBrowser, QVBoxLayout)

from app.reports.relatorio_recarga_colaborador_pdf import html_relatorio
from app.utils.logger import get_logger

logger = get_logger("relatorio_recarga_colaborador_preview")

_ESTILO_PAPEL = """
QTextBrowser {
    background-color: #FFFFFF;
    color: #222222;
    border: 1px solid #C9D3DE;
}
"""


class RelRecargaColaboradorPreviewController(QDialog):
    """Pré-visualização do relatório + exportação (PDF/XLSX/CSV)."""

    def __init__(self, registros, subtitulo: str, parent=None):
        super().__init__(parent)
        self._registros = registros
        self._subtitulo = subtitulo

        self.setWindowTitle(
            "Pré-visualização — Relatório de Recargas por Colaborador")
        self.resize(980, 600)

        self.txt_Visualizacao = QTextBrowser(self)
        self.txt_Visualizacao.setStyleSheet(_ESTILO_PAPEL)

        self.bt_PDF = QPushButton("Gerar PDF", self)
        self.bt_XLSX = QPushButton("Gerar XLSX", self)
        self.bt_CSV = QPushButton("Gerar CSV", self)
        self.bt_Fechar = QPushButton("Fechar", self)

        botoes = QHBoxLayout()
        botoes.addWidget(self.bt_PDF)
        botoes.addWidget(self.bt_XLSX)
        botoes.addWidget(self.bt_CSV)
        botoes.addStretch()
        botoes.addWidget(self.bt_Fechar)

        layout = QVBoxLayout(self)
        layout.addWidget(self.txt_Visualizacao)
        layout.addLayout(botoes)

        self.bt_PDF.clicked.connect(self._gerar_pdf)
        self.bt_XLSX.clicked.connect(self._gerar_xlsx)
        self.bt_CSV.clicked.connect(self._gerar_csv)
        self.bt_Fechar.clicked.connect(self.accept)

        self._montar_visualizacao()

    # ---------------- visualização (mesmo layout do PDF) ----------------

    def _montar_visualizacao(self):
        self.txt_Visualizacao.setHtml(
            html_relatorio(self._registros, self._subtitulo))

    # ---------------- exportação ----------------

    def _gerar_pdf(self):
        from app.reports.relatorio_recarga_colaborador_pdf import (
            gerar_pdf_recarga_colaborador,
        )
        self._exportar("PDF (*.pdf)", gerar_pdf_recarga_colaborador)

    def _gerar_xlsx(self):
        from app.reports.relatorio_recarga_colaborador_export import (
            gerar_xlsx_recarga_colaborador,
        )
        self._exportar("Excel (*.xlsx)", gerar_xlsx_recarga_colaborador)

    def _gerar_csv(self):
        from app.reports.relatorio_recarga_colaborador_export import (
            gerar_csv_recarga_colaborador,
        )
        self._exportar("CSV (*.csv)", gerar_csv_recarga_colaborador)

    def _exportar(self, filtro_arquivo, funcao):
        sugerido = f"Recargas_Colaborador_{datetime.now():%Y-%m-%d}"
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório", sugerido, filtro_arquivo)
        if not caminho:
            return
        try:
            funcao(self._registros, caminho, subtitulo=self._subtitulo)
        except Exception as exc:
            QMessageBox.critical(
                self, "Relatório", f"Erro ao gerar o arquivo:\n{exc}")
            return
        logger.info("Arquivo gerado: %s", caminho)
        QMessageBox.information(
            self, "Relatório", f"Arquivo gerado com sucesso:\n{caminho}")
