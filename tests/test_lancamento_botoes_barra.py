# -*- coding: utf-8 -*-
"""Regressão: barra de ações dos lançamentos (Abrir/Sair/Salvar/
Editar/Limpar/Excluir).

Fecha a cobertura dos botões das duas telas de lançamento. A conexão
é feita no _conectar_botoes da LancamentoBase, mas cada filho aponta
para widgets diferentes — um nome errado num hook (_bt_salvar,
_bt_editar etc.) quebra o botão em silêncio.

LIÇÃO: QPushButton.click() em botão DESABILITADO não faz nada (o Qt
descarta o evento). No estado inicial a maioria dos botões está
desabilitada, então o teste de CONEXÃO emite o sinal direto
(clicked.emit()), que independe do estado. Os testes de FLUXO usam
click() de propósito — assim também validam que o botão está
habilitado no estado certo.

Estratégia: o método da base é substituído por um espião ANTES da
instanciação (a conexão captura o bound method no __init__). O
registro é limpo depois de instanciar, porque _inicializar chama
_limpar_campos() — sem isso o teste do Limpar contaria duas chamadas.
"""
import pytest

from app.controllers import (
    lancamento_abastecimento_controller as abast_mod,
)
from app.controllers import lancamento_recargas_controller as recargas_mod
from app.controllers.lancamento_abastecimento_controller import (
    LancamentoAbastecimentoController,
)
from app.controllers.lancamento_base import (
    ESTADO_ABERTA,
    ESTADO_INICIAL,
    ESTADO_NOVO,
    ESTADO_PRONTA,
)
from app.controllers.lancamento_recargas_controller import (
    LancamentoRecargasController,
)


class _ServiceFake:
    """Service mínimo: sem banco, listas vazias."""

    def pesquisar(self, termo=""):
        return []

    def buscar_por_codigo(self, codigo):
        return None


@pytest.fixture
def services_falsos(monkeypatch):
    """Substitui os services dos dois controllers por falsos."""
    monkeypatch.setattr(recargas_mod, "RecargaService", _ServiceFake)
    monkeypatch.setattr(recargas_mod, "ColaboradorService", _ServiceFake)
    monkeypatch.setattr(abast_mod, "AbastecimentoService", _ServiceFake)
    monkeypatch.setattr(abast_mod, "CaminhaoService", _ServiceFake)
    monkeypatch.setattr(abast_mod, "ColaboradorService", _ServiceFake)


# ---------------- conexão de cada botão ao método da base ----------------

@pytest.mark.parametrize("classe,attr_botao,metodo", [
    # recargas
    (LancamentoRecargasController, "bt_Abrir_Recargas",
     "_abrir_lancamento"),
    (LancamentoRecargasController, "bt_Sair_Recarga", "_sair_lancamento"),
    (LancamentoRecargasController, "bt_Salvar", "_salvar"),
    (LancamentoRecargasController, "bt_Editar", "_liberar_edicao"),
    (LancamentoRecargasController, "bt_Limpar", "_limpar_campos"),
    (LancamentoRecargasController, "bt_Excluir", "_excluir"),
    # abastecimento
    (LancamentoAbastecimentoController, "bt_Abrir_Abastecimento",
     "_abrir_lancamento"),
    (LancamentoAbastecimentoController, "bt_Sair_Abastecimento",
     "_sair_lancamento"),
    (LancamentoAbastecimentoController, "bt_Salvar", "_salvar"),
    (LancamentoAbastecimentoController, "bt_Editar", "_liberar_edicao"),
    (LancamentoAbastecimentoController, "bt_Limpar", "_limpar_campos"),
    (LancamentoAbastecimentoController, "bt_Excluir", "_excluir"),
])
def test_botao_da_barra_chama_metodo_da_base(
        qapp, services_falsos, monkeypatch, classe, attr_botao, metodo):
    """O sinal clicked do botão chega ao método correspondente.

    Emite o sinal direto (não click()): no estado inicial o botão
    está desabilitado e o Qt descartaria o clique.
    """
    chamadas = []
    monkeypatch.setattr(classe, metodo,
                        lambda self: chamadas.append(True))

    tela = classe()
    chamadas.clear()          # _inicializar chama _limpar_campos
    getattr(tela.ui, attr_botao).clicked.emit()

    assert chamadas == [True]


