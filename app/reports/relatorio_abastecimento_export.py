# -*- coding: utf-8 -*-
"""Exportação do relatório de abastecimento (XLSX e CSV).

A coluna KM/L é gravada como NÚMERO (2 casas), não texto — assim o
Excel consegue somar, ordenar e formatar. Trechos sem litros ficam
vazios em vez de "—", para não poluir a coluna numérica.
"""
import csv

from openpyxl import Workbook
from openpyxl.styles import Font

_CABECALHO = ["Sequência", "Data", "Caminhão", "Modelo", "Placa",
              "Colaborador", "Destino", "KM Início", "KM Final",
              "Litros", "KM/L"]


def _km_l(item):
    """KM/L numérico (2 casas) ou "" quando não há litros."""
    valor = item.km_por_litro
    return "" if valor is None else round(valor, 2)


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
        _km_l(item),
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
