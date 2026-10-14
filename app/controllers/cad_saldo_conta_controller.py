# -*- coding: utf-8 -*-
"""Controller da tela de Cadastro de Saldo da Conta Biz.

Responsabilidade: APENAS controle de tela (máquina de estados,
botões, tab order, validações simples de formulário) — sem lógica
de negócio nem acesso a dados. Dados via SaldoContaService.

Máquina de estados (padrão do cadastro de colaboradores):
  inicial      -> só "+" e "..." ativos
  novo         -> campos liberados, Salvar grava (código automático)
  visualizacao -> registro carregado via pesquisa (somente leitura)
  edicao       -> "Editar" liberou os campos; Salvar atualiza

Valor em QDoubleSpinBox (dbs_Valor, prefixo "R$ "): o widget já
garante numérico com 2 decimais — não há texto a validar/converter.
"""
from datetime import date

from PySide6.QtCore import QDate, QLocale, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox, QWidget

from app.models.saldo_conta import SaldoConta
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.views.ui_cad_saldo_conta import Ui_Cad_Saldo_Conta

try:
    from app.services.saldo_conta_service import SaldoContaService
except ImportError:
    SaldoContaService = None

logger = get_logger("cad_saldo_conta")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"


class CadSaldoContaController(QWidget):
    """Cadastro de lançamentos de saldo da conta Biz."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Cad_Saldo_Conta()
        self.ui.setupUi(self)

        self._service = (SaldoContaService()
                         if SaldoContaService else None)
        if self._service is None:
            logger.warning(
                "SaldoContaService nao encontrado - acoes desativadas")

        # campo de valor: moeda com 2 decimais, formato pt-BR
        self.ui.dbs_Valor.setDecimals(2)
        self.ui.dbs_Valor.setRange(-999_999_999.99, 999_999_999.99)
        self.ui.dbs_Valor.setLocale(
            QLocale(QLocale.Portuguese, QLocale.Brazil))

        self._modo = ESTADO_INICIAL

        self._conectar_botoes()
        self._conectar_teclas()
        self._definir_tab_order()
        self._limpar_campos()

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisar_Saldo_Conta.clicked.connect(self._pesquisar)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        # código é automático: Enter no campo abre a pesquisa
        self.ui.txt_Codigo.returnPressed.connect(self._pesquisar)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)

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

    # ---------------- estados da tela ----------------

    def _estado_inicial(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é automático
        self.ui.bt_Pesquisar_Saldo_Conta.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self.ui.dt_Data.setEnabled(False)
        self.ui.dbs_Valor.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é automático
        self.ui.txt_Codigo.clear()
        self.ui.dt_Data.setEnabled(True)
        self.ui.dbs_Valor.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Saldo_Conta.setEnabled(False)

    def _estado_visualizacao(self):
        self.ui.txt_Codigo.setEnabled(False)
        self.ui.dt_Data.setEnabled(False)
        self.ui.dbs_Valor.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Saldo_Conta.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _estado_edicao(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é a chave
        self.ui.dt_Data.setEnabled(True)
        self.ui.dbs_Valor.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Saldo_Conta.setEnabled(False)

    # ---------------- ações ----------------

    def _iniciar_novo(self):
        self._limpar_campos()
        self._modo = ESTADO_NOVO
        self._estado_novo()
        self.ui.dt_Data.setFocus()

    def _novo(self):
        if self._modo != ESTADO_INICIAL:
            return
        self._iniciar_novo()

    def _liberar_edicao(self):
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self.ui.dt_Data.setFocus()

    def _pesquisar(self):
        from app.controllers.pesquisa_saldo_conta_controller import (
            PesquisaSaldoContaController,
        )
        dialogo = PesquisaSaldoContaController(self)
        if dialogo.exec():
            saldo = dialogo.saldo_selecionado()
            if saldo:
                self._carregar(saldo)

    def _carregar(self, saldo: SaldoConta):
        self.ui.txt_Codigo.setText(saldo.codigo)
        if saldo.data:
            self.ui.dt_Data.setDate(QDate(
                saldo.data.year, saldo.data.month, saldo.data.day))
        self.ui.dbs_Valor.setValue(saldo.valor)
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()

    def _coletar_dados(self) -> dict:
        qdata = self.ui.dt_Data.date()
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "data": date(qdata.year(), qdata.month(), qdata.day()),
            "valor": self.ui.dbs_Valor.value(),
        }

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de saldo da conta indisponível.")
            return

        dados = self._coletar_dados()
        try:
            if self._modo == ESTADO_NOVO:
                saldo = self._service.salvar(dados)
                # exibe o código gerado automaticamente
                self.ui.txt_Codigo.setText(saldo.codigo)
            elif self._modo == ESTADO_EDICAO:
                self._service.atualizar(dados)
            else:
                return
        except Exception as exc:
            logger.exception("Falha ao salvar lançamento de saldo")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar o lançamento:"
                f"\n{mensagem_erro(exc)}")
            return

        logger.info("Lançamento de saldo salvo")
        QMessageBox.information(
            self, "Sucesso", "Lançamento salvo com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    def _excluir(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de saldo da conta indisponível.")
            return
        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            return
        resposta = QMessageBox.question(
            self, "Excluir",
            f"Excluir o lançamento {codigo}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resposta != QMessageBox.StandardButton.Yes:
            return
        try:
            self._service.excluir(codigo)
        except Exception as exc:
            logger.exception("Falha ao excluir lançamento de saldo")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir:\n{mensagem_erro(exc)}")
            return
        logger.info("Lançamento de saldo excluído: %s", codigo)
        QMessageBox.information(
            self, "Sucesso", "Lançamento excluído com sucesso.")
        self._limpar_campos()

    def _limpar_campos(self):
        self._modo = ESTADO_INICIAL
        self.ui.txt_Codigo.clear()
        self.ui.dt_Data.setDate(QDate.currentDate())
        self.ui.dbs_Valor.setValue(0.0)
        self._estado_inicial()
