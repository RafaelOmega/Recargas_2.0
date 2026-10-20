# -*- coding: utf-8 -*-
"""Preview do relatório de abastecimento por caminhão.

Layout em BLOCOS por caminhão (barra azul código+modelo+placa, tabela
de itens, SUBTOTAL; TOTAL GERAL só com 2+ blocos). Botões PDF/XLSX/CSV
salvam via QFileDialog (sugestão Abastecimento_AAAA-MM-DD).

Coluna KM/L: consumo por item (km rodados / litros). No SUBTOTAL e no
TOTAL GERAL o valor é PONDERADO (km total / litros totais), nunca a
média das médias — assim trechos curtos não distorcem o resultado.
"""
from datetime import datetime

from PySide6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout,
                               QMessageBox, QPushButton, QTextBrowser,
                               QVBoxLayout)

from app.reports.relatorio_abastecimento_export import (
    exportar_csv_abastecimento, exportar_xlsx_abastecimento)
from app.reports.relatorio_abastecimento_pdf import gerar_pdf_abastecimento
from app.utils.logger import get_logger

logger = get_logger("relatorio_abastecimento_preview")

_ESTILO_PAPEL = """
QTextBrowser { background-color: #FFFFFF; color: #222; }
"""

_AZUL = "#1F3B5B"
_ZEBRA = "#F2F5F8"
_SUBTOTAL = "#E8EDF2"
_TOTAL_GERAL = "#DCE4EE"


