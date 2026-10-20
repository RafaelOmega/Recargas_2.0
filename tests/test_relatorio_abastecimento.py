# -*- coding: utf-8 -*-
"""Regressão: tela de Relatório de Abastecimento.

Bug corrigido em 2.7.1: o controller foi entregue referenciando
widgets que não existem na UI (bt_Pesquisar / bt_Gerar / txt_Pesquisa
em vez de bt_Pesquisar_Abastecimento / bt_Filtrar / txt_PLaca). O CI
ficou verde porque nenhum teste instanciava a tela — o AttributeError
só aparecia em execução.

Estes testes instanciam o controller de verdade (Ui_Rel_Abastecimento
+ widgets reais), com o service substituído por um falso em memória —
nenhuma conexão com o banco. Assim, qualquer widget inexistente ou
renomeado no .ui quebra o CI na hora.

Também cobrem o preview (HTML em blocos por caminhão, com subtotal e
total geral), que é construído em código e não tem .ui para validar.
"""
from datetime import date

import pytest

from app.controllers import relatorio_abastecimento_controller as mod
from app.controllers.relatorio_abastecimento_controller import (
    RelatorioAbastecimentoController,
)
from app.controllers.relatorio_abastecimento_preview_controller import (
    RelatorioAbastecimentoPreviewController,
)
from app.models.relatorio_abastecimento import ItemAbastecimentoRelatorio


# ---------------- falsos ----------------

class _ServiceFake:
    """Service mínimo: sem banco, devolve o que for configurado."""

    def __init__(self, itens=None):
        self.itens = itens if itens is not None else []
        self.chamadas = []

    def itens_por_caminhao(self, caminhao="", data_inicial=None,
                           data_final=None):
        self.chamadas.append((caminhao, data_inicial, data_final))
        return self.itens


class _PreviewFake:
    """Substitui o QDialog do preview (não abre janela no CI)."""

    instancias = []

    def __init__(self, itens, parent=None):
        self.itens = itens
        self.parent = parent
        _PreviewFake.instancias.append(itens)

    def exec(self):
        return 1


def _item(sequencia=1, caminhao_codigo="C1", caminhao_modelo="Volvo",
          placa="ABC1D23", colaborador_nome="Ana", destino="Centro",
          km_inicio=100, km_final=200, litros=150.0,
          data=date(2026, 10, 20)) -> ItemAbastecimentoRelatorio:
    return ItemAbastecimentoRelatorio(
        sequencia=sequencia, data=data,
        caminhao_codigo=caminhao_codigo, caminhao_modelo=caminhao_modelo,
        placa=placa, colaborador_nome=colaborador_nome,
        destino=destino, km_inicio=km_inicio, km_final=km_final,
        litros=litros)


# ---------------- fixtures ----------------

@pytest.fixture
def service_falso(monkeypatch):
    """Substitui o service ANTES da instanciação (evita o banco)."""
    fake = _ServiceFake()
    monkeypatch.setattr(mod, "RelatorioAbastecimentoService",
                        lambda: fake)
    return fake


@pytest.fixture
def preview_falso(monkeypatch):
    """Substitui o preview para não abrir diálogo modal."""
    _PreviewFake.instancias = []
    monkeypatch.setattr(mod, "RelatorioAbastecimentoPreviewController",
                        _PreviewFake)
    return _PreviewFake.instancias


@pytest.fixture
def tela(qapp, service_falso):
    """Tela de relatório instanciada de verdade."""
    return RelatorioAbastecimentoController()


# ---------------- instanciação (o teste que pega o bug) ----------------

def test_tela_instancia_sem_erro(tela):
    """Instanciar a tela não pode levantar AttributeError.

    Se o controller referenciar um widget inexistente na UI, este
    teste falha — é a regressão do commit anterior.
    """
    assert tela is not None
    assert tela.ui is not None


def test_widgets_referenciados_existem(tela):
    """Todo widget usado pelo controller existe na UI gerada."""
    for nome in ("dt_Data_Inicial", "dt_Data_Final", "txt_PLaca",
                 "bt_Pesquisar_Abastecimento", "bt_Filtrar"):
        assert hasattr(tela.ui, nome), f"Widget ausente na UI: {nome}"


