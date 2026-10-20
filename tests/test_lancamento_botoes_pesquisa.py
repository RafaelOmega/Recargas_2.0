# -*- coding: utf-8 -*-
"""Regressão: botões de vínculo, de sequência e de novo.

Bug corrigido em 2.6.1: a refatoração para LancamentoBase perdeu o
.clicked dos botões "..." de vínculo — o clique não fazia nada. Esses
botões não fazem parte do contrato da base, então cada filho precisa
reconectá-los no _conectar_especifico.

Cobertura dos botões:
  - "..." do vínculo (colaborador / caminhão) -> _pesquisar_*
  - "..." da sequência -> _pesquisar (abre a pesquisa do registro)
  - "+" (novo) -> _novo

LIÇÃO: QPushButton.click() em botão DESABILITADO não faz nada. O "..."
do vínculo só é habilitado com o lançamento aberto, então o teste de
CONEXÃO emite o sinal direto (clicked.emit()); o teste de FLUXO usa
click() depois de abrir, validando também o estado habilitado.

Os controllers são instanciados de verdade (UI gerada + widgets
reais), mas os services são substituídos por falsos em memória —
nenhuma conexão com o banco. _abrir_pesquisa é substituído por um
espião para não abrir diálogo modal (travaria em headless).
"""
from datetime import date, datetime

import pytest

from app.controllers import (
    lancamento_abastecimento_controller as abast_mod,
)
from app.controllers import lancamento_recargas_controller as recargas_mod
from app.controllers.lancamento_abastecimento_controller import (
    LancamentoAbastecimentoController,
)
from app.controllers.lancamento_base import (
    ESTADO_INICIAL,
    ESTADO_NOVO,
    ESTADO_VISUALIZACAO,
)
from app.controllers.lancamento_recargas_controller import (
    LancamentoRecargasController,
)


# ---------------- falsos ----------------

class _ServiceFake:
    """Service mínimo: sem banco, listas vazias."""

    def pesquisar(self, termo=""):
        return []

    def buscar_por_codigo(self, codigo):
        return None


class _ItemRecargaFake:
    def __init__(self, nome="Ana", documento="12345678900",
                 carga="10", sem_carga="2", valor=50.0):
        self.nome = nome
        self.documento = documento
        self.carga = carga
        self.sem_carga = sem_carga
        self.valor = valor


class _RecargaFake:
    def __init__(self, sequencia=7, data=None, itens=None,
                 atualizado_em=None):
        self.sequencia = sequencia
        self.data = data or date(2026, 10, 20)
        self.itens = itens if itens is not None else [_ItemRecargaFake()]
        self.atualizado_em = atualizado_em or datetime(
            2026, 10, 20, 12, 0, 0)


class _ItemAbastecimentoFake:
    def __init__(self, caminhao_codigo="C1", caminhao_modelo="Volvo",
                 colaborador_nome="Ana", colaborador_codigo="9",
                 destino="Centro", km_inicio=100, km_final=200,
                 litros=150.0):
        self.caminhao_codigo = caminhao_codigo
        self.caminhao_modelo = caminhao_modelo
        self.colaborador_nome = colaborador_nome
        self.colaborador_codigo = colaborador_codigo
        self.destino = destino
        self.km_inicio = km_inicio
        self.km_final = km_final
        self.litros = litros


class _AbastecimentoFake:
    def __init__(self, sequencia=5, data=None, itens=None,
                 atualizado_em=None):
        self.sequencia = sequencia
        self.data = data or date(2026, 10, 20)
        self.itens = (itens if itens is not None
                      else [_ItemAbastecimentoFake()])
        self.atualizado_em = atualizado_em or datetime(
            2026, 10, 20, 12, 0, 0)


# ---------------- fixtures ----------------

@pytest.fixture
def services_falsos(monkeypatch):
    """Substitui os services dos dois controllers por falsos.

    Os módulos importam os services com try/except e guardam o nome no
    módulo; trocar o atributo do módulo é o suficiente.
    """
    monkeypatch.setattr(recargas_mod, "RecargaService", _ServiceFake)
    monkeypatch.setattr(recargas_mod, "ColaboradorService", _ServiceFake)
    monkeypatch.setattr(abast_mod, "AbastecimentoService", _ServiceFake)
    monkeypatch.setattr(abast_mod, "CaminhaoService", _ServiceFake)
    monkeypatch.setattr(abast_mod, "ColaboradorService", _ServiceFake)


# ---------------- recargas: "..." do colaborador ----------------

def test_recargas_botao_pesquisar_colaborador_abre_pesquisa(
        qapp, services_falsos, monkeypatch):
    """O sinal clicked do "..." chama _pesquisar_colaborador.

    Emite o sinal direto: o botão só é habilitado com a recarga aberta.
    """
    chamadas = []
    monkeypatch.setattr(
        LancamentoRecargasController, "_pesquisar_colaborador",
        lambda self: chamadas.append(True))

    tela = LancamentoRecargasController()
    tela.ui.bt_Pesquisar_Colaborador.clicked.emit()

    assert chamadas == [True]