class RelatorioAbastecimentoPreviewController(QDialog):

    def __init__(self, itens, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Relatório de Abastecimento")
        self.resize(1040, 600)
        self._itens = itens

        self._html = QTextBrowser(self)
        self._html.setStyleSheet(_ESTILO_PAPEL)
        self._html.setHtml(self._montar_html())

        self._bt_pdf = QPushButton("Gerar PDF", self)
        self._bt_xlsx = QPushButton("Gerar XLSX", self)
        self._bt_csv = QPushButton("Gerar CSV", self)
        self._bt_fechar = QPushButton("Fechar", self)

        botoes = QHBoxLayout()
        botoes.addWidget(self._bt_pdf)
        botoes.addWidget(self._bt_xlsx)
        botoes.addWidget(self._bt_csv)
        botoes.addStretch()
        botoes.addWidget(self._bt_fechar)

        layout = QVBoxLayout(self)
        layout.addWidget(self._html)
        layout.addLayout(botoes)

        self._bt_pdf.clicked.connect(self._gerar_pdf)
        self._bt_xlsx.clicked.connect(self._gerar_xlsx)
        self._bt_csv.clicked.connect(self._gerar_csv)
        self._bt_fechar.clicked.connect(self.accept)

    # ---------------- HTML ----------------

    def _montar_html(self) -> str:
        blocos = []
        total_geral = 0.0
        total_km = 0
        atual = None
        itens_bloco = []

        def fechar_bloco():
            nonlocal itens_bloco, total_geral, total_km
            if not itens_bloco:
                return
            subtotal = sum(i.litros for i in itens_bloco)
            total_geral += subtotal
            total_km += sum(i.km_rodados for i in itens_bloco)
            blocos.append(self._bloco_html(atual, itens_bloco, subtotal))
            itens_bloco = []

        for item in self._itens:
            chave = item.caminhao_codigo
            if atual is not None and chave != atual:
                fechar_bloco()
            atual = chave
            itens_bloco.append(item)
        fechar_bloco()

        corpo = "".join(blocos)
        if len(blocos) > 1:
            corpo += self._total_geral_html(total_geral, total_km)

        return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body {{ font-family:'Segoe UI',Arial,sans-serif; font-size:12px; color:#222; margin:16px; }}
h1 {{ font-size:18px; color:{_AZUL}; margin:0 0 4px 0; }}
.sub {{ color:#555; margin-bottom:16px; }}
.bloco {{ margin-bottom:14px; border:1px solid #C9D3DE; }}
.cab {{ background:{_AZUL}; color:#fff; padding:6px 10px; font-weight:600; }}
table {{ width:100%; border-collapse:collapse; }}
th, td {{ border:1px solid #C9D3DE; padding:4px 8px; text-align:left; }}
th {{ background:{_ZEBRA}; }}
td.num, th.num {{ text-align:right; }}
.subtotal {{ background:{_SUBTOTAL}; font-weight:600; }}
.total-geral {{ background:{_TOTAL_GERAL}; font-weight:700; }}
</style></head><body>
<h1>Relatório de Abastecimento por Caminhão</h1>
<div class="sub">{self._periodo()}</div>
{corpo}
</body></html>"""

    def _bloco_html(self, codigo, itens, subtotal) -> str:
        linhas = []
        for i in itens:
            linhas.append(
                f"<tr><td>{i.sequencia}</td>"
                f"<td>{i.data:%d/%m/%Y}</td>"
                f"<td>{i.colaborador_nome}</td>"
                f"<td>{i.destino}</td>"
                f"<td class='num'>{i.km_inicio}</td>"
                f"<td class='num'>{i.km_final}</td>"
                f"<td class='num'>{i.litros:.2f}</td>"
                f"<td class='num'>{self._km_l(i)}</td></tr>")
        primeiro = itens[0]
        titulo = (f"{primeiro.caminhao_codigo} · {primeiro.caminhao_modelo}"
                  f" · {primeiro.placa}")
        km_bloco = sum(i.km_rodados for i in itens)
        return (
            f"<div class='bloco'><div class='cab'>{titulo}</div>"
            "<table><tr><th>Seq.</th><th>Data</th><th>Colaborador</th>"
            "<th>Destino</th><th class='num'>KM Início</th>"
            "<th class='num'>KM Final</th><th class='num'>Litros</th>"
            "<th class='num'>KM/L</th></tr>"
            + "".join(linhas)
            + f"<tr class='subtotal'><td colspan='6'>SUBTOTAL</td>"
              f"<td class='num'>{subtotal:.2f}</td>"
              f"<td class='num'>{self._km_l_ponderado(km_bloco, subtotal)}"
              f"</td></tr>"
              "</table></div>")

    def _total_geral_html(self, total, total_km) -> str:
        return (f"<table><tr class='total-geral'>"
                f"<td colspan='6'>TOTAL GERAL</td>"
                f"<td class='num'>{total:.2f}</td>"
                f"<td class='num'>{self._km_l_ponderado(total_km, total)}"
                f"</td></tr></table>")

    @staticmethod
    def _km_l(item) -> str:
        """KM/L do item formatado, ou '—' quando não há litros."""
        valor = item.km_por_litro
        return "—" if valor is None else f"{valor:.2f}"

    @staticmethod
    def _km_l_ponderado(km: int, litros: float) -> str:
        """KM/L do conjunto: km total / litros totais."""
        if litros <= 0:
            return "—"
        return f"{km / litros:.2f}"

    def _periodo(self) -> str:
        datas = [i.data for i in self._itens if i.data]
        if not datas:
            return ""
        return (f"Período: {min(datas):%d/%m/%Y} a "
                f"{max(datas):%d/%m/%Y}")

    # ---------------- exportação ----------------

    def _sugestao(self, ext: str) -> str:
        return f"Abastecimento_{datetime.now():%Y-%m-%d}.{ext}"

    def _gerar_pdf(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório", self._sugestao("pdf"),
            "PDF (*.pdf)")
        if not caminho:
            return
        try:
            gerar_pdf_abastecimento(self._itens, caminho)
        except Exception as exc:
            logger.exception("Falha ao gerar PDF")
            QMessageBox.critical(
                self, "Erro", f"Não foi possível gerar o PDF:\n{exc}")
            return
        QMessageBox.information(self, "Relatório", "PDF gerado com sucesso.")

    def _gerar_xlsx(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório", self._sugestao("xlsx"),
            "Excel (*.xlsx)")
        if not caminho:
            return
        try:
            exportar_xlsx_abastecimento(self._itens, caminho)
        except Exception as exc:
            logger.exception("Falha ao gerar XLSX")
            QMessageBox.critical(
                self, "Erro", f"Não foi possível gerar o XLSX:\n{exc}")
            return
        QMessageBox.information(
            self, "Relatório", "XLSX gerado com sucesso.")

    def _gerar_csv(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório", self._sugestao("csv"),
            "CSV (*.csv)")
        if not caminho:
            return
        try:
            exportar_csv_abastecimento(self._itens, caminho)
        except Exception as exc:
            logger.exception("Falha ao gerar CSV")
            QMessageBox.critical(
                self, "Erro", f"Não foi possível gerar o CSV:\n{exc}")
            return
        QMessageBox.information(
            self, "Relatório", "CSV gerado com sucesso.")
