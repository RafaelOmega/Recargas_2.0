# -*- coding: utf-8 -*-
"""Testes da PesquisaBase — valem para as 5 pesquisas que herdam dela
(colaboradores, usuários, saldo da conta, caminhões e recargas).

Filho mínimo (_PesquisaFake) com os widgets do contrato (campo de
filtro, botão Confirmar, grade e radios de status) e service falso.
Cobre carga inicial, debounce, confirmação (Enter/duplo clique/botão),
radios, ordenação numérica por UserRole e erro de consulta.
"""
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QLineEdit, QPushButton,
                               QRadioButton, QTableView, QVBoxLayout,
                               QWidget)

from app.controllers.pesquisa_base import PesquisaBase
from app.utils.table_utils import ajustar_larguras


# ---------------- infraestrutura falsa ----------------

class ServicePesquisaFake:
    """Substitui o service real — mesma interface, sem banco."""

    def __init__(self):
        self.registros = [
            {"codigo": "1", "nome": "Ana"},
            {"codigo": "2", "nome": "Bruno"},
            {"codigo": "10", "nome": "Carla"},
        ]
        self.ultimo_filtro = ""
        self.ultimo_ativo = None
        self.falhar = False

    def pesquisar(self, filtro, ativo=None):
        self.ultimo_filtro = filtro
        self.ultimo_ativo = ativo
        if self.falhar:
            raise RuntimeError("falha de banco")
        termo = filtro.lower()
        return [r for r in self.registros
                if termo in r["codigo"].lower()
                or termo in r["nome"].lower()]


class _UiPesquisaFake(QWidget):
    """Widgets do contrato da PesquisaBase, parentados no diálogo.

    Sem radios (com_radios=False), os atributos rb_Ativo/rb_Inativo
    NÃO são criados — igual às UIs reais geradas do Designer, onde o
    hasattr da PesquisaBase precisa devolver False (atributo None
    enganaria o hasattr e quebraria a conexão do toggled).
    """

    def __init__(self, dialogo: QDialog, com_radios: bool = True):
        super().__init__(dialogo)
        layout = QVBoxLayout(self)
        self.txt_Pesquisa = QLineEdit(self)
        self.bt_Pesquisa = QPushButton(self)
        self.tb_Grade = QTableView(self)
        layout.addWidget(self.txt_Pesquisa)
        layout.addWidget(self.bt_Pesquisa)
        layout.addWidget(self.tb_Grade)
        if com_radios:
            self.rb_Ativo = QRadioButton("Ativos", self)
            self.rb_Inativo = QRadioButton("Inativos", self)
            self.rb_Ativo.setChecked(True)
            layout.addWidget(self.rb_Ativo)
            layout.addWidget(self.rb_Inativo)


class PesquisaFake(PesquisaBase):
    """Filho mínimo: só o que o contrato da base exige."""

    def __init__(self, service: ServicePesquisaFake,
                 com_radios: bool = True):
        super().__init__()
        self.ui = _UiPesquisaFake(self, com_radios)
        self._service = service
        self._grade = self.ui.tb_Grade
        self._colunas = ["Código", "Nome"]
        self._coluna_padrao = 0
        self._coluna_stretch = 1
        self._ordem_padrao = Qt.SortOrder.AscendingOrder
        self.consultas = 0
        self._inicializar()

    # ---------------- hooks obrigatórios ----------------

    def _nome_pesquisa(self):
        return "registros"

    def _consultar(self):
        self.consultas += 1
        ativo = (self.ui.rb_Ativo.isChecked()
                 if hasattr(self.ui, "rb_Ativo") else None)
        return self._service.pesquisar(
            self.ui.txt_Pesquisa.text().strip(), ativo=ativo)

    def _popular_lista(self, registros):
        self._modelo.removeRows(0, self._modelo.rowCount())
        for registro in registros:
            self._modelo.appendRow([
                self._item_ordenavel(registro["codigo"],
                                     int(registro["codigo"])),
                self._item_ordenavel(registro["nome"],
                                     registro["nome"]),
            ])
        ajustar_larguras(self._grade, coluna_stretch=self._coluna_stretch)

    # ---------------- seleção (API do filho) ----------------

    def registro_selecionado(self):
        indice = self._grade.currentIndex()
        if not indice.isValid():
            return None
        item = self._modelo.item(indice.row(), 0)
        return item.text() if item is not None else None


