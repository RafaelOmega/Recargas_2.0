# -*- coding: utf-8 -*-
"""Controller do lançamento de abastecimentos.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao AbastecimentoService (cabeçalho +
itens na mesma transação), ao CaminhaoService e ao ColaboradorService
(seleção de vínculos).

Vínculos POR ITEM: caminhão e colaborador pertencem a cada item da
grade (não ao cabeçalho, que fica só com sequência e data). Com o
lançamento aberto, digite o código e pressione Enter (campo vazio +
Enter abre a pesquisa) ou clique em "..." — a descrição (modelo/nome)
é preenchida automaticamente e fica somente leitura; digitar no
código invalida a seleção.

Fluxo mestre-detalhe:
  - "+" prepara um novo abastecimento: escolhe a data e clica em
    "Abrir Abastecimento" para liberar a inclusão de itens;
  - "..." abre a pesquisa e carrega o abastecimento selecionado;
  - "Abrir Abastecimento" habilita o fluxo próprio dos itens (em
    registro novo E na edição): cada item é confirmado em memória
    (grade) com o botão Confirmar; duplo clique OU Enter num item da
    grade o recarrega nos campos para edição (o Confirmar atualiza a
    linha em vez de adicionar outra);
  - "Sair Abastecimento" finaliza o lançamento dos itens e libera o
    bt_Salvar — enquanto o abastecimento está aberto, salvar é
    bloqueado;
  - Salvar grava cabeçalho e itens de uma vez (na edição os itens são
    substituídos).

A sequência é automática (gerada no salvar), mas o campo
txt_Abastecimento fica HABILITADO no estado inicial como campo de
busca: digitar uma sequência e Enter carrega o abastecimento direto
do banco (mesmo resultado de selecionar na pesquisa); Enter com o
campo vazio abre a pesquisa completa. Em novo/edição o campo volta a
bloquear (a sequência é gerada ou é a chave do update).

Last-write-wins: a versão carregada (atualizado_em) fica guardada em
_abastecimento_carregado no _preencher e é enviada no salvar em
edição; alterado por outro usuário, o service levanta
ConflitoEdicaoError — a tela avisa e recarrega a versão mais recente
em vez de sobrescrever calado.

Navegação (Tab) em modo Z: esquerda para a direita e de cima
para baixo — com o abastecimento aberto, os widgets fora do fluxo
de itens estão desabilitados e são pulados pelo Qt.
"""
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import (QKeySequence, QShortcut, QStandardItem,
                           QStandardItemModel)
from PySide6.QtWidgets import QMessageBox, QWidget

from app.models.caminhao import Caminhao
from app.models.colaborador import Colaborador
from app.utils.erros import ConflitoEdicaoError, mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_lancamento_abastecimento import (
    Ui_Lancamento_Abastecimento,
)

try:
    from app.services.abastecimento_service import AbastecimentoService
except ImportError:
    AbastecimentoService = None

try:
    from app.services.caminhao_service import CaminhaoService
except ImportError:
    CaminhaoService = None

try:
    from app.services.colaborador_service import ColaboradorService
except ImportError:
    ColaboradorService = None

logger = get_logger("lancamento_abastecimentos")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"       # aguardando "Abrir Abastecimento"
ESTADO_ABERTA = "aberta"   # lançando/editando itens em memória
ESTADO_PRONTA = "pronta"   # itens finalizados; salvar liberado
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"   # carregado e liberado para edição

# grade: código do colaborador fica no Qt.UserRole da célula 2
COLUNAS_ITENS = ["Caminhão", "Modelo", "Colaborador", "Destino",
                 "KM Início", "KM Final", "Litros"]
COLUNA_STRETCH_ITENS = 0


