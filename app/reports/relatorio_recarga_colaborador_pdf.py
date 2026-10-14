# -*- coding: utf-8 -*-
"""Geração do PDF do relatório de recargas por colaborador.

Mesmo layout da pré-visualização (o HTML é compartilhado). PDF via Qt
(QTextDocument + QPrinter) — sem dependências extras.
"""
from datetime import datetime

from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter

from app.models.relatorio_recarga_colaborador import ItemRecargaRelatorio
from app.utils.logger import get_logger

logger = get_logger("relatorio_recarga_colaborador_pdf")

AZUL = "#1F3B5B"
ZEBRA = "#F2F5F8"
LINHA = "#C9D3DE"
CINZA = "#5A6B7B"
TEXTO = "#222222"

_CABECALHOS = ["Data", "Seq", "Colaborador", "CPF", "Carga",
               "Sem Carga", "Valor", "Benefício"]


def _moeda(valor: float | None) -> str:
    """Valor em moeda no padrão brasileiro (1234.5 -> 'R$ 1.234,50')."""
    if valor is None:
        return "—"
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",")
    return f"R$ {texto.replace('X', '.')}"


def _formatar_documento(documento: str) -> str:
    """CPF com máscara (40513975802 -> 405.139.758-02)."""
    doc = "".join(c for c in (documento or "") if c.isdigit())
    if len(doc) == 11:
        return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
    return documento or ""


def html_relatorio(registros: list[ItemRecargaRelatorio],
                   subtitulo: str = "") -> str:
    """HTML do relatório — usado na pré-visualização E no PDF."""
    partes = [
        f"<h2 style='color:{AZUL};margin-bottom:2px;'>"
        "RELATÓRIO DE RECARGAS POR COLABORADOR</h2>",
    ]
    if subtitulo:
        partes.append(f"<p style='color:{CINZA};'>{subtitulo}</p>")
    partes.append(
        f"<p style='color:{CINZA};'>"
        f"Emitido em {datetime.now():%d/%m/%Y %H:%M}</p>")
    if not registros:
        partes.append("<p>Nenhuma recarga encontrada.</p>")
        return "".join(partes)

    partes += [
        "<table width='100%' cellspacing='0' cellpadding='4' "
        f"style='border:1px solid {LINHA};font-size:9pt;color:{TEXTO};"
        "border-collapse:collapse;'>",
        f"<tr style='background-color:{ZEBRA};color:{AZUL};'>"
        + "".join(f"<th align='left'>{c}</th>" for c in _CABECALHOS)
        + "</tr>",
    ]
    for indice, r in enumerate(registros):
        fundo = ZEBRA if indice % 2 else "#FFFFFF"
        partes.append(
            f"<tr style='background-color:{fundo};'>"
            f"<td>{r.data.strftime('%d/%m/%Y') if r.data else '—'}</td>"
            f"<td>{r.sequencia}</td>"
            f"<td>{r.nome}</td>"
            f"<td>{_formatar_documento(r.documento)}</td>"
            f"<td>{r.carga}</td>"
            f"<td>{r.sem_carga}</td>"
            f"<td align='right'>{_moeda(r.valor)}</td>"
            f"<td>{r.beneficio}</td>"
            "</tr>")
    total = sum(r.valor for r in registros)
    partes.append(
        "<tr style='background-color:#E8EDF2;font-weight:bold;"
        f"color:{TEXTO};'>"
        f"<td colspan='6'>Totais — {len(registros)} item(ns)</td>"
        f"<td align='right'>{_moeda(total)}</td>"
        "<td></td></tr></table>")
    return "".join(partes)


def gerar_pdf_recarga_colaborador(registros: list[ItemRecargaRelatorio],
                                  caminho: str,
                                  subtitulo: str = "") -> str:
    impressora = QPrinter(QPrinter.PrinterMode.HighResolution)
    impressora.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    impressora.setOutputFileName(str(caminho))
    documento = QTextDocument()
    documento.setHtml(html_relatorio(registros, subtitulo))
    documento.print_(impressora)
    logger.info("PDF gerado: %s", caminho)
    return caminho