def test_recargas_botao_pesquisar_colaborador_habilitado_ao_abrir(
        qapp, services_falsos):
    """Com a recarga aberta o "..." fica ativo (faz parte do item)."""
    tela = LancamentoRecargasController()
    tela._novo()
    tela._abrir_lancamento()

    assert tela.ui.bt_Pesquisar_Colaborador.isEnabled()


# ---------------- recargas: "+" e "..." da sequência ----------------

def test_recargas_botao_novo_prepara_recarga(qapp, services_falsos):
    """Clique no "+" (bt_Novo) entra no estado novo."""
    tela = LancamentoRecargasController()
    assert tela._modo == ESTADO_INICIAL

    tela.ui.bt_Novo.click()

    assert tela._modo == ESTADO_NOVO
    assert tela.ui.dt_Data.isEnabled()
    assert tela.ui.bt_Abrir_Recargas.isEnabled()


def test_recargas_botao_pesquisar_sequencia_sem_selecao(
        qapp, services_falsos, monkeypatch):
    """Clique no "..." da sequência sem escolher nada não muda a tela."""
    monkeypatch.setattr(
        LancamentoRecargasController, "_abrir_pesquisa",
        lambda self: None)

    tela = LancamentoRecargasController()
    tela.ui.bt_Pesquisar_Recargas.click()

    assert tela._modo == ESTADO_INICIAL
    assert tela._modelo.rowCount() == 0


def test_recargas_botao_pesquisar_sequencia_carrega_registro(
        qapp, services_falsos, monkeypatch):
    """Clique no "..." da sequência carrega a recarga escolhida."""
    recarga = _RecargaFake(sequencia=7)
    monkeypatch.setattr(
        LancamentoRecargasController, "_abrir_pesquisa",
        lambda self: recarga)

    tela = LancamentoRecargasController()
    tela.ui.bt_Pesquisar_Recargas.click()

    assert tela._modo == ESTADO_VISUALIZACAO
    assert tela.ui.txt_Recargas.text() == "7"
    assert tela._modelo.rowCount() == 1
    assert tela._modelo.item(0, 0).text() == "Ana"


# ---------------- abastecimento: "..." dos vínculos ----------------

def test_abastecimento_botao_pesquisar_caminhao_abre_pesquisa(
        qapp, services_falsos, monkeypatch):
    """O sinal clicked do "..." chama _pesquisar_caminhao."""
    chamadas = []
    monkeypatch.setattr(
        LancamentoAbastecimentoController, "_pesquisar_caminhao",
        lambda self: chamadas.append(True))

    tela = LancamentoAbastecimentoController()
    tela.ui.bt_Pesquisar_Caminhao.clicked.emit()

    assert chamadas == [True]


def test_abastecimento_botao_pesquisar_colaborador_abre_pesquisa(
        qapp, services_falsos, monkeypatch):
    """O sinal clicked do "..." chama _pesquisar_colaborador."""
    chamadas = []
    monkeypatch.setattr(
        LancamentoAbastecimentoController, "_pesquisar_colaborador",
        lambda self: chamadas.append(True))

    tela = LancamentoAbastecimentoController()
    tela.ui.bt_Pesquisar_Colaborador.clicked.emit()

    assert chamadas == [True]


def test_abastecimento_botoes_pesquisar_habilitados_ao_abrir(
        qapp, services_falsos):
    """Com o abastecimento aberto os dois "..." ficam ativos."""
    tela = LancamentoAbastecimentoController()
    tela._novo()
    tela._abrir_lancamento()

    assert tela.ui.bt_Pesquisar_Caminhao.isEnabled()
    assert tela.ui.bt_Pesquisar_Colaborador.isEnabled()


# ---------------- abastecimento: "+" e "..." da sequência ----------------

def test_abastecimento_botao_novo_prepara_abastecimento(
        qapp, services_falsos):
    """Clique no "+" (bt_Novo) entra no estado novo."""
    tela = LancamentoAbastecimentoController()
    assert tela._modo == ESTADO_INICIAL

    tela.ui.bt_Novo.click()

    assert tela._modo == ESTADO_NOVO
    assert tela.ui.dt_Data.isEnabled()
    assert tela.ui.bt_Abrir_Abastecimento.isEnabled()


def test_abastecimento_botao_pesquisar_sequencia_carrega_registro(
        qapp, services_falsos, monkeypatch):
    """Clique no "..." da sequência carrega o abastecimento escolhido."""
    abastecimento = _AbastecimentoFake(sequencia=5)
    monkeypatch.setattr(
        LancamentoAbastecimentoController, "_abrir_pesquisa",
        lambda self: abastecimento)

    tela = LancamentoAbastecimentoController()
    tela.ui.bt_Pesquisar_Abastecimentos.click()

    assert tela._modo == ESTADO_VISUALIZACAO
    assert tela.ui.txt_Abastecimento.text() == "5"
    assert tela._modelo.rowCount() == 1
    assert tela._modelo.item(0, 0).text() == "C1"
