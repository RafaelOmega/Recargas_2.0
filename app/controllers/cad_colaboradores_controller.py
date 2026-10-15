# -*- coding: utf-8 -*-
"""Controller do cadastro de colaboradores.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao ColaboradorService.

O código é automático (gerado no salvar): o campo txt_Codigo é
somente leitura, exibindo o código do colaborador carregado/salvo.
Navegação (Tab) em modo Z: esquerda para a direita e de cima
para baixo — código/pesquisar/novo -> nome/documento/ativo -> CRUD.

Multiusuário: atualizar/excluir retornam False quando o registro
não existe mais (excluído por outro usuário) — a tela avisa e limpa
em vez de fingir sucesso.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.views.ui_cad_colaboradores import Ui_Cad_Colaboradores

try:
    from app.services.colaborador_service import ColaboradorService
except ImportError:
    ColaboradorService = None

logger = get_logger("cad_colaboradores")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"

_MSG_REGISTRO_SUMIU = ("Registro não encontrado — provavelmente foi "
                       "excluído por outro usuário. A tela será limpa.")


class CadColaboradoresController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Cad_Colaboradores()
        self.ui.setupUi(self)

        self._service = (ColaboradorService()
                         if ColaboradorService else None)
        if self._service is None:
            logger.warning(
                "ColaboradorService nao encontrado - acoes desativadas")

        self._modo = ESTADO_INICIAL

        self._conectar_botoes()
        self._conectar_teclas()
        self._definir_tab_order()
        self._limpar_campos()

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisar_Colaborador.clicked.connect(self._pesquisar)
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
        Linha 2 (frm_Corpo):   txt_Nome -> txt_Documento -> chk_Ativo
        Linha 3 (frm_Crud):    bt_Salvar -> bt_Editar -> bt_Limpar
                               -> bt_Excluir
        """
        self.setTabOrder(self.ui.txt_Codigo,
                         self.ui.bt_Pesquisar_Colaborador)
        self.setTabOrder(self.ui.bt_Pesquisar_Colaborador, self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.txt_Nome)
        self.setTabOrder(self.ui.txt_Nome, self.ui.txt_Documento)
        self.setTabOrder(self.ui.txt_Documento, self.ui.chk_Ativo)
        self.setTabOrder(self.ui.chk_Ativo, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    # ---------------- estados da tela ----------------

    def _estado_inicial(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é automático
        self.ui.bt_Pesquisar_Colaborador.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self.ui.txt_Nome.setEnabled(False)
        self.ui.txt_Documento.setEnabled(False)
        self.ui.chk_Ativo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é automático
        self.ui.txt_Codigo.clear()
        self.ui.txt_Nome.setEnabled(True)
        self.ui.txt_Documento.setEnabled(True)
        self.ui.chk_Ativo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Colaborador.setEnabled(False)

    def _estado_visualizacao(self):
        self.ui.txt_Codigo.setEnabled(False)
        self.ui.txt_Nome.setEnabled(False)
        self.ui.txt_Documento.setEnabled(False)
        self.ui.chk_Ativo.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Colaborador.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _estado_edicao(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é a chave
        self.ui.txt_Nome.setEnabled(True)
        self.ui.txt_Documento.setEnabled(True)
        self.ui.chk_Ativo.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Colaborador.setEnabled(False)

    # ---------------- acoes de tela ----------------

    def _iniciar_novo(self):
        self._limpar_campos()
        self._modo = ESTADO_NOVO
        self._estado_novo()
        self.ui.txt_Nome.setFocus()

    def _novo(self):
        if self._modo != ESTADO_INICIAL:
            return
        self._iniciar_novo()

    def _liberar_edicao(self):
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self.ui.txt_Nome.setFocus()

    def _pesquisar(self):
        from app.controllers.pesquisa_colaborador_controller import (
            PesquisaColaboradorController,
        )
        dialogo = PesquisaColaboradorController(self)
        if dialogo.exec():
            colaborador = dialogo.colaborador_selecionado()
            if colaborador:
                self._preencher(colaborador)

    def _validar_obrigatorios(self) -> bool:
        if not self.ui.txt_Nome.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o nome.")
            self.ui.txt_Nome.setFocus()
            return False
        return True

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de colaboradores indisponível.")
            return
        if not self._validar_obrigatorios():
            return

        dados = self._coletar_dados()
        try:
            if self._modo == ESTADO_NOVO:
                colaborador = self._service.salvar(dados)
                # exibe o código gerado automaticamente
                self.ui.txt_Codigo.setText(colaborador.codigo)
            elif self._modo == ESTADO_EDICAO:
                if not self._service.atualizar(dados):
                    # outro usuário excluiu o colaborador enquanto
                    # a edição estava aberta
                    logger.warning(
                        "Atualização sem efeito: colaborador %s "
                        "não existe mais", dados.get("codigo"))
                    QMessageBox.warning(self, "Atenção",
                                        _MSG_REGISTRO_SUMIU)
                    self._limpar_campos()
                    self.ui.txt_Codigo.setFocus()
                    return
            else:
                return
        except Exception as exc:
            logger.exception("Falha ao salvar colaborador")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar o colaborador:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("Colaborador salvo")
        QMessageBox.information(
            self, "Sucesso", "Colaborador salvo com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    def _excluir(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de colaboradores indisponível.")
            return
        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            return
        resposta = QMessageBox.question(
            self, "Excluir",
            f"Excluir o colaborador {codigo}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resposta != QMessageBox.StandardButton.Yes:
            return
        try:
            excluido = self._service.excluir(codigo)
        except Exception as exc:
            logger.exception("Falha ao excluir colaborador")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir:\n{self._mensagem_erro(exc)}")
            return
        if not excluido:
            # outro usuário já havia excluído
            logger.warning("Exclusão sem efeito: colaborador %s "
                           "não existe mais", codigo)
            QMessageBox.warning(self, "Atenção",
                                "Colaborador não encontrado — provavelmente "
                                "já foi excluído por outro usuário.")
            self._limpar_campos()
            self.ui.txt_Codigo.setFocus()
            return
        logger.info("Colaborador excluído: %s", codigo)
        QMessageBox.information(
            self, "Sucesso", "Colaborador excluído com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(
            exc, duplicidade="Já existe um colaborador com esse código.")

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Nome.clear()
        self.ui.txt_Documento.clear()
        self.ui.txt_Usuario.clear()
        self.ui.txt_Senha.clear()
        self.ui.txt_Senha.setPlaceholderText(
            "mínimo 4 caracteres")
        self.ui.chk_Ativo.setChecked(True)
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    def _coletar_dados(self) -> dict:
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "nome": self.ui.txt_Nome.text().strip(),
            "documento": self.ui.txt_Documento.text().strip(),
            "ativo": self.ui.chk_Ativo.isChecked(),
        }

    def _preencher(self, usuario):
        self._limpar_campos()
        self.ui.txt_Codigo.setText(usuario.codigo)
        self.ui.txt_Nome.setText(usuario.nome)
        self.ui.txt_Documento.setText(usuario.documento)
        self.ui.txt_Usuario.setText(usuario.login)
        # senha nunca é exibida: placeholder indica que existe senha
        # definida; vazio na edição = manter a atual
        self.ui.txt_Senha.setPlaceholderText(
            "••••••  (deixe vazio para manter a senha atual)")
        self.ui.chk_Ativo.setChecked(usuario.ativo)
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()
