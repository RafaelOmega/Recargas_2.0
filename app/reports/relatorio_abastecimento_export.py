# -*- coding: utf-8 -*-
"""Exportação do relatório de abastecimento (XLSX e CSV)."""
import csv

from openpyxl import Workbook
from openpyxl.styles import Font

_CABECALHO = ["Sequência", "Data", "Caminhão", "Modelo", "Placa",
              "Colaborador", "Destino", "KM Início", "KM Final",
              "Litros"]


def _linha(item):
    return [
        item.sequencia,
        item.data.strftime("%d/%m/%Y") if item.data else "",
        item.caminhao_codigo,
        item.caminhao_modelo,
        item.placa,
        item.colaborador_nome,
        item.destino,
        item.km_inicio,
        item.km_final,
        item.litros,
    ]


def exportar_xlsx_abastecimento(itens, caminho):
    wb = Workbook()
    ws = wb.active
    ws.title = "Abastecimento"
    ws.append(_CABECALHO)
    for c in range(1, len(_CABECALHO) + 1):
        ws.cell(row=1, column=c).font = Font(bold=True)
    for item in itens:
        ws.append(_linha(item))
    wb.save(caminho)


def exportar_csv_abastecimento(itens, caminho):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(_CABECALHO)
        for item in itens:
            writer.writerow(_linha(item))