def test_periodo_padrao_e_mes_corrente(tela):
    """Padrão: primeiro dia do mês corrente até hoje."""
    from PySide6.QtCore import QDate

    hoje = QDate.currentDate()
    assert tela.ui.dt_Data_Inicial.date() == QDate(hoje.year(),
                                                   hoje.month(), 1)
    assert tela.ui.dt_Data_Final.date() == hoje


# ---------------- conexões dos botões ----------------

def test_botao_pesquisar_chama_pesquisa_de_caminhao(
        tela, monkeypatch):
    """O sinal clicked do '...' chega a _pesquisar_caminhao."""
    chamadas = []
    monkeypatch.setattr(
        RelatorioAbastecimentoController, "_pesquisar_caminhao",
        lambda self: chamadas.append(True))

    tela.ui.bt_Pesquisar_Abastecimento.clicked.emit()

    assert chamadas == [True]


def test_botao_filtrar_chama_gerar(tela, monkeypatch):
    """O sinal clicked do Filtrar chega a _gerar."""
    chamadas = []
    monkeypatch.setattr(
        RelatorioAbastecimentoController, "_gerar",
        lambda self: chamadas.append(True))

    tela.ui.bt_Filtrar.clicked.emit()

    assert chamadas == [True]


# ---------------- geração ----------------

def test_gerar_valida_periodo(tela, caixas):
    """Data inicial maior que a final avisa e não consulta."""
    from PySide6.QtCore import QDate

    tela.ui.dt_Data_Inicial.setDate(QDate(2026, 10, 20))
    tela.ui.dt_Data_Final.setDate(QDate(2026, 10, 1))

    tela._gerar()

    assert caixas.alguma("maior")
    assert tela._service.chamadas == []


def test_gerar_sem_registros_avisa(tela, caixas):
    """Sem resultados, informa e não abre o preview."""
    tela._gerar()

    assert caixas.alguma("Nenhum abastecimento")
    assert _PreviewFake.instancias == []


def test_gerar_passa_placa_e_periodo(tela, service_falso,
                                     preview_falso):
    """A placa digitada e o período chegam ao service."""
    service_falso.itens = [_item()]
    tela.ui.txt_PLaca.setText("ABC1D23")

    tela._gerar()

    assert len(service_falso.chamadas) == 1
    placa, inicial, final = service_falso.chamadas[0]
    assert placa == "ABC1D23"
    assert inicial == tela.ui.dt_Data_Inicial.date().toPython()
    assert final == tela.ui.dt_Data_Final.date().toPython()


def test_gerar_abre_preview_com_os_itens(tela, service_falso,
                                         preview_falso):
    """Com resultados, o preview recebe a lista retornada."""
    itens = [_item(sequencia=1), _item(sequencia=2)]
    service_falso.itens = itens

    tela._gerar()

    assert len(preview_falso) == 1
    assert preview_falso[0] == itens


# ---------------- preview (HTML em blocos) ----------------

def test_preview_monta_html_com_placa_e_subtotal(qapp):
    """O HTML mostra a placa do caminhão e o subtotal do bloco."""
    itens = [_item(litros=100.0), _item(sequencia=2, litros=50.0)]

    preview = RelatorioAbastecimentoPreviewController(itens)
    html = preview._montar_html()

    assert "ABC1D23" in html
    assert "150.00" in html          # subtotal do bloco
    assert "SUBTOTAL" in html


def test_preview_total_geral_so_com_dois_blocos(qapp):
    """TOTAL GERAL aparece apenas com 2+ caminhões."""
    um_bloco = [_item()]
    html_um = RelatorioAbastecimentoPreviewController(
        um_bloco)._montar_html()
    assert "TOTAL GERAL" not in html_um

    dois_blocos = [_item(caminhao_codigo="C1"),
                   _item(caminhao_codigo="C2", placa="XYZ9K88")]
    html_dois = RelatorioAbastecimentoPreviewController(
        dois_blocos)._montar_html()
    assert "TOTAL GERAL" in html_dois
