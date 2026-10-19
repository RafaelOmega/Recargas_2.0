# -*- coding: utf-8 -*-
"""Testes da LancamentoBase (esqueleto comum dos lançamentos).

Os testes NÃO tocam no banco: o service é substituído por um falso
(mesma interface, dados em memória, devolve CÓPIAS — imitando o
repository real) e as caixas de mensagem são interceptadas (fixture
caixas do conftest). Teclas/atalhos são disparados pelos SINAIS
(returnPressed.emit, activated.emit) — determinístico em CI.

A tela de teste (TelaFake) é construída em código, com o contrato
mínimo da base: sequência, data, grade de 2 colunas (Destino, Valor)
e um item com destino + valor.
"""
from datetime import date, datetime

from PySide6.QtCore import QDate
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import (QDateEdit, QDoubleSpinBox, QLineEdit,
                               QMessageBox, QPushButton, QTableView)

from app.controllers.lancamento_base import (
    ESTADO_ABERTA,
    ESTADO_EDICAO,
    ESTADO_INICIAL,
    ESTADO_NOVO,
    ESTADO_PRONTA,
    ESTADO_VISUALIZACAO,
    LancamentoBase,
)


# ---------------- falsos (imitam o repository real) ----------------

class RegistroFake:
    """Registro de domínio mínimo (cabeçalho + itens)."""

    def __init__(self, sequencia=None, data=None, itens=None,
                 atualizado_em=None):
        self.sequencia = sequencia
        self.data = data or date.today()
        self.itens = itens or []
        self.atualizado_em = atualizado_em


class ServiceFake:
    """Mesma interface do repository; devolve CÓPIAS (nunca a
    instância viva — senão o conflito nunca dispara)."""

    def __init__(self):
        self.registros = {}
        self._proxima = 1
        self.chamadas = []

    def salvar(self, dados):
        self.chamadas.append(("salvar", dict(dados)))
        registro = RegistroFake(
            sequencia=self._proxima,
            data=dados["data"],
            itens=[dict(i) for i in dados["itens"]],
            atualizado_em=datetime(2026, 10, 19, 12, 0, 0),
        )
        self.registros[registro.sequencia] = registro
        self._proxima += 1
        return self._copiar(registro)

    def atualizar(self, dados):
        self.chamadas.append(("atualizar", dict(dados)))
        atual = self.registros.get(dados["sequencia"])
        if atual is None:
            return False
        if atual.atualizado_em != dados.get("atualizado_em"):
            from app.utils.erros import ConflitoEdicaoError
            raise ConflitoEdicaoError("alterado por outro usuário")
        atual.data = dados["data"]
        atual.itens = [dict(i) for i in dados["itens"]]
        atual.atualizado_em = datetime(2026, 10, 19, 13, 0, 0)
        return True

    def excluir(self, sequencia):
        self.chamadas.append(("excluir", sequencia))
        return self.registros.pop(sequencia, None) is not None

    def buscar_por_sequencia(self, sequencia):
        registro = self.registros.get(sequencia)
        return self._copiar(registro) if registro else None

    @staticmethod
    def _copiar(registro):
        return RegistroFake(
            sequencia=registro.sequencia,
            data=registro.data,
            itens=[dict(i) for i in registro.itens],
            atualizado_em=registro.atualizado_em,
        )


# ---------------- tela de teste (contrato mínimo) ----------------

