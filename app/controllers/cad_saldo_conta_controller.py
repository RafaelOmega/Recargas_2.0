# -*- coding: utf-8 -*-
"""Controller da tela de Cadastro de Saldo da Conta Biz.

Responsabilidade: APENAS controle de tela. Máquina de estados, busca
por código, salvar/excluir e mensagens comuns vêm de CadastroBase —
aqui ficam apenas os widgets e os dados do lançamento.

O código é gerado automaticamente no salvar, mas o campo txt_Codigo
fica HABILITADO no estado inicial como campo de busca: digitar um
código e pressionar Enter carrega o lançamento direto do banco
(mesmo resultado de selecionar na pesquisa); Enter com o campo vazio
abre a pesquisa completa. Em novo/edição o campo volta a bloquear
(o código é gerado ou é a chave do update).

Navegação por teclado: Enter no valor (dbs_Valor) dispara o salvar —
é o último campo antes dos botões, evita voltar ao mouse. O
QDoubleSpinBox não tem returnPressed (consome o Enter internamente):
a base intercepta a tecla via eventFilter e chama _enter_campo,
sobrescrito aqui.
"""
from datetime import date

from PySide6.QtCore import QDate, QLocale
from PySide6.QtWidgets import QWidget

from app.controllers.cadastro_base import CadastroBase
from app.models.saldo_conta import SaldoConta
from app.utils.logger import get_logger
from app.views.ui_cad_saldo_conta import Ui_Cad_Saldo_Conta

try:
    from app.services.saldo_conta_service import SaldoContaService
except ImportError:
    SaldoContaService = None

logger = get_logger("cad_saldo_conta")


class CadSaldoContaController(CadastroBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Cad_Saldo_Conta()
        self.ui.setupUi(self)

        self._service = (SaldoContaService()
                         if SaldoContaService else None)

        # campo de valor: moeda com 2 decimais, formato pt-BR
        self.ui.dbs_Valor.setDecimals(2)
        self.ui.dbs_Valor.setRange(-999_999_999.99, 999_999_999.99)
        self.ui.dbs_Valor.setLocale(QLocale(QLocale.Portuguese,
                                            QLocale.Brazil))

        self._w_pesquisar = self.ui.bt_Pesquisar_Saldo_Conta
        self._w_campos = [self.ui.dt_Data, self.ui.dbs_Valor]
        self._w_foco_novo = self.ui.dt_Data
        self._inicializar()

    # ---------------- teclas específicas ----------------

    def _enter_campo(self, widget):
        """Enter no valor dispara o salvar; nos demais, comportamento
        padrão da base (avança o foco)."""
        if widget is self.ui.dbs_Valor:
            self._salvar()
        else:
            super()._enter_campo(widget)

    # ---------------- hooks do CadastroBase ----------------

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda->direita, cima->baixo).

        Linha 1 (frm_Codigo):  txt_Codigo -> bt_Pesquisar -> bt_Novo
        Linha 2 (frm_Corpo):   dt_Data -> dbs_Valor
        Linha 3 (frm_Crud):    bt_Salvar -> bt_Editar -> bt_Limpar
                               -> bt_Excluir
        """
        self.setTabOrder(self.ui.txt_Codigo,
                         self.ui.bt_Pesquisar_Saldo_Conta)
        self.setTabOrder(self.ui.bt_Pesquisar_Saldo_Conta,
                         self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.dt_Data)
        self.setTabOrder(self.ui.dt_Data, self.ui.dbs_Valor)
        self.setTabOrder(self.ui.dbs_Valor, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    def _pesquisar(self):
        """Abre a pesquisa e carrega o lançamento selecionado."""
        from app.controllers.pesquisa_saldo_conta_controller import (
            PesquisaSaldoContaController,
        )
        dialogo = PesquisaSaldoContaController(self)
        if dialogo.exec():
            saldo = dialogo.saldo_selecionado()
            if saldo:
                self._carregar_registro(saldo)

    def _nome_registro(self) -> str:
        return "lançamento"

    def _nome_service(self) -> str:
        return "saldo da conta"

    def _msg_duplicidade(self) -> str:
        return ""  # fallback genérico (igual ao comportamento atual)

    def _validar_obrigatorios(self) -> bool:
        # QDoubleSpinBox garante numérico; não há texto a validar
        return True

    def _coletar_dados(self) -> dict:
        qdata = self.ui.dt_Data.date()
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "data": date(qdata.year(), qdata.month(), qdata.day()),
            "valor": self.ui.dbs_Valor.value(),
        }

    def _preencher_campos(self, saldo: SaldoConta):
        if saldo.data:
            self.ui.dt_Data.setDate(QDate(
                saldo.data.year, saldo.data.month, saldo.data.day))
        self.ui.dbs_Valor.setValue(saldo.valor)

    def _limpar_especifico(self):
        self.ui.dt_Data.setDate(QDate.currentDate())
        self.ui.dbs_Valor.setValue(0.0)
