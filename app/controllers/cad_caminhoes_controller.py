# -*- coding: utf-8 -*-
"""Controller do cadastro de caminhões.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao CaminhaoService.

O código é automático (gerado no salvar): o campo txt_Codigo é
somente leitura, exibindo o código do caminhão carregado/salvo.
Navegação (Tab) em modo Z: esquerda para a direita e de cima
para baixo — código/pesquisar/novo -> modelo/placa/ativo -> CRUD.

Multiusuário: atualizar/excluir retornam False quando o registro
não existe mais (excluído por outro usuário) — a tela avisa e limpa
em vez de fingir sucesso.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.views.ui_cad_caminhoes import Ui_Cad_Caminhoes

try:
    from app.services.caminhao_service import CaminhaoService
except ImportError:
    CaminhaoService = None

logger = get_logger("cad_caminhoes")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"

_MSG_REGISTRO_SUMIU = ("Registro não encontrado — provavelmente foi "
                       "excluído por outro usuário. A tela será limpa.")


class CadCaminhoesController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Cad_Caminhoes()
        self.ui.setupUi(self)

        self._service = (CaminhaoService()
                         if CaminhaoService else None)
        if self._service is None:
            logger.warning(
                "CaminhaoService nao encontrado - acoes desativadas")

        self._modo = ESTADO_INICIAL

        self._conectar_botoes()
        self._conectar_teclas()
        self._definir_tab_order()
        self._limpar_campos()

    # ---------------- conexões ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisar_Caminhoes.clicked.connect(self._pesquisar)
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
        Linha 2 (frm_Corpo):   txt_Modelo -> txt_Placa -> chk_Ativo
        Linha 3 (frm_Crud):    bt_Salvar -> bt_Editar -> bt_Limpar
                               -> bt_Excluir
        """
        self.setTabOrder(self.ui.txt_Codigo,
                         self.ui.bt_Pesquisar_Caminhoes)
        self.setTabOrder(self.ui.bt_Pesquisar_Caminhoes, self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.txt_Modelo)
        self.setTabOrder(self.ui.txt_Modelo, self.ui.txt_Placa)
        self.setTabOrder(self.ui.txt_Placa, self.ui.chk_Ativo)
        self.setTabOrder(self.ui.chk_Ativo, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    # ---------------- estados da tela ----------------

    def _estado_inicial(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é automático
        self.ui.bt_Pesquisar_Caminhoes.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self.ui.txt_Modelo.setEnabled(False)
        self.ui.txt_Placa.setEnabled(False)
        self.ui.chk_Ativo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é automático
        self.ui.txt_Codigo.clear()
        self.ui.txt_Modelo.setEnabled(True)
        self.ui.txt_Placa.setEnabled(True)
        self.ui.chk_Ativo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Caminhoes.setEnabled(False)

    def _estado_visualizacao(self):
        self.ui.txt_Codigo.setEnabled(False)
        self.ui.txt_Modelo.setEnabled(False)
        self.ui.txt_Placa.setEnabled(False)
        self.ui.chk_Ativo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Caminhoes.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _estado_edicao(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é a chave
        self.ui.txt_Modelo.setEnabled(True)
        self.ui.txt_Placa.setEnabled(True)
        self.ui.chk_Ativo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Caminhoes.setEnabled(False)

    # ---------------- ações de tela ----------------

    def _iniciar_novo(self):
        self._limpar_campos()
        self._modo = ESTADO_NOVO
        self._estado_novo()
        self.ui.txt_Modelo.setFocus()

    def _novo(self):
        if self._modo != ESTADO_INICIAL:
            return
        self._iniciar_novo()

    def _liberar_edicao(self):
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self.ui.txt_Modelo.setFocus()

    def _pesquisar(self):
        from app.controllers.pesquisa_caminhoes_controller import (
            PesquisaCaminhoesController,
        )
        dialogo = PesquisaCaminhoesController(self)
        if dialogo.exec():
            caminhao = dialogo.caminhao_selecionado()
            if caminhao:
                self._preencher(caminhao)

    def _validar_obrigatorios(self) -> bool:
        if not self.ui.txt_Modelo.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o modelo.")
            self.ui.txt_Modelo.setFocus()
            return False
        return True

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de caminhões indisponível.")
            return
        if not self._validar_obrigatorios():
            return

        dados = self._coletar_dados()
        try:
            if self._modo == ESTADO_NOVO:
                caminhao = self._service.salvar(dados)
                # exibe o código gerado automaticamente
                self.ui.txt_Codigo.setText(caminhao.codigo)
            elif self._modo == ESTADO_EDICAO:
                if not self._service.atualizar(dados):
                    # outro usuário excluiu o caminhão enquanto
                    # a edição estava aberta
                    logger.warning(
                        "Atualização sem efeito: caminhão %s "
                        "não existe mais",
                        dados.get("codigo"))
                    QMessageBox.warning(self, "Atenção",
                                        _MSG_REGISTRO_SUMIU)
                    self._limpar_campos()
                    self.ui.txt_Codigo.setFocus()
                    return
            else:
                return
        except Exception as exc:
            logger.exception("Falha ao salvar caminhão")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar o caminhão:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("Caminhão salvo")
        QMessageBox.information(
            self, "Sucesso", "Caminhão salvo com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    def _excluir(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de caminhões indisponível.")
            return
        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            return
        resposta = QMessageBox.question(
            self, "Excluir",
            f"Excluir o caminhão {codigo}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resposta != QMessageBox.StandardButton.Yes:
            return
        try:
            excluido = self._service.excluir(codigo)
        except Exception as exc:
            logger.exception("Falha ao excluir caminhão")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir:\n{self._mensagem_erro(exc)}")
            return
        if not excluido:
            # outro usuário já havia excluído
            logger.warning("Exclusão sem efeito: caminhão %s "
                           "não existe mais", codigo)
            QMessageBox.warning(self, "Atenção",
                                "Caminhão não encontrado — provavelmente "
                                "já foi excluído por outro usuário.")
            self._limpar_campos()
            self.ui.txt_Codigo.setFocus()
            return
        logger.info("Caminhão excluído: %s", codigo)
        QMessageBox.information(
            self, "Sucesso", "Caminhão excluído com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(
            exc, duplicidade="Já existe um caminhão com esse código.")

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Modelo.clear()
        self.ui.txt_Placa.clear()
        self.ui.chk_Ativo.setChecked(True)  # novo caminhão nasce ativo
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    def _coletar_dados(self) -> dict:
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "modelo": self.ui.txt_Modelo.text().strip(),
            "placa": self.ui.txt_Placa.text().strip(),
            "ativo": self.ui.chk_Ativo.isChecked(),
        }

    def _preencher(self, caminhao):
        self._limpar_campos()
        self.ui.txt_Codigo.setText(caminhao.codigo)
        self.ui.txt_Modelo.setText(caminhao.modelo)
        self.ui.txt_Placa.setText(caminhao.placa)
        self.ui.chk_Ativo.setChecked(caminhao.ativo)
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()
