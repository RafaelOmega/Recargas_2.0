# -*- coding: utf-8 -*-
"""Controller da janela principal (MDI) do sistema Recargas.

Responsabilidade: montar a UI, ligar as ações do menu às subjanelas
do QMdiArea e manter data/hora na barra de status.

Cada tela é uma chave em _TELAS; a factory do seu controller é
registrada em _criadores. Enquanto o controller real não existir,
um placeholder é exibido.
"""
from datetime import datetime

from PySide6.QtCore import QDate, QTime, QTimer
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from app.utils.logger import get_logger
from app.views.ui_main_window import Ui_MainWindow

logger = get_logger("main_window")

# chave -> (nome do QAction na UI, título da janela)
# Somente actions realmente adicionadas a um menu no Qt Designer.
# Ao adicionar/renomear actions no Designer, ajuste apenas este dicionário.
_TELAS = {
    "colaboradores": ("actionCad_Colaboradores", "Colaboradores"),
}


class MainWindowController(QMainWindow):
    """Janela principal (MDI) do sistema Recargas."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._criadores = {}   # chave -> factory do controller da tela
        self._subjanelas = {}  # chave -> QMdiSubWindow aberta

        self._configurar_status_bar()
        self._conectar_acoes()
        self._iniciar_relogio()

        logger.info("Janela principal iniciada")

    # ---------------- configuração ----------------

    def _configurar_status_bar(self):
        self.ui.lb_Comandos.setText("")
        self.ui.mdiArea.subWindowActivated.connect(self._ao_ativar_subjanela)

    def _conectar_acoes(self):
        """Liga cada QAction do menu à abertura da sua tela.

        Usa getattr: action ausente na UI é apenas ignorada (com aviso
        no log), então atualizar o Qt Designer não quebra o controller.
        """
        self._telas = {}
        for chave, (nome_acao, titulo) in _TELAS.items():
            acao = getattr(self.ui, nome_acao, None)
            if acao is None:
                logger.warning("Ação não encontrada na UI: %s", nome_acao)
                continue
            self._telas[chave] = (acao, titulo)
            acao.triggered.connect(
                lambda _checked=False, c=chave: self._abrir_tela(c)
            )

    def _iniciar_relogio(self):
        if not hasattr(self.ui, "dt_Data_Atual") or not hasattr(self.ui, "dt_Hora_Atual"):
            logger.warning(
                "Widgets de data/hora ausentes na UI — relógio desativado")
            return
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._atualizar_relogio)
        self._timer.start(1000)

    def _atualizar_relogio(self):
        agora = datetime.now()
        self.ui.dt_Data_Atual.setDate(
            QDate(agora.year, agora.month, agora.day))
        self.ui.dt_Hora_Atual.setTime(
            QTime(agora.hour, agora.minute, agora.second))

    def _ao_ativar_subjanela(self, sub):
        pass  # ponto de extensão (ex.: limpar lb_Comandos)

    # ---------------- abertura de telas ----------------

    def _abrir_tela(self, chave: str):
        titulo = self._telas[chave][1]

        sub = self._subjanelas.get(chave)
        if sub is not None:  # já aberta -> traz para frente
            sub.show()
            sub.raise_()
            self.ui.mdiArea.setActiveSubWindow(sub)
            return

        widget = self._criar_widget(chave, titulo)
        sub = self.ui.mdiArea.addSubWindow(widget)
        sub.setWindowTitle(titulo)
        sub.destroyed.connect(
            lambda _o=None, c=chave: self._subjanelas.pop(c, None))

        self._subjanelas[chave] = sub
        sub.show()
        logger.info("Tela aberta: %s", titulo)

    def _criar_widget(self, chave: str, titulo: str) -> QWidget:
        criador = self._criadores.get(chave)
        if criador is not None:
            return criador(self)

        # Placeholder até a tela ter seu próprio controller.
        # Exemplo de registro quando existir o controller real:
        #   self._criadores["colaboradores"] = lambda pai: CadColaboradoresController(pai)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        rotulo = QLabel(
            f"{titulo}\n(controller ainda não implementado)", widget)
        layout.addWidget(rotulo)
        return widget