class TelaFake(LancamentoBase):

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service
        self._registro_pesquisa = None

        self.txt_Sequencia = QLineEdit(self)
        self.dt_Data = QDateEdit(self)
        self.tb_Itens = QTableView(self)
        self.txt_Total = QLineEdit(self)
        self.bt_Novo = QPushButton(self)
        self.bt_Pesquisar = QPushButton(self)
        self.bt_Abrir = QPushButton(self)
        self.bt_Sair = QPushButton(self)
        self.bt_Confirmar_Item = QPushButton(self)
        self.bt_Limpar_Item = QPushButton(self)
        self.bt_Excluir_Item = QPushButton(self)
        self.bt_Salvar = QPushButton(self)
        self.bt_Editar = QPushButton(self)
        self.bt_Limpar = QPushButton(self)
        self.bt_Excluir = QPushButton(self)
        self.txt_Destino = QLineEdit(self)
        self.dbs_Valor = QDoubleSpinBox(self)
        self.dbs_Valor.setDecimals(2)

        self._inicializar()

    # ---- hooks de widgets ----

    def _w_sequencia(self):
        return self.txt_Sequencia

    def _w_data(self):
        return self.dt_Data

    def _w_grade(self):
        return self.tb_Itens

    def _w_total(self):
        return self.txt_Total

    def _bt_novo(self):
        return self.bt_Novo

    def _bt_pesquisar(self):
        return self.bt_Pesquisar

    def _bt_abrir(self):
        return self.bt_Abrir

    def _bt_sair(self):
        return self.bt_Sair

    def _bt_confirmar_item(self):
        return self.bt_Confirmar_Item

    def _bt_limpar_item(self):
        return self.bt_Limpar_Item

    def _bt_excluir_item(self):
        return self.bt_Excluir_Item

    def _bt_salvar(self):
        return self.bt_Salvar

    def _bt_editar(self):
        return self.bt_Editar

    def _bt_limpar(self):
        return self.bt_Limpar

    def _bt_excluir(self):
        return self.bt_Excluir

    # ---- contrato ----

    def _colunas_grade(self):
        return ["Destino", "Valor"]

    def _coluna_valor(self):
        return 1

    def _area_itens(self, habilitar):
        self.txt_Destino.setEnabled(habilitar)
        self.dbs_Valor.setEnabled(habilitar)
        self.bt_Confirmar_Item.setEnabled(habilitar)
        self.bt_Limpar_Item.setEnabled(habilitar)
        self.bt_Excluir_Item.setEnabled(habilitar)
        self.bt_Sair.setEnabled(habilitar)

    def _definir_tab_order(self):
        pass

    def _foco_apos_abrir(self):
        self.txt_Destino.setFocus()

    def _foco_primeiro_item(self):
        self.txt_Destino.setFocus()

    def _validar_item(self):
        if not self.txt_Destino.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o destino.")
            return False
        if self.dbs_Valor.value() <= 0:
            QMessageBox.warning(self, "Atenção",
                                "Informe um valor maior que zero.")
            return False
        return True

    def _linha_item(self):
        return [
            QStandardItem(self.txt_Destino.text().strip()),
            QStandardItem(self._formatar_valor(self.dbs_Valor.value())),
        ]

    def _carregar_item_campos(self, linha):
        self.txt_Destino.setText(self._modelo.item(linha, 0).text())
        self.dbs_Valor.setValue(
            self._valor_para_float(self._modelo.item(linha, 1).text()))

    def _limpar_item_campos(self):
        self.txt_Destino.clear()
        self.dbs_Valor.setValue(0.0)

    def _foco_apos_item(self):
        self.txt_Destino.setFocus()

    def _abrir_pesquisa(self):
        return self._registro_pesquisa

    def _popular_grade(self, registro):
        for item in registro.itens:
            self._modelo.appendRow([
                QStandardItem(item["destino"]),
                QStandardItem(self._formatar_valor(item["valor"])),
            ])

    def _coletar_itens(self):
        itens = []
        for linha in range(self._modelo.rowCount()):
            itens.append({
                "destino": self._modelo.item(linha, 0).text(),
                "valor": self._valor_para_float(
                    self._modelo.item(linha, 1).text()),
            })
        return itens

    def _nome_registro(self):
        return "registro"

    def _msg_duplicidade(self):
        return "Já existe um registro com essa sequência."


# ---------------- auxiliares ----------------

def _carregar(tela, service, sequencia=1):
    registro = service.buscar_por_sequencia(sequencia)
    tela._preencher(registro)
    return registro


