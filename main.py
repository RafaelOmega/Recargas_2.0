# -*- coding: utf-8 -*-
"""Ponto de entrada do sistema Recargas."""
import sys

from PySide6.QtWidgets import QApplication

from app.controllers.main_window_controller import MainWindowController
from app.database.schema import criar_schema
from app.utils.icons import aplicar_icone_aplicacao
from app.utils.logger import get_logger, setup_logging
from app.utils.theme import aplicar_tema

logger = get_logger("main")


def main() -> int:
    setup_logging()
    logger.info("Iniciando sistema Recargas")

    criar_schema()  # idempotente: cria as tabelas que não existirem

    app = QApplication(sys.argv)
    aplicar_tema(app)
    aplicar_icone_aplicacao(app)

    janela = MainWindowController()
    janela.show()

    codigo = app.exec()
    logger.info("Sistema finalizado (código %s)", codigo)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
