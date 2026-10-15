# -*- coding: utf-8 -*-
"""Controller da tela de Dashboard de Recargas Refeição (Power BI).

Exibe o relatório do Power BI Service dentro do sistema, via
QWebEngineView (navegador embutido). O usuário autentica com a
conta Microsoft na primeira abertura — o login fica salvo no
perfil do WebEngine e as aberturas seguintes entram direto.

A URL do relatório vem da variável de ambiente POWERBI_REFEICAO_URL
(defina nas Variáveis de Ambiente do Windows). Use a URL de
incorporação segura do relatório: no Power BI Service,
Arquivo -> Incorporar relatório -> "Portal da Web seguro".
"""
import os

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget

from app.utils.logger import get_logger
from app.views.ui_dashboard_refeicao import Ui_Dash_Refeicao

logger = get_logger("dashboard_refeicao")

# fallback se a variável não estiver definida (cole a URL aqui se preferir)
URL_PADRAO = ""

# aviso exibido no navegador quando a URL não está configurada
_HTML_SEM_URL = (
    "<html><body style='background:#131B2F;color:#FFFFFF;"
    "font-family:Segoe UI Semibold;font-size:14pt;'>"
    "<p style='text-align:center;margin-top:120px;'>"
    "Dashboard n&atilde;o configurado.<br><br>"
    "Defina a vari&aacute;vel de ambiente POWERBI_REFEICAO_URL com a "
    "URL de incorpora&ccedil;&atilde;o segura do relat&oacute;rio "
    "(Power BI Service -&gt; Arquivo -&gt; Incorporar relat&oacute;rio "
    "-&gt; Portal da Web seguro)."
    "</p></body></html>"
)


class DashRefeicaoController(QWidget):
    """Dashboard do Power BI (Recargas Refeição) embutido no sistema."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Dash_Refeicao()
        self.ui.setupUi(self)

        self._url = (os.environ.get("POWERBI_REFEICAO_URL", "").strip()
                     or URL_PADRAO)

        if not self._url:
            self.ui.webEngineView.setHtml(_HTML_SEM_URL)
            logger.warning(
                "POWERBI_REFEICAO_URL não definida — dashboard vazio")
            return

        self.ui.webEngineView.load(QUrl(self._url))
        logger.info("Dashboard carregado: %s", self._url)
