# -*- coding: utf-8 -*-
"""Geração do PDF do relatório de abastecimento por caminhão."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

_AZUL = colors.HexColor("#1F3B5B")
_ZEBRA = colors.HexColor("#F2F5F8")
_SUBTOTAL = colors.HexColor("#E8EDF2")
_TOTAL = colors.HexColor("#DCE4EE")


def _blocos(itens):
    """Agrupa os itens por caminhão (ordem já vem ordenada)."""
    blocos = []
    atual = None
    atual_itens = []
    for item in itens:
        if atual is not None and item.caminhao_codigo != atual:
            blocos.append((atual, atual_itens))
            atual_itens = []
        atual = item.caminhao_codigo
        atual_itens.append(item)
    if atual_itens:
        blocos.append((atual, atual_itens))
    return blocos


def _km_l(item) -> str:
    """KM/L do item formatado, ou '—' quando não há litros."""
    valor = item.km_por_litro
    return "—" if valor is None else f"{valor:.2f}"


def _km_l_ponderado(km: int, litros: float) -> str:
    """KM/L do conjunto: km total / litros totais."""
    if litros <= 0:
        return "—"
    return f"{km / litros:.2f}"


def gerar_pdf_abastecimento(itens, caminho,
                            titulo="Relatório de Abastecimento"):
    doc = SimpleDocTemplate(
        caminho, pagesize=landscape(A4),
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm)
    story = [Paragraph(titulo, _estilo_titulo())]
    story.append(Spacer(1, 4 * mm))

    total_geral = 0.0
    total_km = 0
    for codigo, itens_bloco in _blocos(itens):
        primeiro = itens_bloco[0]
        cab = (f"{primeiro.caminhao_codigo} · "
               f"{primeiro.caminhao_modelo} · {primeiro.placa}")
        story.append(Paragraph(cab, _estilo_cab()))
        story.append(Spacer(1, 2 * mm))

        dados = [["Seq.", "Data", "Colaborador", "Destino",
                  "KM Início", "KM Final", "Litros", "KM/L"]]
        for i in itens_bloco:
            dados.append([
                str(i.sequencia),
                i.data.strftime("%d/%m/%Y") if i.data else "",
                i.colaborador_nome,
                i.destino,
                str(i.km_inicio),
                str(i.km_final),
                f"{i.litros:.2f}",
                _km_l(i),
            ])
        subtotal = sum(i.litros for i in itens_bloco)
        km_bloco = sum(i.km_rodados for i in itens_bloco)
        total_geral += subtotal
        total_km += km_bloco
        dados.append(["", "", "", "", "", "SUBTOTAL",
                      f"{subtotal:.2f}",
                      _km_l_ponderado(km_bloco, subtotal)])

        tabela = Table(dados, repeatRows=1)
        tabela.setStyle(_estilo_tabela())
        story.append(tabela)
        story.append(Spacer(1, 4 * mm))

    if len(_blocos(itens)) > 1:
        total = Table([["TOTAL GERAL", f"{total_geral:.2f}",
                        _km_l_ponderado(total_km, total_geral)]])
        total.setStyle(_estilo_total())
        story.append(total)

    doc.build(story)


def _estilo_titulo():
    from reportlab.lib.styles import ParagraphStyle
    return ParagraphStyle("titulo", fontName="Helvetica-Bold",
                          fontSize=16, textColor=_AZUL, spaceAfter=4)


def _estilo_cab():
    from reportlab.lib.styles import ParagraphStyle
    return ParagraphStyle("cab", fontName="Helvetica-Bold",
                          fontSize=11, textColor=colors.white)


def _estilo_tabela():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _AZUL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, _ZEBRA]),
        ("BACKGROUND", (0, -1), (-1, -1), _SUBTOTAL),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D3DE")),
        ("ALIGN", (4, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])


def _estilo_total():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _TOTAL),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D3DE")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ])