# ---------------- fluxo real pelos cliques ----------------

def test_recargas_abrir_e_sair_pelos_botoes(qapp, services_falsos):
    """'+' -> 'Abrir Recarga' -> 'Sair Recarga' percorre os estados."""
    tela = LancamentoRecargasController()

    tela.ui.bt_Novo.click()
    assert tela._modo == ESTADO_NOVO

    tela.ui.bt_Abrir_Recargas.click()
    assert tela._modo == ESTADO_ABERTA
    assert tela.ui.txt_Cod_Colaborador.isEnabled()

    tela.ui.bt_Sair_Recarga.click()
    assert tela._modo == ESTADO_PRONTA
    assert tela.ui.bt_Salvar.isEnabled()
    assert not tela.ui.txt_Cod_Colaborador.isEnabled()


def test_abastecimento_abrir_e_sair_pelos_botoes(qapp, services_falsos):
    """'+' -> 'Abrir' -> 'Sair' percorre os estados."""
    tela = LancamentoAbastecimentoController()

    tela.ui.bt_Novo.click()
    assert tela._modo == ESTADO_NOVO

    tela.ui.bt_Abrir_Abastecimento.click()
    assert tela._modo == ESTADO_ABERTA
    assert tela.ui.txt_Cod_Caminhao.isEnabled()

    tela.ui.bt_Sair_Abastecimento.click()
    assert tela._modo == ESTADO_PRONTA
    assert tela.ui.bt_Salvar.isEnabled()


def test_recargas_limpar_pelos_botoes_volta_ao_inicial(
        qapp, services_falsos):
    """'Limpar' em qualquer estado volta ao inicial."""
    tela = LancamentoRecargasController()
    tela.ui.bt_Novo.click()
    tela.ui.bt_Abrir_Recargas.click()

    tela.ui.bt_Limpar.click()

    assert tela._modo == ESTADO_INICIAL
    assert tela.ui.txt_Recargas.text() == ""
    assert tela._modelo.rowCount() == 0


def test_abastecimento_limpar_pelos_botoes_volta_ao_inicial(
        qapp, services_falsos):
    """'Limpar' em qualquer estado volta ao inicial."""
    tela = LancamentoAbastecimentoController()
    tela.ui.bt_Novo.click()
    tela.ui.bt_Abrir_Abastecimento.click()

    tela.ui.bt_Limpar.click()

    assert tela._modo == ESTADO_INICIAL
    assert tela.ui.txt_Abastecimento.text() == ""
    assert tela._modelo.rowCount() == 0


def test_recargas_salvar_bloqueado_antes_de_sair(qapp, services_falsos):
    """'Salvar' não age com a recarga aberta (fluxo de itens ativo)."""
    tela = LancamentoRecargasController()
    tela.ui.bt_Novo.click()
    tela.ui.bt_Abrir_Recargas.click()

    tela.ui.bt_Salvar.clicked.emit()   # desabilitado: emite direto

    assert tela._modo == ESTADO_ABERTA


def test_recargas_editar_bloqueado_no_inicial(qapp, services_falsos):
    """'Editar' só age a partir da visualização."""
    tela = LancamentoRecargasController()

    tela.ui.bt_Editar.clicked.emit()   # desabilitado: emite direto

    assert tela._modo == ESTADO_INICIAL


def test_recargas_excluir_bloqueado_no_inicial(qapp, services_falsos):
    """'Excluir' só age a partir de pronta/visualização/edição."""
    tela = LancamentoRecargasController()

    tela.ui.bt_Excluir.clicked.emit()  # desabilitado: emite direto

    assert tela._modo == ESTADO_INICIAL
