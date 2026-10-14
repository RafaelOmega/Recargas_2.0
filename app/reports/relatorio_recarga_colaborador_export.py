# -*- coding: utf-8 -*-
"""Exportação do relatório de recargas por colaborador para XLSX e CSV.

Mesmos dados e mesmo layout em BLOCOS do PDF: barra com o nome do
colaborador no topo, itens e subtotal no fim de cada bloco. XLSX grava
valores numéricos com formato de célula; CSV grava valores já
formatados no padrão brasileiro (separador ';' e BOM para o Excel).
"""
import csv
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from app.models.relatorio_recarga_colaborador import ItemRecargaRelatorio
from app.reports.relatorio_recarga_colaborador_pdf import (
    _agrupar_por_colaborador, _formatar_documento, _moeda,
)
from app.utils.logger import get_logger

logger = get_logger("relatorio_recarga_colaborador_export")

AZUL = "1F3B5B"
ZEBRA = "F2F5F8"
SUBTOTAL = "E8EDF2"
TOTAL_GERAL = "DCE4EE"

_CABECALHOS = ["Data", "Seq", "CPF", "Carga", "Sem Carga", "Valor",
               "Benefício"]
_FMT_MOEDA = '"R$" #,##0.00'


def _titulo_bloco(nome: str, itens: list[ItemRecargaRelatorio]) -> str:
    """Nome do colaborador (+ CPF) para o cabeçalho do bloco."""
    documento = next((r.documento for r in itens if r.documento), "")
    doc = _formatar_documento(documento)
    return f"{nome} · CPF {doc}" if doc else nome


# ---------------- XLSX ----------------

def gerar_xlsx_recarga_colaborador(registros: list[ItemRecargaRelatorio],
                                   caminho: str,
                                   subtitulo: str = "") -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "Recargas por Colaborador"

    ws["A1"] = "RELATÓRIO DE RECARGAS POR COLABORADOR"
    ws["A1"].font = Font(bold=True, size=14, color=AZUL)
    linha = 2
    if subtitulo:
        ws.cell(linha, 1, subtitulo)
        linha += 1
    ws.cell(linha, 1, f"Emitido em {datetime.now():%d/%m/%Y %H:%M}")
    linha += 2

    grupos = _agrupar_por_colaborador(registros)
    for nome, itens in grupos:
        # barra do bloco: nome do colaborador no topo
        celula = ws.cell(linha, 1, _titulo_bloco(nome, itens))
        celula.font = Font(bold=True, color="FFFFFF")
        celula.fill = PatternFill("solid", fgColor=AZUL)
        ws.merge_cells(start_row=linha, start_column=1,
                       end_row=linha, end_column=7)
        linha += 1

        for coluna, texto in enumerate(_CABECALHOS, start=1):
            cel = ws.cell(linha, coluna, texto)
            cel.font = Font(bold=True, color=AZUL)
            cel.fill = PatternFill("solid", fgColor=ZEBRA)
        linha += 1

        for indice, r in enumerate(itens):
            fundo = ZEBRA if indice % 2 else "FFFFFF"
            ws.cell(linha, 1,
                    r.data.strftime("%d/%m/%Y") if r.data else "")
            ws.cell(linha, 2, r.sequencia)
            ws.cell(linha, 3, _formatar_documento(r.documento))
            ws.cell(linha, 4, r.carga)
            ws.cell(linha, 5, r.sem_carga)
            cel_valor = ws.cell(linha, 6, r.valor)
            cel_valor.number_format = _FMT_MOEDA
            ws.cell(linha, 7, r.beneficio)
            for coluna in range(1, 8):
                ws.cell(linha, coluna).fill = PatternFill("solid",
                                                          fgColor=fundo)
            linha += 1

        subtotal = sum(r.valor for r in itens)
        cel_rotulo = ws.cell(linha, 1,
                             f"Subtotal ({len(itens)} item(ns))")
        cel_rotulo.font = Font(bold=True)
        cel_rotulo.fill = PatternFill("solid", fgColor=SUBTOTAL)
        ws.merge_cells(start_row=linha, start_column=1,
                       end_row=linha, end_column=5)
        cel_sub = ws.cell(linha, 6, subtotal)
        cel_sub.font = Font(bold=True)
        cel_sub.fill = PatternFill("solid", fgColor=SUBTOTAL)
        cel_sub.number_format = _FMT_MOEDA
        ws.cell(linha, 7).fill = PatternFill("solid", fgColor=SUBTOTAL)
        linha += 2  # linha em branco entre blocos

    if len(grupos) > 1:
        total = sum(r.valor for r in registros)
        cel_rotulo = ws.cell(linha, 1,
                             f"Total geral — {len(registros)} item(ns)")
        cel_rotulo.font = Font(bold=True, color=AZUL)
        cel_rotulo.fill = PatternFill("solid", fgColor=TOTAL_GERAL)
        ws.merge_cells(start_row=linha, start_column=1,
                       end_row=linha, end_column=5)
        cel_total = ws.cell(linha, 6, total)
        cel_total.font = Font(bold=True, color=AZUL)
        cel_total.fill = PatternFill("solid", fgColor=TOTAL_GERAL)
        cel_total.number_format = _FMT_MOEDA
        ws.cell(linha, 7).fill = PatternFill("solid", fgColor=TOTAL_GERAL)

    for coluna, largura in zip("ABCDEFG",
                               (12, 8, 16, 12, 12, 14, 14)):
        ws.column_dimensions[coluna].width = largura

    wb.save(caminho)
    logger.info("XLSX gerado: %s", caminho)
    return caminho


# ---------------- CSV ----------------

def gerar_csv_recarga_colaborador(registros: list[ItemRecargaRelatorio],
                                  caminho: str,
                                  subtitulo: str = "") -> str:
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo, delimiter=";")
        writer.writerow(["RELATÓRIO DE RECARGAS POR COLABORADOR"])
        if subtitulo:
            writer.writerow([subtitulo])
        writer.writerow([f"Emitido em {datetime.now():%d/%m/%Y %H:%M}"])

        grupos = _agrupar_por_colaborador(registros)
        for nome, itens in grupos:
            writer.writerow([])
            writer.writerow([_titulo_bloco(nome, itens)])
            writer.writerow(_CABECALHOS)
            for r in itens:
                writer.writerow([
                    r.data.strftime("%d/%m/%Y") if r.data else "",
                    r.sequencia,
                    _formatar_documento(r.documento),
                    r.carga,
                    r.sem_carga,
                    _moeda(r.valor),
                    r.beneficio,
                ])
            subtotal = sum(r.valor for r in itens)
            writer.writerow([
                "", "", "", "",
                f"Subtotal ({len(itens)} item(ns))",
                _moeda(subtotal), "",
            ])

        if len(grupos) > 1:
            total = sum(r.valor for r in registros)
            writer.writerow([])
            writer.writerow([
                "", "", "", "",
                f"Total geral — {len(registros)} item(ns)",
                _moeda(total), "",
            ])
    logger.info("CSV gerado: %s", caminho)
    return caminho
