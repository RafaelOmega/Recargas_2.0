# -*- coding: utf-8 -*-
"""Ponto de entrada do sistema Recargas."""
import ctypes
import os
import sys

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from app.controllers.carregamento_controller import CarregamentoController
from app.controllers.login_controller import LoginController
from app.controllers.main_window_controller import MainWindowController
from app.database import get_connection
from app.database.schema import criar_schema
from app.utils import sessao
from app.utils.icons import aplicar_icone_aplicacao
from app.utils.logger import get_logger, setup_logging
from app.utils.theme import aplicar_tema
from app.version import __version__

logger = get_logger("main")

# WebEngine (dashboard Power BI): sem aceleração de GPU, sem processo
# de GPU separado e sem sandbox — evita tela branca em máquinas/RDP
# sem suporte adequado. O --no-sandbox é necessário quando o app roda
# de unidade de rede: o sandbox do Chromium não sobe em caminho de rede.
os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--disable-gpu --disable-gpu-compositing "
    "--in-process-gpu --no-sandbox",
)


def _definir_app_id():
    """Define o AppUserModelID para o Windows usar o ícone correto
    na barra de tarefas (em vez do ícone do python.exe)."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "Omega.Recargas.2.0"
        )
    except Exception:
        pass  # não é Windows ou falhou -> segue sem o ID


def _validar_conexao() -> bool:
    """Tenta conectar ao banco. Retorna True se conectou."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception as exc:
        logger.error("Falha ao conectar ao banco: %s", exc)
        return False


def main() -> int:
    setup_logging()
    logger.info("Iniciando sistema Recargas %s", __version__)

    _definir_app_id()

    # exigido pelo Qt WebEngine: definir ANTES de criar o QApplication,
    # senão o QWebEngineView fica em branco
    QCoreApplication.setAttribute(
        Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    aplicar_tema(app)
    aplicar_icone_aplicacao(app)

    # splash: aparece antes de qualquer passo bloqueante
    splash = CarregamentoController()
    splash.show()
    splash.atualizar(10, "Abrindo Controle de Recargas")
    splash.atualizar(30, "Conectando ao banco de dados...")
    if not _validar_conexao():
        resposta = QMessageBox.question(
            splash,
            "Banco de dados",
            "Não foi possível conectar ao banco de dados.\n\n"
            "Deseja continuar mesmo assim?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            logger.info("Aplicação encerrada pelo usuário (sem banco)")
            splash.close()
            return 0
    else:
        # cria as tabelas que não existirem (idempotente)
        splash.atualizar(60, "Preparando as tabelas do banco...")
        try:
            criar_schema()
        except Exception as exc:
            logger.error("Falha ao preparar o schema: %s", exc)
            splash.close()
            QMessageBox.critical(
                None,
                "Banco de dados",
                f"Não foi possível preparar as tabelas do banco:\n{exc}",
            )
            return 1

    # login: bloqueia o acesso antes de abrir o sistema
    splash.atualizar(80, "Autenticando usuário...")
    splash.close()
    login = LoginController()
    if login.exec() != QDialog.DialogCode.Accepted:
        logger.info("Login cancelado — encerrando")
        return 0
    usuario = login.usuario_autenticado
    # last-write-wins: registra quem está editando (carimbo pelo_usuario)
    sessao.definir_usuario(usuario.login if usuario else "")
    logger.info("Sessão iniciada: %s", usuario.login if usuario else "?")

    splash = CarregamentoController()
    splash.show()
    splash.atualizar(85, "Carregando as janelas do sistema...")
    janela = MainWindowController()
    splash.atualizar(100, "Pronto")
    janela.showMaximized()
    splash.close()
    logger.info("Aplicação iniciada")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