# ---------------- fixtures ----------------

@pytest.fixture
def service():
    return ServicePesquisaFake()


@pytest.fixture
def dialogo(qtbot, service, caixas):
    dialogo = PesquisaFake(service)
    qtbot.addWidget(dialogo)
    return dialogo


# ---------------- carga e filtro ----------------

def test_carga_inicial_popula_grade(dialogo):
    assert dialogo.consultas == 1
    assert dialogo._modelo.rowCount() == 3
    assert dialogo._modelo.columnCount() == 2
    assert dialogo._modelo.horizontalHeaderItem(0).text() == "Código"


def test_filtro_debounce_repesquisa(qtbot, dialogo, service):
    dialogo.ui.txt_Pesquisa.setText("an")     # debounce 300ms agenda
    qtbot.waitUntil(lambda: dialogo.consultas == 2, timeout=2000)
    assert service.ultimo_filtro == "an"
    assert dialogo._modelo.rowCount() == 1    # só "Ana"


def test_radio_inativo_repesquisa(qtbot, dialogo, service):
    consultas_antes = dialogo.consultas
    dialogo.ui.rb_Inativo.setChecked(True)    # dispara toggled
    qtbot.waitUntil(lambda: dialogo.consultas == consultas_antes + 1,
                    timeout=2000)
    assert service.ultimo_ativo is False


def test_erro_na_consulta_nao_derruba_tela(qtbot, dialogo, service, caixas):
    service.falhar = True
    dialogo.ui.txt_Pesquisa.setText("x")
    qtbot.waitUntil(lambda: dialogo.consultas == 2, timeout=2000)
    assert caixas.do_tipo("critical")
    assert dialogo._modelo.rowCount() == 3    # dados anteriores preservados


# ---------------- confirmação ----------------

def test_confirmar_com_selecao_aceita(dialogo):
    dialogo._grade.selectRow(0)
    dialogo.ui.bt_Pesquisa.click()            # Confirmar
    assert dialogo.result() == QDialog.DialogCode.Accepted
    assert dialogo.registro_selecionado() == "1"


def test_confirmar_sem_selecao_apenas_pesquisa(dialogo):
    dialogo.ui.bt_Pesquisa.click()
    assert dialogo.result() != QDialog.DialogCode.Accepted
    assert dialogo.consultas == 2             # refez a pesquisa


def test_enter_na_grade_confirma(dialogo):
    dialogo._grade.selectRow(0)
    dialogo._at_enter_grade.activated.emit()  # atalho Enter da base
    assert dialogo.result() == QDialog.DialogCode.Accepted


def test_duplo_clique_confirma(dialogo):
    dialogo._grade.selectRow(0)
    # emite o sinal que o duplo clique dispararia (testa a ligação)
    dialogo._grade.doubleClicked.emit(dialogo._grade.currentIndex())
    assert dialogo.result() == QDialog.DialogCode.Accepted


# ---------------- ordenação ----------------

def test_ordenacao_numerica_por_user_role(dialogo):
    """Códigos '1','2','10' ordenam 1,2,10 — não 1,10,2 (texto)."""
    dialogo._grade.sortByColumn(0, Qt.SortOrder.AscendingOrder)
    ordem = [dialogo._modelo.item(linha, 0).text()
             for linha in range(dialogo._modelo.rowCount())]
    assert ordem == ["1", "2", "10"]

    dialogo._grade.sortByColumn(0, Qt.SortOrder.DescendingOrder)
    ordem = [dialogo._modelo.item(linha, 0).text()
             for linha in range(dialogo._modelo.rowCount())]
    assert ordem == ["10", "2", "1"]


def test_item_ordenavel_guarda_valor_no_user_role(dialogo):
    item = dialogo._modelo.item(0, 0)
    assert item.data(Qt.ItemDataRole.UserRole) == 1   # int, não texto


def test_sem_radios_funciona(qtbot, service, caixas):
    """Telas sem filtro de status (recargas) também herdam a base."""
    dialogo = PesquisaFake(service, com_radios=False)
    qtbot.addWidget(dialogo)
    assert dialogo.consultas == 1
    assert dialogo._modelo.rowCount() == 3