def _item_na_grade(tela, destino="Centro", valor=10.0):
    tela.txt_Destino.setText(destino)
    tela.dbs_Valor.setValue(valor)
    tela._confirmar_item()


def _fluxo_edicao(tela):
    """Carregado -> Editar -> Abrir -> Sair (salvar liberado)."""
    tela._liberar_edicao()
    tela._abrir_lancamento()
    tela._sair_lancamento()


# ---------------- testes: estados ----------------

def test_estado_inicial(tela):
    assert tela._w_sequencia().isEnabled()
    assert tela._bt_novo().isEnabled()
    assert not tela._w_data().isEnabled()
    assert not tela._bt_abrir().isEnabled()
    assert not tela.txt_Destino.isEnabled()
    assert not tela._bt_salvar().isEnabled()
    assert not tela._bt_editar().isEnabled()
    assert not tela._bt_excluir().isEnabled()
    assert not tela._bt_limpar().isEnabled()


def test_novo_libera_data_e_abrir(tela):
    tela._novo()
    assert tela._modo == ESTADO_NOVO
    assert not tela._w_sequencia().isEnabled()
    assert tela._w_data().isEnabled()
    assert tela._bt_abrir().isEnabled()
    assert tela._bt_limpar().isEnabled()
    assert not tela._bt_salvar().isEnabled()


def test_novo_somente_do_estado_inicial(tela, service):
    tela._novo()
    tela._abrir_lancamento()
    tela._novo()
    assert tela._modo == ESTADO_ABERTA
    assert service.chamadas == []


def test_f2_abre_novo(tela):
    tela._at_f2.activated.emit()
    assert tela._modo == ESTADO_NOVO


def test_limpar_volta_ao_inicial(tela):
    tela._novo()
    tela._limpar_campos()
    assert tela._modo == ESTADO_INICIAL


def test_liberar_edicao_somente_da_visualizacao(tela, service):
    tela._novo()
    tela._liberar_edicao()
    assert tela._modo == ESTADO_NOVO
    _carregar(tela, service)
    tela._liberar_edicao()
    assert tela._modo == ESTADO_EDICAO


# ---------------- testes: busca por sequência ----------------

def test_enter_com_sequencia_busca_direto(tela, service):
    service.registros[7] = RegistroFake(
        sequencia=7, itens=[{"destino": "A", "valor": 5.0}])
    tela._w_sequencia().setText("7")
    tela._w_sequencia().returnPressed.emit()
    assert tela._modo == ESTADO_VISUALIZACAO
    assert tela._modelo.rowCount() == 1


def test_enter_vazio_abre_pesquisa(tela):
    tela._registro_pesquisa = RegistroFake(
        sequencia=3, itens=[{"destino": "X", "valor": 2.0}])
    tela._w_sequencia().returnPressed.emit()
    assert tela._w_sequencia().text() == "3"
    assert tela._modo == ESTADO_VISUALIZACAO


def test_sequencia_inexistente_avisa(tela, service, caixas):
    tela._w_sequencia().setText("99")
    tela._w_sequencia().returnPressed.emit()
    assert caixas.alguma("não encontrado")
    assert tela._modo == ESTADO_INICIAL


def test_sequencia_nao_numerica_avisa(tela, caixas):
    tela._w_sequencia().setText("abc")
    tela._w_sequencia().returnPressed.emit()
    assert caixas.alguma("sequência numérica")


# ---------------- testes: fluxo de itens ----------------

def test_abrir_e_sair_controlam_fluxo(tela):
    tela._novo()
    tela._abrir_lancamento()
    assert tela._modo == ESTADO_ABERTA
    assert tela.txt_Destino.isEnabled()
    assert not tela._bt_salvar().isEnabled()  # bloqueado enquanto aberta
    _item_na_grade(tela)
    tela._sair_lancamento()
    assert tela._modo == ESTADO_PRONTA
    assert tela._bt_salvar().isEnabled()
    assert not tela.txt_Destino.isEnabled()


