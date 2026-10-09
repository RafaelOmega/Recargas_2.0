# -*- coding: utf-8 -*-
"""Configuração padrão de QTableView (larguras automáticas)."""
from PySide6.QtWidgets import QHeaderView

LARGURA_MINIMA_PADRAO = 60
LARGURA_MAXIMA_PADRAO = 400


def configurar_tabela(table_view, coluna_stretch=None, ordenavel=False,
                      selecionavel=True,
                      largura_maxima=LARGURA_MAXIMA_PADRAO):
    """Ajusta as colunas pelo conteúdo, com limite por coluna.

    coluna_stretch: índice da coluna que recebe a folga horizontal.
    """
    header = table_view.horizontalHeader()
    header.setMinimumSectionSize(LARGURA_MINIMA_PADRAO)
    table_view.setSortingEnabled(ordenavel)
    if selecionavel:
        table_view.setSelectionBehavior(
            table_view.SelectionBehavior.SelectRows)

    modelo = table_view.model()
    if modelo is None or modelo.columnCount() == 0:
        return

    # 1. largura pelo conteúdo real; 2. limite por coluna;
    # 3. folga vai para a coluna de stretch (se houver).
    for coluna in range(modelo.columnCount()):
        header.setSectionResizeMode(coluna, QHeaderView.ResizeToContents)
        if header.sectionSize(coluna) > largura_maxima:
            header.setSectionResizeMode(coluna, QHeaderView.Interactive)
            header.resizeSection(coluna, largura_maxima)

    if coluna_stretch is not None:
        header.setSectionResizeMode(coluna_stretch, QHeaderView.Stretch)
