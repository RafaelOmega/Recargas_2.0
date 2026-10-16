# -*- coding: utf-8 -*-
"""Controller do cadastro de usuários.

Responsabilidade: APENAS controle de tela (máquina de estados,
botões, tab order, validações de formulário). Dados via
UsuarioService — a senha em texto puro só existe aqui dentro e
vai ao service para virar hash.

Máquina de estados (padrão do cadastro de colaboradores):
inicial      -> só "+" e "..." ativos
  novo         -> campos liberados, Salvar grava (código automático)
  visualizacao -> registro carregado via pesquisa (somente leitura)
  edicao       -> "Editar" liberou os campos; Salvar atualiza

O código é gerado automaticamente no salvar, mas o campo txt_Codigo
fica HABILITADO no estado inicial como campo de busca: digitar um
código e Enter carrega o usuário direto do banco (mesmo resultado
de selecionar na pesquisa); Enter com o campo vazio abre a pesquisa
completa. Em novo/edição o campo volta a bloquear (o código é gerado
ou é a chave do update).

Senha: obrigatória no novo (mínimo 4 caracteres); na edição,
vazia significa "manter a senha atual".
O hash nunca é exibido.

Multiusuário: atualizar/excluir retornam False quando o registro
não existe mais (excluído por outro usuário) — a tela avisa e limpa.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.views.ui_cad_usuarios import Ui_Cad_Usuarios

try:
    from app.services.usuario_service import UsuarioService
except ImportError:
    UsuarioService = None

logger = get_logger("cad_usuarios")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"

_TAM_SENHA_MIN = 4

_MSG_REGISTRO_SUMIU = ("Registro não encontrado — provavelmente foi "
                       "excluído por outro usuário. A tela será limpa.")


class CadUsuariosController(QWidget):
    """Cadastro de usuários do sistema."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Cad_Usuarios()
        self.ui.setupUi(self)

        self._service = (UsuarioService()
                         if UsuarioService else None)
        if self._service is None:
            logger.warning(
                "UsuarioService nao encontrado - acoes desativadas")

        self._modo = ESTADO_INICIAL
        self._conectar_botoes()
        self._conectar_teclas()
        self._definir_tab_order()
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    # ---------------- conexoes ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisar_Usuario.clicked.connect(self._pesquisar)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        # Enter no código: com texto busca direto; vazio abre a pesquisa
        self.ui.txt_Codigo.returnPressed.connect(self._enter_codigo)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda->direita, cima->baixo).

        Linha 1 (frm_Codigo):   txt_Codigo -> bt_Pesquisar -> bt_Novo
        Linha 2 (frm_Corpo):    txt_Nome -> txt_Documento -> chk_Ativo
        Linha 3 (frm_Usuario):  txt_Usuario -> txt_Senha
        Linha 4 (frm_Crud):     bt_Salvar -> bt_Editar -> bt_Limpar
                                -> bt_Excluir
        """
        self.setTabOrder(self.ui.txt_Codigo,
                         self.ui.bt_Pesquisar_Usuario)
        self.setTabOrder(self.ui.bt_Pesquisar_Usuario, self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.txt_Nome)
        self.setTabOrder(self.ui.txt_Nome, self.ui.txt_Documento)
        self.setTabOrder(self.ui.txt_Documento, self.ui.chk_Ativo)
        self.setTabOrder(self.ui.chk_Ativo, self.ui.txt_Usuario)
        self.setTabOrder(self.ui.txt_Usuario, self.ui.txt_Senha)
        self.setTabOrder(self.ui.txt_Senha, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    # ---------------- estados da tela ----------------

    def _estado_inicial(self):
        self.ui.txt_Codigo.setEnabled(True)   # campo de busca liberado
        self.ui.bt_Pesquisar_Usuario.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self.ui.txt_Nome.setEnabled(False)
        self.ui.txt_Documento.setEnabled(False)
        self.ui.chk_Ativo.setEnabled(False)
        self.ui.txt_Usuario.setEnabled(False)
        self.ui.txt_Senha.setEnabled(False)
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
        self.ui.txt_Usuario.setEnabled(True)
        self.ui.txt_Senha.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Usuario.setEnabled(False)

    def _estado_visualizacao(self):
        self.ui.txt_Codigo.setEnabled(False)  # evita alterar a chave
        self.ui.txt_Nome.setEnabled(False)
        self.ui.txt_Documento.setEnabled(False)
        self.ui.chk_Ativo.setEnabled(False)
        self.ui.txt_Usuario.setEnabled(False)
        self.ui.txt_Senha.setEnabled(False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Usuario.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _estado_edicao(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é a chave
        self.ui.txt_Nome.setEnabled(True)
        self.ui.txt_Documento.setEnabled(True)
        self.ui.chk_Ativo.setEnabled(True)
        self.ui.txt_Usuario.setEnabled(True)
        self.ui.txt_Senha.setEnabled(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self.ui.bt_Pesquisar_Usuario.setEnabled(False)

    # ---------------- ações ----------------

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

    def _enter_codigo(self):
        """Enter no código: com texto busca direto; vazio abre pesquisa."""
        if self.ui.txt_Codigo.text().strip():
            self._buscar_por_codigo()
        else:
            self._pesquisar()

    def _buscar_por_codigo(self):
        """Carrega o usuário do código digitado direto do banco."""
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de usuários indisponível.")
            return
        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            return
        try:
            usuario = self._service.buscar_por_codigo(codigo)
        except Exception as exc:
            logger.exception("Falha ao buscar usuário %s", codigo)
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o usuário:"
                f"\n{self._mensagem_erro(exc)}")
            return
        if usuario is None:
            QMessageBox.information(
                self, "Não encontrado",
                f"Usuário {codigo} não encontrado.")
            self.ui.txt_Codigo.setFocus()
            self.ui.txt_Codigo.selectAll()
            return
        self._preencher(usuario)

    def _pesquisar(self):
        from app.controllers.pesquisa_usuario_controller import (
            PesquisaUsuarioController,
        )
        dialogo = PesquisaUsuarioController(self)
        if dialogo.exec():
            usuario = dialogo.usuario_selecionado()
            if usuario:
                self._preencher(usuario)

    def _validar_obrigatorios(self) -> bool:
        if not self.ui.txt_Nome.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o nome.")
            self.ui.txt_Nome.setFocus()
            return False
        if not self.ui.txt_Usuario.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o usuário.")
            self.ui.txt_Usuario.setFocus()
            return False

        senha = self.ui.txt_Senha.text()
        if self._modo == ESTADO_NOVO or senha:
            # novo: senha obrigatória; edição: só valida se digitada
            if len(senha) < _TAM_SENHA_MIN:
                QMessageBox.warning(
                    self, "Atenção",
                    f"A senha deve ter pelo menos {_TAM_SENHA_MIN} "
                    "caracteres.")
                self.ui.txt_Senha.setFocus()
                return False
        return True

    def _coletar_dados(self) -> dict:
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "nome": self.ui.txt_Nome.text().strip(),
            "documento": self.ui.txt_Documento.text().strip(),
            "login": self.ui.txt_Usuario.text().strip(),
            "senha": self.ui.txt_Senha.text(),
            "ativo": self.ui.chk_Ativo.isChecked(),
        }

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de usuários indisponível.")
            return
        if not self._validar_obrigatorios():
            return

        dados = self._coletar_dados()
        try:
            if self._modo == ESTADO_NOVO:
                usuario = self._service.salvar(dados)
                # exibe o código gerado automaticamente
                self.ui.txt_Codigo.setText(usuario.codigo)
            elif self._modo == ESTADO_EDICAO:
                if not self._service.atualizar(dados):
                    # outro usuário excluiu o usuário enquanto a
                    # edição estava aberta
                    logger.warning(
                        "Atualização sem efeito: usuário %s "
                        "não existe mais",
                        dados.get("codigo"))
                    QMessageBox.warning(self, "Atenção",
                                        _MSG_REGISTRO_SUMIU)
                    self._limpar_campos()
                    self.ui.txt_Codigo.setFocus()
                    return
            else:
                return
        except ValueError as exc:
            QMessageBox.warning(self, "Atenção", str(exc))
            self.ui.txt_Senha.setFocus()
            return
        except Exception as exc:
            logger.exception("Falha ao salvar usuário")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar o usuário:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("Usuario salvo")
        QMessageBox.information(
            self, "Sucesso", "Usuário salvo com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    def _excluir(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de usuários indisponível.")
            return
        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            return
        resposta = QMessageBox.question(
            self, "Excluir",
            f"Excluir o usuário {codigo}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resposta != QMessageBox.StandardButton.Yes:
            return
        try:
            excluido = self._service.excluir(codigo)
        except Exception as exc:
            logger.exception("Falha ao excluir usuário")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir:\n{self._mensagem_erro(exc)}")
            return
        if not excluido:
            # outro usuário já havia excluído
            logger.warning("Exclusão sem efeito: usuário %s "
                           "não existe mais", codigo)
            QMessageBox.warning(self, "Atenção",
                                "Usuário não encontrado — provavelmente "
                                "já foi excluído por outro usuário.")
            self._limpar_campos()
            self.ui.txt_Codigo.setFocus()
            return
        logger.info("Usuario excluído: %s", codigo)
        QMessageBox.information(
            self, "Sucesso", "Usuário excluído com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(
            exc,
            duplicidade="Já existe um usuário com esse código ou login.")

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self.ui.txt_Nome.clear()
        self.ui.txt_Documento.clear()
        self.ui.txt_Usuario.clear()
        self.ui.txt_Senha.clear()
        self.ui.chk_Ativo.setChecked(True)  # novo usuário nasce ativo
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    def _preencher(self, usuario):
        self._limpar_campos()
        self.ui.txt_Codigo.setText(usuario.codigo)
        self.ui.txt_Nome.setText(usuario.nome)
        self.ui.txt_Documento.setText(usuario.documento)
        self.ui.txt_Usuario.setText(usuario.login)
        # senha nunca é exibida: vazia = manter a atual na edição
        self.ui.chk_Ativo.setChecked(usuario.ativo)
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()