def test_confirmar_item_adiciona_linha(tela):
    tela._novo()
    tela._abrir_lancamento()
    _item_na_grade(tela, "Centro", 10.0)
    assert tela._modelo.rowCount() == 1
    assert tela._modelo.item(0, 0).text() == "Centro"
    assert tela._w_total().text() == "10,00"


def test_confirmar_item_invalido_bloqueia(tela, caixas):
    tela._novo()
    tela._abrir_lancamento()
    tela._confirmar_item()
    assert tela._modelo.rowCount() == 0
    assert caixas.alguma("destino")


def test_duplo_clique_recarrega_e_atualiza(tela):
    tela._novo()
    tela._abrir_lancamento()
    _item_na_grade(tela, "Centro", 10.0)
    tela._w_grade().doubleClicked.emit(tela._modelo.index(0, 0))
    assert tela.txt_Destino.text() == "Centro"
    assert tela.dbs_Valor.value() == 10.0
    # confirmar atualiza, não duplica
    tela.txt_Destino.setText("Rodovia")
    tela._confirmar_item()
    assert tela._modelo.rowCount() == 1
    assert tela._modelo.item(0, 0).text() == "Rodovia"


def test_enter_na_grade_recarrega_item(tela):
    tela._novo()
    tela._abrir_lancamento()
    _item_na_grade(tela, "Centro", 10.0)
    tela._w_grade().selectRow(0)
    tela._at_enter_grade.activated.emit()
    assert tela.txt_Destino.text() == "Centro"


def test_excluir_item_remove_linha(tela):
    tela._novo()
    tela._abrir_lancamento()
    _item_na_grade(tela, "Centro", 10.0)
    _item_na_grade(tela, "Rodovia", 5.0)
    tela._w_grade().selectRow(1)
    tela._excluir_item()
    assert tela._modelo.rowCount() == 1
    assert tela._modelo.item(0, 0).text() == "Centro"
    assert tela._w_total().text() == "10,00"


def test_total_soma_valores(tela):
    tela._novo()
    tela._abrir_lancamento()
    _item_na_grade(tela, "A", 10.50)
    _item_na_grade(tela, "B", 5.25)
    assert tela._w_total().text() == "15,75"


# ---------------- testes: salvar ----------------

def test_salvar_bloqueado_sem_itens(tela, service, caixas):
    tela._novo()
    tela._abrir_lancamento()
    tela._sair_lancamento()
    tela._salvar()
    assert caixas.alguma("pelo menos um item")
    assert service.chamadas == []


def test_salvar_em_aberta_bloqueado(tela, service):
    tela._novo()
    tela._abrir_lancamento()
    tela._salvar()
    assert service.chamadas == []
    assert tela._modo == ESTADO_ABERTA


def test_salvar_novo_grava(tela, service, caixas):
    tela._novo()
    tela._abrir_lancamento()
    _item_na_grade(tela, "Centro", 10.0)
    tela._sair_lancamento()
    tela._salvar()
    assert [c[0] for c in service.chamadas] == ["salvar"]
    dados = service.chamadas[0][1]
    assert "sequencia" not in dados          # sequência é automática
    assert dados["itens"] == [{"destino": "Centro", "valor": 10.0}]
    assert caixas.alguma("salvo com sucesso")
    assert tela._modo == ESTADO_INICIAL      # tela limpa após salvar


def test_salvar_edicao_atualiza(tela, service):
    service.registros[1] = RegistroFake(
        sequencia=1, itens=[{"destino": "A", "valor": 5.0}],
        atualizado_em=datetime(2026, 10, 19, 12, 0, 0))
    _carregar(tela, service)
    _fluxo_edicao(tela)
    _item_na_grade(tela, "B", 7.0)           # item novo na edição
    tela._salvar()
    assert [c[0] for c in service.chamadas] == ["atualizar"]
    dados = service.chamadas[0][1]
    assert dados["sequencia"] == 1
    assert len(dados["itens"]) == 2


