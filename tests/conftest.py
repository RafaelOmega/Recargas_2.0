# -*- coding: utf-8 -*-
"""Fixtures compartilhadas dos testes.

Os testes NÃO tocam no banco: os services são substituídos por falsos
(mesma interface, dados em memória) e as caixas de mensagem
(QMessageBox) são interceptadas para não bloquear a execução.
"""
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QMessageBox

# garante que a raiz do projeto está no sys.path (import app.*)
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


class _Caixas:
    """Registro das caixas de mensagem exibidas durante o teste."""

    def __init__(self):
        self.registro = []          # lista de (tipo, texto)
        self.resposta_question = QMessageBox.StandardButton.Yes

    def do_tipo(self, tipo):
        return [texto for (t, texto) in self.registro if t == tipo]

    def alguma(self, trecho):
        return any(trecho in texto for (_, texto) in self.registro)


@pytest.fixture
def caixas(monkeypatch):
    """Intercepta QMessageBox.information/warning/critical/question.

    Em vez de abrir janela (o que travaria o teste), registra a
    chamada e devolve resposta padrão; question devolve
    caixas.resposta_question (mutável durante o teste para simular
    o Sim/Não do usuário).
    """
    caixas = _Caixas()

    def _fabricar(tipo, resposta_padrao):
        def _mostrar(*args, **kwargs):
            # assinatura estática: (parent, titulo, texto, ...)
            texto = args[2] if len(args) >= 3 else ""
            caixas.registro.append((tipo, texto))
            return (caixas.resposta_question if tipo == "question"
                    else resposta_padrao)
        return _mostrar

    monkeypatch.setattr(QMessageBox, "information",
                        _fabricar("information",
                                  QMessageBox.StandardButton.Ok))
    monkeypatch.setattr(QMessageBox, "warning",
                        _fabricar("warning",
                                  QMessageBox.StandardButton.Ok))
    monkeypatch.setattr(QMessageBox, "critical",
                        _fabricar("critical",
                                  QMessageBox.StandardButton.Ok))
    monkeypatch.setattr(QMessageBox, "question",
                        _fabricar("question",
                                  QMessageBox.StandardButton.Yes))
    return caixas
