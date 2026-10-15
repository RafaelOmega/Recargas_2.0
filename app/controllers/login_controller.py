# -*- coding: utf-8 -*-
"""Controller da tela de login.

QDialog modal: bloqueia o acesso até autenticar. Consulta a tabela
usuarios via UsuarioService (buscar_por_login) e confere a senha com
verificar_senha (PBKDF2). Usuário inativo não entra.

Navegação (Tab) em modo Z: usuario -> senha -> Entrar.
Enter no campo senha dispara o login.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox

from app.utils.logger import get_logger
from app.utils.senha import verificar_senha
from app.views.ui_login import Ui_Login

try:
    from app.services.usuario_service import UsuarioService
except ImportError:
    UsuarioService = None

logger = get_logger("login")


class LoginController(QDialog):
    """Autenticação do usuário antes de abrir o sistema."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Login()
        self.ui.setupUi(self)

        self._service = (UsuarioService()
                         if UsuarioService else None)
        if self._service is None:
            logger.warning("UsuarioService nao encontrado")

        self.usuario_autenticado = None  # preenchido no sucesso

        self.ui.bt_Entrar.clicked.connect(self._entrar)
        self.ui.txt_Senha.returnPressed.connect(self._entrar)
        self.ui.txt_Usuario.returnPressed.connect(
            self.ui.txt_Senha.setFocus)

        # ordem de tabulação em modo Z
        self.setTabOrder(self.ui.txt_Usuario, self.ui.txt_Senha)
        self.setTabOrder(self.ui.txt_Senha, self.ui.bt_Entrar)

        self.ui.txt_Usuario.setFocus()

    def _entrar(self):
        """Valida as credenciais; aceita o diálogo em caso de sucesso."""
        login = self.ui.txt_Usuario.text().strip()
        senha = self.ui.txt_Senha.text()

        if not login or not senha:
            QMessageBox.warning(
                self, "Atenção", "Informe usuário e senha.")
            if not login:
                self.ui.txt_Usuario.setFocus()
            else:
                self.ui.txt_Senha.setFocus()
            return

        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de usuários indisponível.")
            return

        try:
            usuario = self._service.buscar_por_login(login)
        except Exception as exc:
            logger.exception("Falha ao consultar usuário no login")
            QMessageBox.critical(
                self, "Erro",
                f"Falha ao consultar o usuário:\n{exc}")
            return

        # mensagem única: não revela se o login existe
        if (usuario is None or not usuario.ativo
                or not verificar_senha(senha, usuario.senha_hash)):
            logger.warning("Tentativa de login recusada: %s", login)
            QMessageBox.warning(
                self, "Atenção", "Usuário ou senha inválidos.")
            self.ui.txt_Senha.clear()
            self.ui.txt_Senha.setFocus()
            return

        logger.info("Login efetuado: %s (código %s)",
                    usuario.login, usuario.codigo)
        self.usuario_autenticado = usuario
        self.accept()