def test_base_injeta_versao_carregada(tela, service):
    versao = datetime(2026, 10, 19, 12, 0, 0)
    service.registros[1] = RegistroFake(
        sequencia=1, itens=[{"destino": "A", "valor": 5.0}],
        atualizado_em=versao)
    _carregar(tela, service)
    _fluxo_edicao(tela)
    tela._salvar()
    dados = service.chamadas[0][1]
    assert dados["atualizado_em"] == versao


def test_salvar_edicao_registro_sumiu(tela, service, caixas):
    service.registros[1] = RegistroFake(
        sequencia=1, itens=[{"destino": "A", "valor": 5.0}])
    _carregar(tela, service)
    service.registros.clear()                # outro usuário excluiu
    _fluxo_edicao(tela)
    tela._salvar()
    assert caixas.alguma("excluído por outro usuário")
    assert tela._modo == ESTADO_INICIAL


def test_conflito_avisa_e_recarrega(tela, service, caixas):
    service.registros[1] = RegistroFake(
        sequencia=1, itens=[{"destino": "A", "valor": 5.0}],
        atualizado_em=datetime(2026, 10, 19, 12, 0, 0))
    _carregar(tela, service)
    # outro usuário salvou durante a edição
    service.registros[1].atualizado_em = datetime(2026, 10, 19, 13, 0, 0)
    service.registros[1].itens = [{"destino": "Outro", "valor": 9.0}]
    _fluxo_edicao(tela)
    tela._salvar()
    assert caixas.alguma("alterado por outro usuário")
    # tela recarregada com a versão mais recente
    assert tela._modelo.rowCount() == 1
    assert tela._modelo.item(0, 0).text() == "Outro"
    assert tela._modo == ESTADO_VISUALIZACAO


def test_conflito_recarrego_falhou_limpa(tela, service, caixas):
    service.registros[1] = RegistroFake(
        sequencia=1, itens=[{"destino": "A", "valor": 5.0}],
        atualizado_em=datetime(2026, 10, 19, 12, 0, 0))
    _carregar(tela, service)
    service.registros[1].atualizado_em = datetime(2026, 10, 19, 13, 0, 0)
    # recarga após o conflito não encontra mais o registro
    service.buscar_por_sequencia = lambda sequencia: None
    _fluxo_edicao(tela)
    tela._salvar()
    assert caixas.alguma("alterado por outro usuário")
    assert tela._modo == ESTADO_INICIAL
    assert tela._w_sequencia().text() == ""


# ---------------- testes: excluir ----------------

def test_excluir_com_confirmacao(tela, service, caixas):
    service.registros[1] = RegistroFake(
        sequencia=1, itens=[{"destino": "A", "valor": 5.0}])
    _carregar(tela, service)
    tela._excluir()
    assert service.chamadas == [("excluir", 1)]
    assert caixas.alguma("excluído com sucesso")
    assert tela._modo == ESTADO_INICIAL


def test_excluir_cancelado_nao_chama_service(tela, service, caixas):
    service.registros[1] = RegistroFake(
        sequencia=1, itens=[{"destino": "A", "valor": 5.0}])
    _carregar(tela, service)
    caixas.resposta_question = QMessageBox.StandardButton.No
    tela._excluir()
    assert service.chamadas == []


def test_excluir_registro_sumiu(tela, service, caixas):
    service.registros[1] = RegistroFake(
        sequencia=1, itens=[{"destino": "A", "valor": 5.0}])
    _carregar(tela, service)
    service.registros.clear()
    tela._excluir()
    assert caixas.alguma("excluído por outro usuário")
    assert tela._modo == ESTADO_INICIAL


def test_excluir_sem_registro_carregado(tela, service, caixas):
    tela._excluir()
    assert caixas.alguma("Nenhum")
    assert service.chamadas == []
