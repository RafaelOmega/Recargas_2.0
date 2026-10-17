# -*- coding: utf-8 -*-
"""Base das telas de pesquisa (colaboradores, usuários, saldo da conta,
caminhões e recargas).

Absorve o esqueleto comum às cinco telas — modelo com ordenação por
UserRole, debounce 300ms, conexões de sinais, tab order em modo Z,
Enter na grade e tratamento de erros — para que um ajuste comum seja
feito UMA vez aqui e valha para todas as pesquisas.

Contrato do filho:
  - no __init__: criar a UI (self.ui), definir self._service,
    self._grade, self._colunas, self._coluna_padrao,
    self._coluna_stretch, self._ordem_padrao e chamar
    self._inicializar() por último;
  - implementar: _nome_pesquisa(), _consultar() e _popular_lista();
  - o método público de seleção (colaborador_selecionado(),
    usuario_selecionado()...) fica no filho — é a API consumida pelos
    cadastros e o nome não muda.

Filtro de status (Ativos/Inativos): telas que possuem rb_Ativo têm os
radios conectados automaticamente (trocar o radio refaz a pesquisa).

Comportamentos unificados pela base:
  - bt_Pesquisa confirma com seleção; sem seleção, pesquisa;
  - _pesquisar para o debounce antes de consultar;
  - erros de consulta via app.utils.erros.mensagem_erro;
  - tab order automático: pesquisa -> (Ativos -> Inativos) -> Confirmar
    -> grade.
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (QKeySequence, QShortcut, QStandardItem,
                           QStandardItemModel)
from PySide6.QtWidgets import QDialog, QMessageBox

from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import configurar_tabela

logger = get_logger("pesquisa_base")

DEBOUNCE_MS = 300


class PesquisaBase(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

    # ---------------- fase 2 (chamada pelo filho) ----------------

    def _inicializar(self):
        """Monta modelo, conexões e tab order — chamar no fim do
        __init__ do filho, após definir _service, _grade e as colunas."""
        if getattr(self, "_service", None) is None:
            logger.warning("%s: service nao encontrado",
                           type(self).__name__)

        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(self._colunas)
        # ordenação (padrão e clique no cabeçalho) usa o UserRole —
        # EditRole no QStandardItem sobrescreve o texto exibido
        self._modelo.setSortRole(Qt.ItemDataRole.UserRole)
        self._grade.setModel(self._modelo)
        configurar_tabela(self._grade,
                          coluna_stretch=self._coluna_stretch,
                          ordenavel=True)
        # ordenação padrão da tela (coluna e sentido definidos pelo filho)
        self._grade.sortByColumn(self._coluna_padrao, self._ordem_padrao)

        self._timer_filtro = QTimer(self)
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._pesquisar)

        self._conectar_eventos()
        self._definir_tab_order()
        self._pesquisar()

    # ---------------- conexões ----------------

    def _conectar_eventos(self):
        self.ui.txt_Pesquisa.textChanged.connect(self._agendar_filtro)
        # telas com filtro de status: trocar o radio refaz a pesquisa
        if hasattr(self.ui, "rb_Ativo"):
            self.ui.rb_Ativo.toggled.connect(self._agendar_filtro)
        self.ui.bt_Pesquisa.clicked.connect(self._confirmar)
        self.ui.txt_Pesquisa.returnPressed.connect(self._pesquisar)
        self._grade.doubleClicked.connect(self.accept)
        # Enter na grade confirma como o duplo clique
        self._at_enter_grade = QShortcut(
            QKeySequence(Qt.Key.Key_Return), self._grade)
        self._at_enter_grade.activated.connect(self._confirmar)

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z: pesquisa -> (Ativos -> Inativos)
        -> Confirmar -> grade (radios entram só quando existirem)."""
        ordem = [self.ui.txt_Pesquisa]
        if hasattr(self.ui, "rb_Ativo"):
            ordem += [self.ui.rb_Ativo, self.ui.rb_Inativo]
        ordem += [self.ui.bt_Pesquisa, self._grade]
        for atual, proximo in zip(ordem, ordem[1:]):
            self.setTabOrder(atual, proximo)

    # ---------------- filtro ----------------

    def _agendar_filtro(self):
        self._timer_filtro.start(DEBOUNCE_MS)

    # ---------------- ações ----------------

    def _confirmar(self):
        """Confirmar: com seleção, devolve o registro;
        sem seleção, apenas pesquisa."""
        if self._grade.currentIndex().isValid():
            self.accept()
        else:
            self._pesquisar()

    def _pesquisar(self):
        """Para o debounce, consulta o service e popula a grade."""
        self._timer_filtro.stop()
        if self._service is None:
            return
        try:
            registros = self._consultar()
        except Exception as exc:
            logger.exception("Falha ao pesquisar %s",
                             self._nome_pesquisa())
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível pesquisar:\n{mensagem_erro(exc)}")
            return
        self._popular_lista(registros)

    # ---------------- auxiliares ----------------

    @staticmethod
    def _item_ordenavel(texto: str, valor_ordenacao) -> QStandardItem:
        """Item que exibe texto mas ordena pelo valor informado."""
        item = QStandardItem(texto)
        item.setData(valor_ordenacao, Qt.ItemDataRole.UserRole)
        return item

    # ---------------- hooks do filho (obrigatórios) ----------------

    def _nome_pesquisa(self) -> str:
        """Nome para logs: 'colaboradores', 'recargas'..."""
        raise NotImplementedError

    def _consultar(self) -> list:
        """Consulta o service com os filtros da tela e devolve a lista."""
        raise NotImplementedError

    def _popular_lista(self, registros: list):
        """Limpa a grade e popula as linhas (terminar com
        ajustar_larguras(self._grade,
                         coluna_stretch=self._coluna_stretch))."""
        raise NotImplementedError