class LancamentoAbastecimentoController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Lancamento_Abastecimento()
        self.ui.setupUi(self)

        self._service = (AbastecimentoService()
                         if AbastecimentoService else None)
        self._caminhao_service = (CaminhaoService()
                                  if CaminhaoService else None)
        self._colaborador_service = (ColaboradorService()
                                     if ColaboradorService else None)
        if self._service is None:
            logger.warning(
                "AbastecimentoService nao encontrado - acoes desativadas")

        self._modo = ESTADO_INICIAL
        self._item_em_edicao: int | None = None  # linha da grade em edição
        self._caminhoes = []                     # cadastro p/ reedição
        self._colaboradores = []                 # cadastro p/ reedição
        self._caminhao_selecionado: Caminhao | None = None
        self._colaborador_selecionado: Colaborador | None = None
        self._abastecimento_carregado = None  # versão p/ last-write-wins

        self.ui.txt_Total.setReadOnly(True)
        self.ui.txt_Modelo.setReadOnly(True)  # descrição vem do código
        self.ui.txt_Nome.setReadOnly(True)    # descrição vem do código
        self.ui.dbs_Litros.setDecimals(2)
        self.ui.dbs_Litros.setMaximum(9999999.0)

        self._montar_grade()
        self._conectar_botoes()
        self._conectar_teclas()
        self._definir_tab_order()
        self._carregar_caminhoes()
        self._carregar_colaboradores()
        self._limpar_campos()
        self.ui.txt_Abastecimento.setFocus()

    # ---------------- configuracao ----------------

    def _montar_grade(self):
        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(COLUNAS_ITENS)
        self.ui.tb_Itens.setModel(self._modelo)
        configurar_tabela(self.ui.tb_Itens,
                          coluna_stretch=COLUNA_STRETCH_ITENS,
                          ordenavel=False)
        self.ui.tb_Itens.setEditTriggers(
            self.ui.tb_Itens.EditTrigger.NoEditTriggers)

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self.ui.bt_Pesquisar_Abastecimentos.clicked.connect(self._pesquisar)
        self.ui.bt_Abrir_Abastecimento.clicked.connect(
            self._abrir_abastecimento)
        self.ui.bt_Pesquisar_Caminhao.clicked.connect(
            self._pesquisar_caminhao)
        self.ui.bt_Pesquisar_Colaborador.clicked.connect(
            self._pesquisar_colaborador)
        self.ui.bt_Confirmar_Item.clicked.connect(self._confirmar_item)
        self.ui.bt_Limpar_Item.clicked.connect(self._limpar_item)
        self.ui.bt_Excluir_Item.clicked.connect(self._excluir_item)
        self.ui.bt_Sair_Abastecimento.clicked.connect(
            self._sair_abastecimento)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        # Enter na sequência: com texto busca direto; vazio abre a pesquisa
        self.ui.txt_Abastecimento.returnPressed.connect(
            self._enter_abastecimento)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)
        # duplo clique na grade carrega o item para edição
        self.ui.tb_Itens.doubleClicked.connect(self._carregar_item_edicao)
        # Enter na grade carrega o item para edição (como o duplo clique)
        self._at_enter_grade = QShortcut(
            QKeySequence(Qt.Key.Key_Return), self.ui.tb_Itens)
        self._at_enter_grade.activated.connect(self._enter_grade_itens)
        # vínculos do item: Enter resolve; digitar invalida a seleção
        self.ui.txt_Cod_Caminhao.returnPressed.connect(
            self._buscar_caminhao_por_codigo)
        self.ui.txt_Cod_Caminhao.textEdited.connect(
            self._caminhao_digitado)
        self.ui.txt_Cod_Colaborador.returnPressed.connect(
            self._buscar_colaborador_por_codigo)
        self.ui.txt_Cod_Colaborador.textEdited.connect(
            self._colaborador_digitado)

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda->direita, cima->baixo).

        Com o abastecimento aberto, os widgets fora do fluxo de itens
        estão desabilitados e o Z efetivo fica restrito aos itens
        (vínculos incluídos — são do item).
        """
        self.setTabOrder(self.ui.txt_Abastecimento,
                         self.ui.bt_Pesquisar_Abastecimentos)
        self.setTabOrder(self.ui.bt_Pesquisar_Abastecimentos,
                         self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.dt_Data)
        self.setTabOrder(self.ui.dt_Data, self.ui.bt_Abrir_Abastecimento)
        self.setTabOrder(self.ui.bt_Abrir_Abastecimento,
                         self.ui.txt_Cod_Caminhao)
        self.setTabOrder(self.ui.txt_Cod_Caminhao,
                         self.ui.bt_Pesquisar_Caminhao)
        self.setTabOrder(self.ui.bt_Pesquisar_Caminhao,
                         self.ui.txt_Modelo)
        self.setTabOrder(self.ui.txt_Modelo, self.ui.txt_Cod_Colaborador)
        self.setTabOrder(self.ui.txt_Cod_Colaborador,
                         self.ui.bt_Pesquisar_Colaborador)
        self.setTabOrder(self.ui.bt_Pesquisar_Colaborador,
                         self.ui.txt_Nome)
        self.setTabOrder(self.ui.txt_Nome, self.ui.txt_Destino)
        self.setTabOrder(self.ui.txt_Destino, self.ui.spn_KM_Inicio)
        self.setTabOrder(self.ui.spn_KM_Inicio, self.ui.spn_KM_Final)
        self.setTabOrder(self.ui.spn_KM_Final, self.ui.dbs_Litros)
        self.setTabOrder(self.ui.dbs_Litros, self.ui.bt_Confirmar_Item)
        self.setTabOrder(self.ui.bt_Confirmar_Item, self.ui.tb_Itens)
        self.setTabOrder(self.ui.tb_Itens, self.ui.bt_Limpar_Item)
        self.setTabOrder(self.ui.bt_Limpar_Item, self.ui.bt_Excluir_Item)
        self.setTabOrder(self.ui.bt_Excluir_Item,
                         self.ui.bt_Sair_Abastecimento)
        self.setTabOrder(self.ui.bt_Sair_Abastecimento, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    # ---------------- estados da tela ----------------

    def _area_vinculos(self, habilitar: bool):
        """Habilita/desabilita os vínculos DO ITEM (caminhão e
        colaborador) — ativos junto com o fluxo de itens."""
        self.ui.txt_Cod_Caminhao.setEnabled(habilitar)
        self.ui.bt_Pesquisar_Caminhao.setEnabled(habilitar)
        self.ui.txt_Modelo.setEnabled(habilitar)
        self.ui.txt_Cod_Colaborador.setEnabled(habilitar)
        self.ui.bt_Pesquisar_Colaborador.setEnabled(habilitar)
        self.ui.txt_Nome.setEnabled(habilitar)

    def _area_itens(self, habilitar: bool):
        """Habilita/desabilita o fluxo próprio dos itens."""
        self.ui.txt_Destino.setEnabled(habilitar)
        self.ui.spn_KM_Inicio.setEnabled(habilitar)
        self.ui.spn_KM_Final.setEnabled(habilitar)
        self.ui.dbs_Litros.setEnabled(habilitar)
        self.ui.bt_Confirmar_Item.setEnabled(habilitar)
        self.ui.bt_Limpar_Item.setEnabled(habilitar)
        self.ui.bt_Excluir_Item.setEnabled(habilitar)
        self.ui.bt_Sair_Abastecimento.setEnabled(habilitar)

    def _estado_inicial(self):
        self.ui.txt_Abastecimento.setEnabled(True)  # busca liberada
        self.ui.bt_Pesquisar_Abastecimentos.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self.ui.dt_Data.setEnabled(False)
        self.ui.bt_Abrir_Abastecimento.setEnabled(False)
        self._area_vinculos(False)
        self._area_itens(False)

        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Abastecimento.setEnabled(False)  # sequência automática
        self.ui.txt_Abastecimento.clear()
        self.ui.bt_Pesquisar_Abastecimentos.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(True)
        self.ui.dt_Data.setDate(QDate.currentDate())
        self.ui.bt_Abrir_Abastecimento.setEnabled(True)
        self._area_vinculos(False)  # liberam ao clicar em Abrir
        self._area_itens(False)  # liberada ao clicar em Abrir Abastecimento

        self.ui.bt_Salvar.setEnabled(False)  # só após "Sair Abastecimento"
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)

    def _estado_aberta(self):
        """Abastecimento aberto: fluxo de itens ativo, salvar bloqueado."""
        self.ui.txt_Abastecimento.setEnabled(False)
        self.ui.bt_Pesquisar_Abastecimentos.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(False)  # data travada no lançamento
        self.ui.bt_Abrir_Abastecimento.setEnabled(False)
        self._area_vinculos(True)   # vínculos são do item
        self._area_itens(True)

        self.ui.bt_Salvar.setEnabled(False)  # só após "Sair Abastecimento"
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)

    def _estado_pronta(self):
        """Itens finalizados: salvar liberado."""
        self.ui.txt_Abastecimento.setEnabled(False)
        self.ui.bt_Pesquisar_Abastecimentos.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(False)
        self.ui.bt_Abrir_Abastecimento.setEnabled(False)
        self._area_vinculos(False)
        self._area_itens(False)

        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(
            bool(self.ui.txt_Abastecimento.text().strip()))
        self.ui.bt_Limpar.setEnabled(True)

    def _estado_visualizacao(self):
        self.ui.txt_Abastecimento.setEnabled(False)
        self.ui.bt_Pesquisar_Abastecimentos.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(False)
        self.ui.bt_Abrir_Abastecimento.setEnabled(False)
        self._area_vinculos(False)
        self._area_itens(False)

        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)

    def _estado_edicao(self):
        """Carregado e liberado: data editável; salvar e itens exigem
        o ciclo Abrir Abastecimento -> Sair Abastecimento."""
        self.ui.txt_Abastecimento.setEnabled(False)  # sequência é a chave
        self.ui.bt_Pesquisar_Abastecimentos.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(True)
        self.ui.bt_Abrir_Abastecimento.setEnabled(True)
        self._area_vinculos(False)
        self._area_itens(False)

        self.ui.bt_Salvar.setEnabled(False)  # só após "Sair Abastecimento"
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(
            exc,
            duplicidade="Já existe um abastecimento com essa sequência.")

    # ---------------- acoes de tela ----------------

    def _iniciar_novo(self):
        self._limpar_campos()
        self._modo = ESTADO_NOVO
        self._estado_novo()
        self.ui.dt_Data.setFocus()

    def _novo(self):
        if self._modo != ESTADO_INICIAL:
            return
        self._iniciar_novo()

    def _liberar_edicao(self):
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self.ui.dt_Data.setFocus()

    def _abrir_abastecimento(self):
        """Abre o lançamento dos itens em memória (vínculos são do item
        e são informados linha a linha)."""
        if self._modo not in (ESTADO_NOVO, ESTADO_EDICAO):
            return
        self._modo = ESTADO_ABERTA
        self._item_em_edicao = None
        self._estado_aberta()
        self.ui.txt_Cod_Caminhao.setFocus()

    def _sair_abastecimento(self):
        """Finaliza o lançamento dos itens e libera o botão Salvar."""
        if self._modo != ESTADO_ABERTA:
            return
        self._item_em_edicao = None
        self._limpar_item()
        self._modo = ESTADO_PRONTA
        self._estado_pronta()
        self.ui.bt_Salvar.setFocus()

    def _pesquisar(self):
        """Abre a pesquisa e carrega o abastecimento selecionado."""
        from app.controllers.pesquisa_abastecimento_controller import (
            PesquisaAbastecimentoController,
        )
        try:
            dialogo = PesquisaAbastecimentoController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa de abastecimentos")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            abastecimento = dialogo.abastecimento_selecionado()
            if abastecimento:
                self._preencher(abastecimento)

    def _enter_abastecimento(self):
        """Enter na sequência: com texto busca direto; vazio abre pesquisa."""
        if self.ui.txt_Abastecimento.text().strip():
            self._buscar_abastecimento_por_sequencia()
        else:
            self._pesquisar()

    def _buscar_abastecimento_por_sequencia(self):
        """Carrega o abastecimento da sequência digitada direto do banco."""
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de abastecimentos indisponível.")
            return
        texto = self.ui.txt_Abastecimento.text().strip()
        if not texto.isdigit():
            QMessageBox.warning(
                self, "Atenção", "Informe uma sequência numérica.")
            self.ui.txt_Abastecimento.setFocus()
            self.ui.txt_Abastecimento.selectAll()
            return
        try:
            abastecimento = self._service.buscar_por_sequencia(int(texto))
        except Exception as exc:
            logger.exception("Falha ao buscar abastecimento %s", texto)
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o abastecimento:"
                f"\n{self._mensagem_erro(exc)}")
            return
        if abastecimento is None:
            QMessageBox.information(
                self, "Não encontrado",
                f"Abastecimento {texto} não encontrado.")
            self.ui.txt_Abastecimento.setFocus()
            self.ui.txt_Abastecimento.selectAll()
            return
        self._preencher(abastecimento)

    def _validar_obrigatorios(self) -> bool:
        if self._modelo.rowCount() == 0:
            QMessageBox.warning(
                self, "Atenção",
                "Inclua pelo menos um item no abastecimento.")
            self.ui.txt_Cod_Caminhao.setFocus()
            return False
        return True

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de abastecimentos indisponível.")
            return
        if not self._validar_obrigatorios():
            return

        dados = self._coletar_dados()
        try:
            if dados.get("sequencia"):
                if not self._service.atualizar(dados):
                    # outro usuário excluiu o abastecimento enquanto a
                    # edição estava aberta
                    logger.warning(
                        "Atualização sem efeito: abastecimento %s "
                        "não existe mais", dados.get("sequencia"))
                    QMessageBox.warning(
                        self, "Atenção",
                        "Abastecimento não encontrado — provavelmente "
                        "foi excluído por outro usuário. A tela será "
                        "limpa.")
                    self._limpar_campos()
                    self.ui.txt_Abastecimento.setFocus()
                    return
            else:
                abastecimento = self._service.salvar(dados)
                # exibe a sequência gerada automaticamente
                self.ui.txt_Abastecimento.setText(
                    str(abastecimento.sequencia))
        except ConflitoEdicaoError:
            # outro usuário salvou durante a edição: avisa e recarrega
            # a versão mais recente em vez de sobrescrever calado
            logger.warning(
                "Conflito de edição: abastecimento %s alterado por "
                "outro usuário", dados.get("sequencia"))
            QMessageBox.warning(
                self, "Atenção",
                "Abastecimento alterado por outro usuário — a tela foi "
                "atualizada com a versão mais recente. Revise e salve "
                "novamente se necessário.")
            abastecimento = None
            try:
                abastecimento = self._service.buscar_por_sequencia(
                    int(dados.get("sequencia")))
            except Exception:
                logger.exception("Falha ao recarregar após conflito")
            if abastecimento is not None:
                self._preencher(abastecimento)
            else:
                self._limpar_campos()
                self.ui.txt_Abastecimento.setFocus()
            return
        except Exception as exc:
            logger.exception("Falha ao salvar abastecimento")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar o abastecimento:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("Abastecimento salvo")
        QMessageBox.information(
            self, "Sucesso", "Abastecimento salvo com sucesso.")
        self._limpar_campos()
        self.ui.txt_Abastecimento.setFocus()

    def _excluir(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de abastecimentos indisponível.")
            return

        sequencia = self.ui.txt_Abastecimento.text().strip()
        if not sequencia:
            QMessageBox.warning(
                self, "Atenção",
                "Nenhum abastecimento carregado para excluir.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir o abastecimento '{sequencia}' e todos os seus "
            "itens?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            excluido = self._service.excluir(int(sequencia))
        except Exception as exc:
            logger.exception("Falha ao excluir abastecimento")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir o abastecimento:"
                f"\n{self._mensagem_erro(exc)}")
            return
        if not excluido:
            # outro usuário já havia excluído
            logger.warning("Exclusão sem efeito: abastecimento %s "
                           "não existe mais", sequencia)
            QMessageBox.warning(
                self, "Atenção",
                "Abastecimento não encontrado — provavelmente já foi "
                "excluído por outro usuário.")
            self._limpar_campos()
            self.ui.txt_Abastecimento.setFocus()
            return

        logger.info("Abastecimento excluído: %s", sequencia)
        QMessageBox.information(
            self, "Sucesso", "Abastecimento excluído com sucesso.")
        self._limpar_campos()
        self.ui.txt_Abastecimento.setFocus()

    # ---------------- cadastros para reedicao ----------------

    def _carregar_caminhoes(self):
        """Carrega o cadastro para localizar snapshots na reedição."""
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

    def _carregar_colaboradores(self):
        """Carrega o cadastro para localizar snapshots na reedição."""
        self._colaboradores = []
        if self._colaborador_service is None:
            return
        try:
            self._colaboradores = self._colaborador_service.pesquisar("")
        except Exception as exc:
            logger.exception("Falha ao carregar colaboradores")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível carregar colaboradores:\n{exc}")

    # ---------------- selecao de caminhao (do item) ----------------

    def _caminhao_digitado(self):
        """Usuário digitou outro código: invalida a seleção anterior."""
        self._caminhao_selecionado = None
        self.ui.txt_Modelo.clear()

    def _buscar_caminhao_por_codigo(self,
                                    avisar: bool = True) -> Caminhao | None:
        """Enter no código: com texto resolve; vazio abre a pesquisa.

        avisar=False (chamada interna, ex.: Confirmar item) resolve em
        silêncio para que a validação exiba UM único aviso.
        """
        codigo = self.ui.txt_Cod_Caminhao.text().strip()
        if not codigo:
            self._pesquisar_caminhao()
            return self._caminhao_selecionado
        if self._caminhao_service is None:
            QMessageBox.critical(
                self, "Erro", "Service de caminhões indisponível.")
            return None
        try:
            caminhao = self._caminhao_service.buscar_por_codigo(codigo)
        except Exception as exc:
            logger.exception("Falha ao buscar caminhão por código")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o caminhão:\n{exc}")
            return None
        if caminhao is None:
            if avisar:
                QMessageBox.warning(
                    self, "Atenção",
                    f"Caminhão '{codigo}' não encontrado.")
            self._caminhao_selecionado = None
            self.ui.txt_Modelo.clear()
            return None
        self._aplicar_caminhao(caminhao)
        return caminhao

    def _pesquisar_caminhao(self):
        """'...' abre a pesquisa de caminhões e aplica o escolhido."""
        from app.controllers.pesquisa_caminhoes_controller import (
            PesquisaCaminhoesController,
        )
        try:
            dialogo = PesquisaCaminhoesController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa de caminhões")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() != dialogo.DialogCode.Accepted:
            return
        caminhao = dialogo.caminhao_selecionado()
        if caminhao:
            self._aplicar_caminhao(caminhao)

    def _aplicar_caminhao(self, caminhao: Caminhao):
        """Preenche código/modelo e guarda o caminhão selecionado."""
        self._caminhao_selecionado = caminhao
        self.ui.txt_Cod_Caminhao.setText(caminhao.codigo or "")
        self.ui.txt_Modelo.setText(caminhao.modelo or "")
        self.ui.txt_Cod_Colaborador.setFocus()

    def _localizar_caminhao(self, codigo: str,
                            modelo: str) -> Caminhao | None:
        """Localiza o caminhão do snapshot no cadastro carregado.

        Snapshots antigos podem divergir do cadastro atual, então a
        comparação nunca é textual estrita.
        """
        if codigo:
            for caminhao in self._caminhoes:
                if caminhao.codigo == codigo:
                    return caminhao
        if codigo or modelo:
            # snapshot sem cadastro: entrada temporária para edição
            return Caminhao(id=None, codigo=codigo, modelo=modelo)
        return None

    # ---------------- selecao de colaborador (do item) ----------------

    def _colaborador_digitado(self):
        """Usuário digitou outro código: invalida a seleção anterior."""
        self._colaborador_selecionado = None
        self.ui.txt_Nome.clear()

    def _buscar_colaborador_por_codigo(
            self, avisar: bool = True) -> Colaborador | None:
        """Enter no código: com texto resolve; vazio abre a pesquisa.

        avisar=False (chamada interna, ex.: Confirmar item) resolve em
        silêncio para que a validação exiba UM único aviso.
        """
        codigo = self.ui.txt_Cod_Colaborador.text().strip()
        if not codigo:
            self._pesquisar_colaborador()
            return self._colaborador_selecionado
        if self._colaborador_service is None:
            QMessageBox.critical(
                self, "Erro", "Service de colaboradores indisponível.")
            return None
        try:
            colaborador = self._colaborador_service.buscar_por_codigo(
                codigo)
        except Exception as exc:
            logger.exception("Falha ao buscar colaborador por código")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o colaborador:\n{exc}")
            return None
        if colaborador is None:
            if avisar:
                QMessageBox.warning(
                    self, "Atenção",
                    f"Colaborador '{codigo}' não encontrado.")
            self._colaborador_selecionado = None
            self.ui.txt_Nome.clear()
            return None
        self._aplicar_colaborador(colaborador)
        return colaborador

    def _pesquisar_colaborador(self):
        """'...' abre a pesquisa de colaboradores e aplica o escolhido."""
        from app.controllers.pesquisa_colaborador_controller import (
            PesquisaColaboradorController,
        )
        try:
            dialogo = PesquisaColaboradorController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa de colaboradores")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() != dialogo.DialogCode.Accepted:
            return
        colaborador = dialogo.colaborador_selecionado()
        if colaborador:
            self._aplicar_colaborador(colaborador)

    def _aplicar_colaborador(self, colaborador: Colaborador):
        """Preenche código/nome e guarda o colaborador selecionado."""
        self._colaborador_selecionado = colaborador
        self.ui.txt_Cod_Colaborador.setText(colaborador.codigo or "")
        self.ui.txt_Nome.setText(colaborador.nome or "")
        self.ui.txt_Destino.setFocus()

    @staticmethod
    def _so_digitos(texto: str) -> str:
        return "".join(c for c in (texto or "") if c.isdigit())

    def _localizar_colaborador(self, codigo: str, nome: str,
                               documento: str) -> Colaborador | None:
        """Localiza o colaborador do snapshot no cadastro carregado.

        1) código igual; 2) documento igual (apenas dígitos);
        3) nome igual ignorando maiúsculas/minúsculas e espaços.
        Snapshots antigos podem divergir do cadastro atual, então a
        comparação nunca é textual estrita.
        """
        if codigo:
            for col in self._colaboradores:
                if col.codigo == codigo:
                    return col
        doc = self._so_digitos(documento)
        nome_norm = " ".join(nome.split()).casefold()
        if doc:
            for col in self._colaboradores:
                if self._so_digitos(col.documento) == doc:
                    return col
        for col in self._colaboradores:
            if " ".join(col.nome.split()).casefold() == nome_norm:
                return col
        if nome:
            # snapshot sem cadastro: entrada temporária para edição
            return Colaborador(id=None, codigo="", nome=nome,
                               documento=documento)
        return None

    # ---------------- itens da grade ----------------

    def _confirmar_item(self):
        # vínculos do item: resolve código digitado sem Enter em
        # silêncio (a validação exibe UM único aviso por campo)
        caminhao = self._caminhao_selecionado
        if caminhao is None and self.ui.txt_Cod_Caminhao.text().strip():
            caminhao = self._buscar_caminhao_por_codigo(avisar=False)
        if caminhao is None:
            QMessageBox.warning(
                self, "Atenção",
                "Selecione o caminhão (código ou pesquisa).")
            self.ui.txt_Cod_Caminhao.setFocus()
            return
        colaborador = self._colaborador_selecionado
        if (colaborador is None
                and self.ui.txt_Cod_Colaborador.text().strip()):
            colaborador = self._buscar_colaborador_por_codigo(avisar=False)
        if colaborador is None:
            QMessageBox.warning(
                self, "Atenção",
                "Selecione o colaborador (código ou pesquisa).")
            self.ui.txt_Cod_Colaborador.setFocus()
            return

        destino = self.ui.txt_Destino.text().strip()
        if not destino:
            QMessageBox.warning(
                self, "Atenção", "Informe o destino.")
            self.ui.txt_Destino.setFocus()
            return

        litros = self.ui.dbs_Litros.value()
        if litros <= 0:
            QMessageBox.warning(
                self, "Atenção",
                "Informe uma quantidade de litros maior que zero.")
            self.ui.dbs_Litros.setFocus()
            return

        km_inicio = self.ui.spn_KM_Inicio.value()
        km_final = self.ui.spn_KM_Final.value()
        cel_colaborador = QStandardItem(colaborador.nome or "")
        # valor real no UserRole: código do colaborador para o snapshot
        cel_colaborador.setData(colaborador.codigo or "", Qt.UserRole)
        itens = [
            QStandardItem(caminhao.codigo or ""),
            QStandardItem(caminhao.modelo or ""),
            cel_colaborador,
            QStandardItem(destino),
            QStandardItem(str(km_inicio)),
            QStandardItem(str(km_final)),
            QStandardItem(self._formatar_valor(litros)),
        ]
        if self._item_em_edicao is not None:
            # duplo clique carregou o item: atualiza a linha existente
            linha = self._item_em_edicao
            for coluna, item in enumerate(itens):
                self._modelo.setItem(linha, coluna, item)
            self._item_em_edicao = None
        else:
            self._modelo.appendRow(itens)
        self._atualizar_total()
        self._limpar_item()
        self.ui.txt_Cod_Caminhao.setFocus()

    def _enter_grade_itens(self):
        """Enter na grade: recarrega o item selecionado para edição."""
        self._carregar_item_edicao(self.ui.tb_Itens.currentIndex())

    def _carregar_item_edicao(self, indice):
        """Duplo clique na grade: recarrega o item nos campos."""
        if self._modo != ESTADO_ABERTA or not indice.isValid():
            return
        linha = indice.row()
        caminhao = self._localizar_caminhao(
            self._modelo.item(linha, 0).text(),
            self._modelo.item(linha, 1).text())
        if caminhao is not None:
            self._aplicar_caminhao(caminhao)
        cel_colaborador = self._modelo.item(linha, 2)
        colaborador = self._localizar_colaborador(
            cel_colaborador.data(Qt.UserRole) or "",
            cel_colaborador.text(),
            "")
        if colaborador is not None:
            self._aplicar_colaborador(colaborador)
        self.ui.txt_Destino.setText(self._modelo.item(linha, 3).text())
        self.ui.spn_KM_Inicio.setValue(
            int(self._modelo.item(linha, 4).text() or 0))
        self.ui.spn_KM_Final.setValue(
            int(self._modelo.item(linha, 5).text() or 0))
        self.ui.dbs_Litros.setValue(
            self._valor_para_float(self._modelo.item(linha, 6).text()))
        self._item_em_edicao = linha
        self.ui.txt_Cod_Caminhao.setFocus()

    def _excluir_item(self):
        indice = self.ui.tb_Itens.currentIndex()
        linha = indice.row() if indice.isValid() else self._item_em_edicao
        if linha is None or linha < 0:
            QMessageBox.warning(
                self, "Atenção", "Selecione um item na grade.")
            return
        self._modelo.removeRow(linha)
        if self._item_em_edicao == linha:
            self._item_em_edicao = None
            self._limpar_item()
        elif self._item_em_edicao is not None and self._item_em_edicao > linha:
            self._item_em_edicao -= 1
        self._atualizar_total()
        self.ui.txt_Cod_Caminhao.setFocus()

    def _limpar_item(self):
        self._caminhao_selecionado = None
        self._colaborador_selecionado = None
        self.ui.txt_Cod_Caminhao.clear()
        self.ui.txt_Modelo.clear()
        self.ui.txt_Cod_Colaborador.clear()
        self.ui.txt_Nome.clear()
        self.ui.txt_Destino.clear()
        self.ui.spn_KM_Inicio.setValue(0)
        self.ui.spn_KM_Final.setValue(0)
        self.ui.dbs_Litros.setValue(0.0)
        self._item_em_edicao = None

    def _atualizar_total(self):
        total = 0.0
        for linha in range(self._modelo.rowCount()):
            item = self._modelo.item(linha, 6)
            if item is None:
                continue
            total += self._valor_para_float(item.text())
        self.ui.txt_Total.setText(self._formatar_valor(total))

    @staticmethod
    def _valor_para_float(texto: str) -> float:
        try:
            return float(texto.replace(".", "").replace(",", "."))
        except ValueError:
            return 0.0

    @staticmethod
    def _formatar_valor(valor: float) -> str:
        texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",")
        return texto.replace("X", ".")

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Abastecimento.clear()
        self.ui.dt_Data.setDate(QDate.currentDate())
        self._modelo.removeRows(0, self._modelo.rowCount())
        self._limpar_item()
        self.ui.txt_Total.clear()
        self._abastecimento_carregado = None
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    def _coletar_dados(self) -> dict:
        qdata = self.ui.dt_Data.date()
        itens = []
        for linha in range(self._modelo.rowCount()):
            cel_colaborador = self._modelo.item(linha, 2)
            itens.append({
                "caminhao_codigo": self._modelo.item(linha, 0).text(),
                "caminhao_modelo": self._modelo.item(linha, 1).text(),
                "colaborador_codigo": str(
                    cel_colaborador.data(Qt.UserRole) or ""),
                "colaborador_nome": cel_colaborador.text(),
                "destino": self._modelo.item(linha, 3).text(),
                "km_inicio": int(self._modelo.item(linha, 4).text() or 0),
                "km_final": int(self._modelo.item(linha, 5).text() or 0),
                "litros": self._valor_para_float(
                    self._modelo.item(linha, 6).text()),
            })
        dados = {
            "data": date(qdata.year(), qdata.month(), qdata.day()),
            "itens": itens,
        }
        sequencia = self.ui.txt_Abastecimento.text().strip()
        if sequencia:
            dados["sequencia"] = int(sequencia)
            # last-write-wins: envia a versão carregada; o UPDATE só
            # aplica se ela ainda for a atual no banco
            dados["atualizado_em"] = getattr(
                self._abastecimento_carregado, "atualizado_em", None)
        return dados

    def _preencher(self, abastecimento):
        self._limpar_campos()
        self.ui.txt_Abastecimento.setText(str(abastecimento.sequencia))
        data = abastecimento.data
        self.ui.dt_Data.setDate(QDate(data.year, data.month, data.day))
        for item in abastecimento.itens:
            cel_colaborador = QStandardItem(item.colaborador_nome or "")
            # valor real no UserRole: código do colaborador do snapshot
            cel_colaborador.setData(item.colaborador_codigo or "",
                                    Qt.UserRole)
            self._modelo.appendRow([
                QStandardItem(item.caminhao_codigo or ""),
                QStandardItem(item.caminhao_modelo or ""),
                cel_colaborador,
                QStandardItem(item.destino or ""),
                QStandardItem(str(item.km_inicio or 0)),
                QStandardItem(str(item.km_final or 0)),
                QStandardItem(self._formatar_valor(item.litros or 0.0)),
            ])
        ajustar_larguras(self.ui.tb_Itens,
                         coluna_stretch=COLUNA_STRETCH_ITENS)
        self._atualizar_total()
        # last-write-wins: guarda a versão carregada para o salvar
        self._abastecimento_carregado = abastecimento
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()
