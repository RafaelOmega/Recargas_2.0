# -*- coding: utf-8 -*-
"""Controller da pesquisa de abastecimentos.

Ordenação padrão: coluna Sequência (DESCENDENTE — do maior para o
menor, ordenação NUMÉRICA). A coluna Data é exibida em formato
brasileiro (dd/mm/aaaa). Caminhão e Colaborador são POR ITEM: as
colunas mostram as PLACAS/nomes dos itens em uma única linha
(separados por vírgula) e a coluna Itens mostra os DESTINOS em linha.
Enter na grade confirma a seleção (como o duplo clique).

Modelo, debounce, conexões, tab order e erros comuns vêm de
PesquisaBase — aqui ficam apenas as colunas, a consulta e as linhas.
"""
from datetime import date, datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from app.controllers.pesquisa_base import PesquisaBase
from app.models.abastecimento import Abastecimento
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras
from app.views.ui_pesquisa_abastecimento import Ui_Pesquisa_Abastecimento

try:
    from app.services.abastecimento_service import AbastecimentoService
except ImportError:
    AbastecimentoService = None

try:
    from app.services.caminhao_service import CaminhaoService
except ImportError:
    CaminhaoService = None

logger = get_logger("pesquisa_abastecimentos")


class PesquisaAbastecimentoController(PesquisaBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Pesquisa_Abastecimento()
        self.ui.setupUi(self)

        self._service = (AbastecimentoService()
                         if AbastecimentoService else None)
        self._caminhao_service = (CaminhaoService()
                                  if CaminhaoService else None)
        self._grade = self.ui.tb_Abastecimento
        self._colunas = ["Sequência", "Data", "Caminhão", "Colaborador",
                         "Itens"]
        self._coluna_padrao = 0  # Sequência
        self._coluna_stretch = 4
        self._ordem_padrao = Qt.SortOrder.DescendingOrder

        # cadastro carregado ANTES do _inicializar: a carga inicial da
        # grade já mostra as placas na coluna Caminhão
        self._caminhoes = []
        self._carregar_caminhoes()

        self._inicializar()

    # ---------------- hooks do PesquisaBase ----------------

    def _nome_pesquisa(self) -> str:
        return "abastecimentos"

    def _consultar(self) -> list[Abastecimento]:
        filtro = self.ui.txt_Pesquisa.text().strip()
        return self._service.pesquisar(filtro)

    def _popular_lista(self, registros: list[Abastecimento]):
        self._modelo.removeRows(0, self._modelo.rowCount())
        for abastecimento in registros:
            data = self._para_data(abastecimento.data)
            caminhoes = self._caminhoes_em_linha(abastecimento)
            colaboradores = self._colaboradores_em_linha(abastecimento)
            itens = self._itens_em_linha(abastecimento)
            self._modelo.appendRow([
                # sequência como int no UserRole: ordenação numérica
                self._item_ordenavel(str(abastecimento.sequencia),
                                     abastecimento.sequencia),
                # exibição dd/mm/aaaa; ISO no UserRole: ordem cronológica
                self._item_ordenavel(
                    data.strftime("%d/%m/%Y"),
                    data.isoformat()),
                # vínculos são POR ITEM: placas dos itens em linha;
                # ordena pelo próprio texto
                self._item_ordenavel(caminhoes, caminhoes),
                # nomes dos colaboradores dos itens em linha;
                # ordena pelo próprio texto
                self._item_ordenavel(colaboradores, colaboradores),
                # destinos em linha; ordena pelo próprio texto
                self._item_ordenavel(itens, itens),
            ])
        # garante a ordenação padrão: Sequência, do maior para o menor
        self._modelo.sort(self._coluna_padrao, self._ordem_padrao)
        ajustar_larguras(self._grade, coluna_stretch=self._coluna_stretch)

    # ---------------- seleção (API consumida pelo lançamento) ----------------

    def abastecimento_selecionado(self) -> Abastecimento | None:
        """Abastecimento da linha selecionada (recarregado do banco)."""
        indice = self._grade.currentIndex()
        if not indice.isValid():
            return None
        item = self._modelo.item(indice.row(), 0)
        try:
            return self._service.buscar_por_sequencia(int(item.text()))
        except Exception as exc:
            logger.exception("Falha ao carregar abastecimento selecionado")
            QMessageBox.critical(
                self, "Erro",
                f"Falha ao carregar o abastecimento:\n{mensagem_erro(exc)}")
            return None

    # ---------------- auxiliares ----------------

    @staticmethod
    def _para_data(valor) -> date:
        """Aceita date, datetime ou texto (ISO ou brasileiro)."""
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        texto = str(valor).strip()[:10]
        try:
            return date.fromisoformat(texto)
        except ValueError:
            return datetime.strptime(texto, "%d/%m/%Y").date()

    def _caminhoes_em_linha(self, abastecimento: Abastecimento) -> str:
        """Placas de caminhão dos itens em uma única linha (sem repetir).

        A placa vem do cadastro carregado; se o caminhão não existe (ou
        não tem placa), cai ao código do snapshot.
        """
        placas = []
        for item in (abastecimento.itens or []):
            codigo = item.caminhao_codigo or ""
            if not codigo:
                continue
            placa = self._placa_caminhao(codigo) or codigo
            if placa not in placas:
                placas.append(placa)
        return ", ".join(placas)

    def _placa_caminhao(self, codigo: str) -> str:
        """Placa do caminhão no cadastro carregado ("" se não existe)."""
        for caminhao in self._caminhoes:
            if caminhao.codigo == codigo:
                return caminhao.placa or ""
        return ""

    def _carregar_caminhoes(self):
        """Carrega o cadastro para mostrar a placa na coluna Caminhão."""
        self._caminhoes = []
        if self._caminhao_service is None:
            return
        try:
            self._caminhoes = self._caminhao_service.pesquisar("")
        except Exception as exc:
            logger.exception("Falha ao carregar caminhões")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar caminhões:\n{exc}")

    @staticmethod
    def _colaboradores_em_linha(abastecimento: Abastecimento) -> str:
        """Nomes de colaborador dos itens em uma única linha (sem repetir)."""
        nomes = []
        for item in (abastecimento.itens or []):
            nome = item.colaborador_nome or ""
            if nome and nome not in nomes:
                nomes.append(nome)
        return ", ".join(nomes)

    @staticmethod
    def _itens_em_linha(abastecimento: Abastecimento) -> str:
        """Destinos dos itens em uma única linha (coluna Itens)."""
        destinos = [item.destino for item in (abastecimento.itens or [])
                    if item.destino]
        return ", ".join(destinos)
