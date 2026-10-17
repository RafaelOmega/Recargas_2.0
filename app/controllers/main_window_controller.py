# -*- coding: utf-8 -*-
"""Controller da janela principal (MDI) do sistema Recargas.

Responsabilidade: montar a UI, ligar as ações do menu às subjanelas
do QMdiArea e manter data/hora, o saldo da conta e a indicação da
tela ativa na barra de status.

Cada tela é uma chave em _TELAS; a factory do seu controller é
registrada em _criadores.

Navegação por teclado (sem depender do mouse):
  - Ctrl+1..Ctrl+7 abre cada tela na ordem do _TELAS (se já aberta,
    apenas traz para frente);
  - Ctrl+Tab / Ctrl+Shift+Tab alternam a subjanela ativa
    (próxima/anterior);
  - Ctrl+F4 fecha a subjanela ativa;
  - F1 abre a ajuda de atalhos (diálogo modal) — a lista nasce de
    _TELAS (fonte única): reordenar/adicionar telas atualiza a ajuda
    sozinho, sem tocar no .ui.

Multiusuário: o saldo é recalculado no banco (nunca em cache) e o
service é recriado automaticamente se a conexão morrer (queda de
rede ou restart do PostgreSQL) — na próxima atualização ele volta.
"""
from datetime import datetime

from PySide6.QtCore import QDate, QTime, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QDialog, QLabel, QMainWindow,
                               QPushButton, QTextBrowser, QVBoxLayout,
                               QWidget)

from app.controllers.cad_caminhoes_controller import (
    CadCaminhoesController,
)
from app.controllers.cad_colaboradores_controller import (
    CadColaboradoresController,
)
from app.controllers.cad_saldo_conta_controller import (
    CadSaldoContaController,
)
from app.controllers.cad_usuarios_controller import (
    CadUsuariosController,
)
from app.controllers.dashboard_refeicao_controller import (
    DashRefeicaoController,
)
from app.controllers.lancamento_recargas_controller import (
    LancamentoRecargasController,
)
from app.controllers.relatorio_recarga_colaborador_controller import (
    RelRecargaColaboradorController,
)
from app.utils.logger import get_logger
from app.version import __version__
from app.views.ui_main_window import Ui_MainWindow

try:
    from app.services.saldo_conta_service import SaldoContaService
except ImportError:
    SaldoContaService = None

logger = get_logger("main_window")

# chave -> (nome do QAction na UI, título da janela)
# Somente actions realmente adicionadas a um menu no Qt Designer.
# Ao adicionar/renomear actions no Designer, ajuste apenas este dicionário.
# A ORDEM define os atalhos globais: Ctrl+1 abre a primeira, Ctrl+7 a última.
_TELAS = {
    "colaboradores": ("actionCad_Colaboradores", "Colaboradores"),
    "caminhoes": ("actionCaminhoes", "Caminhões"),
    "usuarios": ("actionUsuarios", "Usuários"),
    "recargas": ("actionRecargas", "Lançamento de Recargas"),
    "saldo_biz": ("actionSaldo_BIZ", "Saldo BIZ"),
    "rel_recarga_colaborador": ("actionRecarga_Colaborador",
                                "Recarga por Colaborador"),
    "dash_refeicao": ("actionDash_Refeicao", "Dashboard Refeição"),
}
# intervalo de atualização automática do saldo da conta (30 s)
INTERVALO_SALDO_MS = 30_000
# estilo do campo de saldo (chip sobre a barra azul da barra de status)
_ESTILO_SALDO = (
    "QLineEdit{background:rgba(255,255,255,0.12);"
    "border:1px solid #2E5A8F;border-radius:4px;"
    "padding:2px 8px;color:#FFFFFF;}"
)
_ESTILO_SALDO_NEGATIVO = (
    "QLineEdit{background:rgba(255,255,255,0.12);"
    "border:1px solid #C0392B;border-radius:4px;"
    "padding:2px 8px;color:#FF8A80;font-weight:bold;}"
)
# estilo da ajuda de atalhos (F1): fundo escuro consistente com o tema
_ESTILO_AJUDA = (
    "QTextBrowser{background:#16222F;color:#D5DDE8;"
    "border:1px solid #2E5A8F;border-radius:4px;padding:10px;}"
)


def _formatar_moeda(valor: float) -> str:
    """Float -> 'R$ 1.234,56' (padrão brasileiro, sinal na frente)."""
    texto = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",")
    texto = texto.replace("X", ".")
    sinal = "-" if valor < 0 else ""
    return f"{sinal}R$ {texto}"


class MainWindowController(QMainWindow):
    """Janela principal (MDI) do sistema Recargas."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._criadores = {}   # chave -> factory do controller da tela
        self._subjanelas = {}  # chave -> QMdiSubWindow aberta

        self._service_saldo = (SaldoContaService()
                               if SaldoContaService else None)

        self._configurar_status_bar()
        self._conectar_acoes()
        self._conectar_navegacao()
        self._iniciar_relogio()
        self._iniciar_atualizacao_saldo()

        logger.info("Janela principal iniciada")

        self._criadores["colaboradores"] = lambda pai: CadColaboradoresController(
            pai)
        self._criadores["caminhoes"] = lambda pai: CadCaminhoesController(
            pai)
        self._criadores["usuarios"] = lambda pai: CadUsuariosController(
            pai)
        self._criadores["recargas"] = lambda pai: LancamentoRecargasController(
            pai)
        self._criadores["saldo_biz"] = lambda pai: CadSaldoContaController(
            pai)
        self._criadores["rel_recarga_colaborador"] = lambda pai: (
            RelRecargaColaboradorController(pai))
        self._criadores["dash_refeicao"] = lambda pai: (
            DashRefeicaoController(pai))

    # ---------------- configuração ----------------

    def _configurar_status_bar(self):
        self.ui.lb_Comandos.setText("")
        # versão do sistema: fonte única em app/version.py — o texto
        # fixo do .ui é sobrescrito aqui a cada abertura
        if hasattr(self.ui, "lb_Versao"):
            self.ui.lb_Versao.setText(f"Versão {__version__}")
        self.ui.mdiArea.subWindowActivated.connect(self._ao_ativar_subjanela)

    def _conectar_acoes(self):
        """Liga cada QAction do menu à abertura da sua tela.

        Usa getattr: action ausente na UI é apenas ignorada (com aviso
        no log), então atualizar o Qt Designer não quebra o controller.
        Cada tela ganha o atalho global Ctrl+N conforme a posição no
        _TELAS (Ctrl+1 = primeira, Ctrl+7 = última).
        """
        self._telas = {}
        for indice, (chave, (nome_acao, titulo)) in enumerate(
                _TELAS.items(), start=1):
            acao = getattr(self.ui, nome_acao, None)
            if acao is None:
                logger.warning("Ação não encontrada na UI: %s", nome_acao)
                continue
            self._telas[chave] = (acao, titulo)
            acao.setShortcut(QKeySequence(f"Ctrl+{indice}"))
            acao.triggered.connect(
                lambda _checked=False, c=chave: self._abrir_tela(c)
            )

    def _conectar_navegacao(self):
        """Atalhos de navegação entre subjanelas (padrão MDI).

        Ctrl+Tab / Ctrl+Shift+Tab: próxima/anterior subjanela aberta.
        Ctrl+F4: fecha a subjanela ativa. F1: ajuda de atalhos.
        Contexto de janela: valem enquanto a janela principal estiver
        ativa, sem roubar teclas de diálogos modais (login, pesquisas).
        """
        self._at_proxima = QShortcut(QKeySequence("Ctrl+Tab"), self)
        self._at_proxima.activated.connect(
            self.ui.mdiArea.activateNextSubWindow)
        self._at_anterior = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        self._at_anterior.activated.connect(
            self.ui.mdiArea.activatePreviousSubWindow)
        self._at_fechar = QShortcut(QKeySequence("Ctrl+F4"), self)
        self._at_fechar.activated.connect(self._fechar_ativa)
        self._at_ajuda = QShortcut(QKeySequence("F1"), self)
        self._at_ajuda.activated.connect(self._abrir_ajuda)

    def _html_atalhos(self) -> str:
        """HTML da lista de atalhos — nasce de _TELAS (fonte única).

        Reordenar/adicionar telas atualiza a ajuda automaticamente.
        """
        itens = "".join(
            f"<tr><td style='padding:2px 10px 2px 0;white-space:nowrap;'>"
            f"<b>Ctrl+{indice}</b></td>"
            f"<td style='padding:2px 0;'>{titulo}</td></tr>"
            for indice, (_, titulo) in enumerate(_TELAS.values(), start=1))
        return (
            "<html><body style='color:#D5DDE8;'>"
            "<h3 style='color:#FFFFFF;margin:0 0 6px 0;'>Atalhos do "
            "sistema</h3>"
            "<table cellspacing='0' cellpadding='0'>"
            f"{itens}"
            "<tr><td style='padding:2px 10px 2px 0;white-space:nowrap;'>"
            "<b>Ctrl+Tab</b></td>"
            "<td style='padding:2px 0;'>Próxima tela aberta</td></tr>"
            "<tr><td style='padding:2px 10px 2px 0;white-space:nowrap;'>"
            "<b>Ctrl+Shift+Tab</b></td>"
            "<td style='padding:2px 0;'>Tela anterior</td></tr>"
            "<tr><td style='padding:2px 10px 2px 0;white-space:nowrap;'>"
            "<b>Ctrl+F4</b></td>"
            "<td style='padding:2px 0;'>Fecha a tela ativa</td></tr>"
            "<tr><td style='padding:2px 10px 2px 0;white-space:nowrap;'>"
            "<b>F2</b></td>"
            "<td style='padding:2px 0;'>Novo registro (nas telas de "
            "cadastro e no lançamento)</td></tr>"
            "<tr><td style='padding:2px 10px 2px 0;white-space:nowrap;'>"
            "<b>F1</b></td>"
            "<td style='padding:2px 0;'>Esta ajuda</td></tr>"
            "</table></body></html>")

    def _abrir_ajuda(self):
        """F1: diálogo modal com a lista de atalhos (tema escuro).

        Construído em código — não depende do .ui. Esc ou o botão
        fecham.
        """
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Atalhos do sistema")
        layout = QVBoxLayout(dialogo)
        navegador = QTextBrowser(dialogo)
        navegador.setStyleSheet(_ESTILO_AJUDA)
        navegador.setHtml(self._html_atalhos())
        navegador.setOpenExternalLinks(False)
        layout.addWidget(navegador)
        botao = QPushButton("Fechar (Esc)", dialogo)
        botao.clicked.connect(dialogo.accept)
        layout.addWidget(botao)
        dialogo.exec()

    def _fechar_ativa(self):
        """Fecha a subjanela ativa (Ctrl+F4); sem ativa, não faz nada."""
        sub = self.ui.mdiArea.activeSubWindow()
        if sub is not None:
            sub.close()

    def _iniciar_relogio(self):
        if not hasattr(self.ui, "dt_Data_Atual") or not hasattr(
                self.ui, "dt_Hora_Atual"):
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

    # ---------------- saldo da conta (barra de status) ----------------
    def _iniciar_atualizacao_saldo(self):
        """Saldo na abertura + refresh periódico (cobre multiusuário)."""
        if not hasattr(self.ui, "txt_Saldo_Conta"):
            logger.warning(
                "txt_Saldo_Conta ausente na UI — saldo desativado")
            return
        self._atualizar_saldo_conta()
        self._timer_saldo = QTimer(self)
        self._timer_saldo.timeout.connect(self._atualizar_saldo_conta)
        self._timer_saldo.start(INTERVALO_SALDO_MS)

    def _atualizar_saldo_conta(self):
        """Saldo da conta Biz = soma das recargas - soma dos saldos.

        Se a consulta falhar (conexão morta após queda de rede ou
        restart do banco), o service é descartado: no próximo ciclo
        um novo service — com conexão nova — é criado sozinho.
        """
        if self._service_saldo is None:
            # recria o service (reconexão) — se a dependência existir
            self._service_saldo = (SaldoContaService()
                                   if SaldoContaService else None)
        if self._service_saldo is None:
            self.ui.txt_Saldo_Conta.setText("—")
            return
        try:
            saldo = self._service_saldo.saldo_atual()
        except Exception:
            logger.exception("Falha ao calcular o saldo da conta")
            # conexão provavelmente morta: descarta para reconectar
            self._service_saldo = None
            self.ui.txt_Saldo_Conta.setText("—")
            return
        self.ui.txt_Saldo_Conta.setText(_formatar_moeda(saldo))
        # negativo destacado: borda e texto vermelhos, chip mantido
        self.ui.txt_Saldo_Conta.setStyleSheet(
            _ESTILO_SALDO_NEGATIVO if saldo < 0 else _ESTILO_SALDO)

    def _ao_ativar_subjanela(self, sub):
        """Informa a tela ativa na barra de status e atualiza o saldo.

        sub é None quando a última subjanela é fechada — o indicador
        de tela é limpo.
        """
        if sub is None:
            self.ui.lb_Comandos.setText("")
        else:
            self.ui.lb_Comandos.setText(sub.windowTitle())
        # ao voltar/focus de uma subjanela (ex.: após salvar), atualiza
        self._atualizar_saldo_conta()

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
        # indicador da tela ativa (subWindowActivated também cobre;
        # o set explícito garante na abertura)
        self.ui.lb_Comandos.setText(titulo)
        logger.info("Tela aberta: %s", titulo)

    def _criar_widget(self, chave: str, titulo: str) -> QWidget:
        criador = self._criadores.get(chave)
        if criador is not None:
            return criador(self)

        # Placeholder até a tela ter seu próprio controller.
        widget = QWidget()
        layout = QVBoxLayout(widget)
        rotulo = QLabel(
            f"{titulo}\n(controller ainda não implementado)", widget)
        layout.addWidget(rotulo)
        return widget
