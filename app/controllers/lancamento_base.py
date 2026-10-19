# -*- coding: utf-8 -*-
"""Base das telas de lançamento com itens (recargas, abastecimentos).

Absorve o esqueleto comum às telas de lançamento mestre-detalhe:
  - máquina de estados: inicial -> novo -> aberta -> pronta ->
    visualizacao/edicao
  - campo de sequência como busca no estado inicial (Enter com texto
    busca direto; vazio abre a pesquisa)
  - F2 = novo; grade em memória (Confirmar adiciona; duplo clique ou
    Enter recarrega o item — Confirmar atualiza, não duplica)
  - Total calculado da grade
  - last-write-wins completo: a versão carregada fica guardada em
    _registro_carregado no _preencher e é enviada no salvar em edição;
    alterado por outro usuário, o service levanta ConflitoEdicaoError —
    a tela avisa e recarrega a versão mais recente; o registro ter
    sumido (False) avisa e limpa
  - _salvar (só no estado pronta) e _excluir com os mesmos fluxos e
    mensagens em todas as telas
  - tab order em modo Z (o filho define a ordem específica)

Contrato do filho (implementar; chamar _inicializar() por último):
  - criar a UI (self.ui) e definir self._service
  - hooks de widgets: _w_sequencia, _w_data, _w_grade, _w_total,
    _bt_novo, _bt_pesquisar, _bt_abrir, _bt_sair, _bt_confirmar_item,
    _bt_limpar_item, _bt_excluir_item, _bt_salvar, _bt_editar,
    _bt_limpar, _bt_excluir
  - _colunas_grade(): rótulos das colunas da grade
  - _coluna_valor(): índice da coluna somada no Total
  - _area_itens(habilitar): liga/desliga o fluxo de itens (campos,
    vínculos e botões de item, incluindo o bt_Sair)
  - _definir_tab_order(): ordem Z específica da tela
  - _foco_apos_abrir(): foco ao abrir o lançamento (1º campo do item)
  - _foco_primeiro_item(): foco quando faltam itens no salvar
  - _validar_item(): valida o item (exibe o aviso e devolve bool)
  - _linha_item(): linha da grade a partir dos campos
  - _carregar_item_campos(linha): devolve a linha da grade aos campos
  - _limpar_item_campos(): limpa os campos do item
  - _foco_apos_item(): foco após Confirmar/Excluir item
  - _abrir_pesquisa(): abre o diálogo e devolve o registro ou None
  - _popular_grade(registro): despeja os itens do registro na grade
  - _coletar_itens(): itens a partir da grade
  - _nome_registro(): nome nas mensagens ("recarga", "abastecimento")
  - _msg_duplicidade(): mensagem de duplicidade do módulo
  - opcionais: _conectar_especifico() (conexões extras),
    _dados_cabecalho() (campos extras do cabeçalho), _msg_salvo()/
    _msg_excluido() (mensagens de sucesso)
"""
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import (QKeySequence, QShortcut, QStandardItem,
                           QStandardItemModel)
from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.erros import ConflitoEdicaoError, mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela

logger = get_logger("lancamento_base")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"       # aguardando "Abrir ..."
ESTADO_ABERTA = "aberta"   # lançando/editando itens em memória
ESTADO_PRONTA = "pronta"   # itens finalizados; salvar liberado
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"   # carregado e liberado para edição


class LancamentoBase(QWidget):

    COLUNA_STRETCH_GRADE = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._service = None
        self._modelo: QStandardItemModel | None = None
        self._modo = ESTADO_INICIAL
        self._item_em_edicao: int | None = None  # linha da grade em edição
        self._registro_carregado = None  # versão p/ last-write-wins

    # ================= contrato do filho (hooks) =================

    def _w_sequencia(self):
        """Campo da sequência (QLineEdit) — busca no estado inicial."""
        raise NotImplementedError

    def _w_data(self):
        """Data do lançamento (QDateEdit)."""
        raise NotImplementedError

    def _w_grade(self):
        """Grade dos itens (QTableView)."""
        raise NotImplementedError

    def _w_total(self):
        """Campo do total (QLineEdit, somente leitura)."""
        raise NotImplementedError

    def _bt_novo(self):
        raise NotImplementedError

    def _bt_pesquisar(self):
        raise NotImplementedError

    def _bt_abrir(self):
        raise NotImplementedError

    def _bt_sair(self):
        raise NotImplementedError

    def _bt_confirmar_item(self):
        raise NotImplementedError

    def _bt_limpar_item(self):
        raise NotImplementedError

    def _bt_excluir_item(self):
        raise NotImplementedError

    def _bt_salvar(self):
        raise NotImplementedError

    def _bt_editar(self):
        raise NotImplementedError

    def _bt_limpar(self):
        raise NotImplementedError

    def _bt_excluir(self):
        raise NotImplementedError

    def _colunas_grade(self) -> list:
        raise NotImplementedError

    def _coluna_valor(self) -> int:
        """Índice da coluna da grade somada no Total."""
        raise NotImplementedError

    def _area_itens(self, habilitar: bool):
        """Liga/desliga o fluxo de itens (campos, vínculos e botões)."""
        raise NotImplementedError

    def _definir_tab_order(self):
        raise NotImplementedError

    def _foco_apos_abrir(self):
        raise NotImplementedError

    def _foco_primeiro_item(self):
        raise NotImplementedError

    def _validar_item(self) -> bool:
        raise NotImplementedError

    def _linha_item(self) -> list:
        raise NotImplementedError

    def _carregar_item_campos(self, linha: int):
        raise NotImplementedError

    def _limpar_item_campos(self):
        raise NotImplementedError

    def _foco_apos_item(self):
        raise NotImplementedError

    def _abrir_pesquisa(self):
        raise NotImplementedError

    def _popular_grade(self, registro):
        raise NotImplementedError

    def _coletar_itens(self) -> list:
        raise NotImplementedError

    def _nome_registro(self) -> str:
        raise NotImplementedError

    def _msg_duplicidade(self) -> str:
        raise NotImplementedError

    def _conectar_especifico(self):
        """Conexões extras da tela (vínculos do item etc.). Padrão: nada."""

    def _dados_cabecalho(self) -> dict:
        """Campos extras do cabeçalho (além da data). Padrão: vazio."""
        return {}

    def _msg_salvo(self) -> str:
        return f"{self._nome_registro().capitalize()} salvo com sucesso."

    def _msg_excluido(self) -> str:
        return f"{self._nome_registro().capitalize()} excluído com sucesso."

    # ================= montagem =================

    def _inicializar(self):
        """Monta e conecta a tela; o filho chama por último."""
        self._montar_grade()
        self._conectar_botoes()
        self._conectar_teclas()
        self._conectar_especifico()
        self._definir_tab_order()
        self._limpar_campos()
        self._w_sequencia().setFocus()

    def _montar_grade(self):
        self._modelo = QStandardItemModel(self)
        self._modelo.setHorizontalHeaderLabels(self._colunas_grade())
        grade = self._w_grade()
        grade.setModel(self._modelo)
        configurar_tabela(grade,
                          coluna_stretch=self.COLUNA_STRETCH_GRADE,
                          ordenavel=False)
        grade.setEditTriggers(grade.EditTrigger.NoEditTriggers)

    def _conectar_botoes(self):
        self._bt_novo().clicked.connect(self._novo)
        self._bt_pesquisar().clicked.connect(self._pesquisar)
        self._bt_abrir().clicked.connect(self._abrir_lancamento)
        self._bt_sair().clicked.connect(self._sair_lancamento)
        self._bt_confirmar_item().clicked.connect(self._confirmar_item)
        self._bt_limpar_item().clicked.connect(self._limpar_item)
        self._bt_excluir_item().clicked.connect(self._excluir_item)
        self._bt_salvar().clicked.connect(self._salvar)
        self._bt_editar().clicked.connect(self._liberar_edicao)
        self._bt_limpar().clicked.connect(self._limpar_campos)
        self._bt_excluir().clicked.connect(self._excluir)

    def _conectar_teclas(self):
        # Enter na sequência: com texto busca direto; vazio abre a pesquisa
        self._w_sequencia().returnPressed.connect(self._enter_sequencia)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)
        # duplo clique na grade carrega o item para edição
        self._w_grade().doubleClicked.connect(self._carregar_item_edicao)
        # Enter na grade carrega o item para edição (como o duplo clique)
        self._at_enter_grade = QShortcut(
            QKeySequence(Qt.Key.Key_Return), self._w_grade())
        self._at_enter_grade.activated.connect(self._enter_grade_itens)

    # ================= estados da tela =================

    def _estado_inicial(self):
        self._w_sequencia().setEnabled(True)  # busca liberada
        self._bt_pesquisar().setEnabled(True)
        self._bt_novo().setEnabled(True)

        self._w_data().setEnabled(False)
        self._bt_abrir().setEnabled(False)
        self._area_itens(False)

        self._bt_salvar().setEnabled(False)
        self._bt_editar().setEnabled(False)
        self._bt_excluir().setEnabled(False)
        self._bt_limpar().setEnabled(False)

    def _estado_novo(self):
        self._w_sequencia().setEnabled(False)  # sequência automática
        self._w_sequencia().clear()
        self._bt_pesquisar().setEnabled(False)
        self._bt_novo().setEnabled(False)

        self._w_data().setEnabled(True)
        self._w_data().setDate(QDate.currentDate())
        self._bt_abrir().setEnabled(True)
        self._area_itens(False)  # liberada ao clicar em Abrir

        self._bt_salvar().setEnabled(False)  # só após "Sair"
        self._bt_editar().setEnabled(False)
        self._bt_excluir().setEnabled(False)
        self._bt_limpar().setEnabled(True)

    def _estado_aberta(self):
        """Lançamento aberto: fluxo de itens ativo, salvar bloqueado."""
        self._w_sequencia().setEnabled(False)
        self._bt_pesquisar().setEnabled(False)
        self._bt_novo().setEnabled(False)

        self._w_data().setEnabled(False)  # dados travados no lançamento
        self._bt_abrir().setEnabled(False)
        self._area_itens(True)

        self._bt_salvar().setEnabled(False)  # só após "Sair"
        self._bt_editar().setEnabled(False)
        self._bt_excluir().setEnabled(False)
        self._bt_limpar().setEnabled(True)

    def _estado_pronta(self):
        """Itens finalizados: salvar liberado."""
        self._w_sequencia().setEnabled(False)
        self._bt_pesquisar().setEnabled(False)
        self._bt_novo().setEnabled(False)

        self._w_data().setEnabled(False)
        self._bt_abrir().setEnabled(False)
        self._area_itens(False)

        self._bt_salvar().setEnabled(True)
        self._bt_editar().setEnabled(False)
        self._bt_excluir().setEnabled(
            bool(self._w_sequencia().text().strip()))
        self._bt_limpar().setEnabled(True)

    def _estado_visualizacao(self):
        self._w_sequencia().setEnabled(False)
        self._bt_pesquisar().setEnabled(False)
        self._bt_novo().setEnabled(False)

        self._w_data().setEnabled(False)
        self._bt_abrir().setEnabled(False)
        self._area_itens(False)

        self._bt_salvar().setEnabled(False)
        self._bt_editar().setEnabled(True)
        self._bt_excluir().setEnabled(True)
        self._bt_limpar().setEnabled(True)

    def _estado_edicao(self):
        """Carregado e liberado: data editável; salvar e itens exigem
        o ciclo Abrir -> Sair."""
        self._w_sequencia().setEnabled(False)  # sequência é a chave
        self._bt_pesquisar().setEnabled(False)
        self._bt_novo().setEnabled(False)

        self._w_data().setEnabled(True)
        self._bt_abrir().setEnabled(True)
        self._area_itens(False)

        self._bt_salvar().setEnabled(False)  # só após "Sair"
        self._bt_editar().setEnabled(False)
        self._bt_excluir().setEnabled(True)
        self._bt_limpar().setEnabled(True)

    # ================= mensagens =================

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(exc, duplicidade=self._msg_duplicidade())

    # ================= acoes de tela =================

    def _iniciar_novo(self):
        self._limpar_campos()
        self._modo = ESTADO_NOVO
        self._estado_novo()
        self._w_data().setFocus()

    def _novo(self):
        if self._modo != ESTADO_INICIAL:
            return
        self._iniciar_novo()

    def _liberar_edicao(self):
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self._w_data().setFocus()

    def _abrir_lancamento(self):
        """Abre o lançamento dos itens em memória."""
        if self._modo not in (ESTADO_NOVO, ESTADO_EDICAO):
            return
        self._modo = ESTADO_ABERTA
        self._item_em_edicao = None
        self._estado_aberta()
        self._foco_apos_abrir()

    def _sair_lancamento(self):
        """Finaliza o lançamento dos itens e libera o botão Salvar."""
        if self._modo != ESTADO_ABERTA:
            return
        self._item_em_edicao = None
        self._limpar_item_campos()
        self._modo = ESTADO_PRONTA
        self._estado_pronta()
        self._bt_salvar().setFocus()

    def _pesquisar(self):
        """Abre a pesquisa e carrega o registro selecionado."""
        registro = self._abrir_pesquisa()
        if registro:
            self._preencher(registro)

    def _enter_sequencia(self):
        """Enter na sequência: com texto busca direto; vazio abre pesquisa."""
        if self._w_sequencia().text().strip():
            self._buscar_por_sequencia()
        else:
            self._pesquisar()

    def _buscar_por_sequencia(self):
        """Carrega o registro da sequência digitada direto do banco."""
        if self._service is None:
            QMessageBox.critical(
                self, "Erro",
                f"Service de {self._nome_registro()}s indisponível.")
            return
        texto = self._w_sequencia().text().strip()
        if not texto.isdigit():
            QMessageBox.warning(
                self, "Atenção", "Informe uma sequência numérica.")
            self._w_sequencia().setFocus()
            self._w_sequencia().selectAll()
            return
        try:
            registro = self._service.buscar_por_sequencia(int(texto))
        except Exception as exc:
            logger.exception("Falha ao buscar %s %s",
                             self._nome_registro(), texto)
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o {self._nome_registro()}:"
                f"\n{self._mensagem_erro(exc)}")
            return
        if registro is None:
            QMessageBox.information(
                self, "Não encontrado",
                f"{self._nome_registro().capitalize()} {texto} "
                "não encontrado.")
            self._w_sequencia().setFocus()
            self._w_sequencia().selectAll()
            return
        self._preencher(registro)

    def _validar_obrigatorios(self) -> bool:
        if self._modelo.rowCount() == 0:
            QMessageBox.warning(
                self, "Atenção",
                f"Inclua pelo menos um item no {self._nome_registro()}.")
            self._foco_primeiro_item()
            return False
        return True

    def _salvar(self):
        if self._modo != ESTADO_PRONTA:
            return
        if self._service is None:
            QMessageBox.critical(
                self, "Erro",
                f"Service de {self._nome_registro()}s indisponível.")
            return
        if not self._validar_obrigatorios():
            return

        dados = self._coletar_dados()
        try:
            if dados.get("sequencia"):
                if not self._service.atualizar(dados):
                    # outro usuário excluiu o registro enquanto a
                    # edição estava aberta
                    logger.warning(
                        "Atualização sem efeito: %s %s não existe mais",
                        self._nome_registro(), dados.get("sequencia"))
                    QMessageBox.warning(
                        self, "Atenção",
                        f"{self._nome_registro().capitalize()} não "
                        "encontrado — provavelmente foi excluído por "
                        "outro usuário. A tela será limpa.")
                    self._limpar_campos()
                    self._w_sequencia().setFocus()
                    return
            else:
                registro = self._service.salvar(dados)
                # exibe a sequência gerada automaticamente
                self._w_sequencia().setText(str(registro.sequencia))
        except ConflitoEdicaoError:
            # outro usuário salvou durante a edição: avisa e recarrega
            # a versão mais recente em vez de sobrescrever calado
            logger.warning(
                "Conflito de edição: %s %s alterado por outro usuário",
                self._nome_registro(), dados.get("sequencia"))
            QMessageBox.warning(
                self, "Atenção",
                f"{self._nome_registro().capitalize()} alterado por "
                "outro usuário — a tela foi atualizada com a versão "
                "mais recente. Revise e salve novamente se necessário.")
            registro = None
            try:
                registro = self._service.buscar_por_sequencia(
                    int(dados.get("sequencia")))
            except Exception:
                logger.exception("Falha ao recarregar após conflito")
            if registro is not None:
                self._preencher(registro)
            else:
                self._limpar_campos()
                self._w_sequencia().setFocus()
            return
        except Exception as exc:
            logger.exception("Falha ao salvar %s", self._nome_registro())
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar o {self._nome_registro()}:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("%s salvo", self._nome_registro().capitalize())
        QMessageBox.information(self, "Sucesso", self._msg_salvo())
        self._limpar_campos()
        self._w_sequencia().setFocus()

    def _excluir(self):
        if self._modo not in (ESTADO_PRONTA, ESTADO_VISUALIZACAO,
                              ESTADO_EDICAO):
            return
        if self._service is None:
            QMessageBox.critical(
                self, "Erro",
                f"Service de {self._nome_registro()}s indisponível.")
            return

        sequencia = self._w_sequencia().text().strip()
        if not sequencia:
            QMessageBox.warning(
                self, "Atenção",
                f"Nenhum {self._nome_registro()} carregado para excluir.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir o {self._nome_registro()} '{sequencia}' e todos "
            "os seus itens?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            excluido = self._service.excluir(int(sequencia))
        except Exception as exc:
            logger.exception("Falha ao excluir %s",
                             self._nome_registro())
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir o {self._nome_registro()}:"
                f"\n{self._mensagem_erro(exc)}")
            return
        if not excluido:
            # outro usuário já havia excluído
            logger.warning("Exclusão sem efeito: %s %s não existe mais",
                           self._nome_registro(), sequencia)
            QMessageBox.warning(
                self, "Atenção",
                f"{self._nome_registro().capitalize()} não encontrado "
                "— provavelmente já foi excluído por outro usuário.")
            self._limpar_campos()
            self._w_sequencia().setFocus()
            return

        logger.info("%s excluído: %s",
                    self._nome_registro().capitalize(), sequencia)
        QMessageBox.information(self, "Sucesso", self._msg_excluido())
        self._limpar_campos()
        self._w_sequencia().setFocus()

    # ================= itens da grade =================

    def _confirmar_item(self):
        if not self._validar_item():
            return
        linha = self._linha_item()
        if self._item_em_edicao is not None:
            # duplo clique carregou o item: atualiza a linha existente
            for coluna, celula in enumerate(linha):
                self._modelo.setItem(self._item_em_edicao, coluna, celula)
            self._item_em_edicao = None
        else:
            self._modelo.appendRow(linha)
        self._atualizar_total()
        self._limpar_item_campos()
        self._foco_apos_item()

    def _enter_grade_itens(self):
        """Enter na grade: recarrega o item selecionado para edição."""
        self._carregar_item_edicao(self._w_grade().currentIndex())

    def _carregar_item_edicao(self, indice):
        """Duplo clique na grade: recarrega o item nos campos."""
        if self._modo != ESTADO_ABERTA or not indice.isValid():
            return
        self._carregar_item_campos(indice.row())
        self._item_em_edicao = indice.row()
        self._foco_apos_abrir()

    def _excluir_item(self):
        indice = self._w_grade().currentIndex()
        linha = indice.row() if indice.isValid() else self._item_em_edicao
        if linha is None or linha < 0:
            QMessageBox.warning(
                self, "Atenção", "Selecione um item na grade.")
            return
        self._modelo.removeRow(linha)
        if self._item_em_edicao == linha:
            self._item_em_edicao = None
            self._limpar_item_campos()
        elif (self._item_em_edicao is not None
                and self._item_em_edicao > linha):
            self._item_em_edicao -= 1
        self._atualizar_total()
        self._foco_apos_item()

    def _limpar_item(self):
        self._limpar_item_campos()
        self._item_em_edicao = None

    def _atualizar_total(self):
        total = 0.0
        for linha in range(self._modelo.rowCount()):
            celula = self._modelo.item(linha, self._coluna_valor())
            if celula is None:
                continue
            total += self._valor_para_float(celula.text())
        self._w_total().setText(self._formatar_valor(total))

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self._w_sequencia().clear()
        self._w_data().setDate(QDate.currentDate())
        self._modelo.removeRows(0, self._modelo.rowCount())
        self._limpar_item_campos()
        self._w_total().clear()
        self._registro_carregado = None
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    def _coletar_dados(self) -> dict:
        qdata = self._w_data().date()
        dados = {
            "data": date(qdata.year(), qdata.month(), qdata.day()),
            **self._dados_cabecalho(),
            "itens": self._coletar_itens(),
        }
        sequencia = self._w_sequencia().text().strip()
        if sequencia:
            dados["sequencia"] = int(sequencia)
            # last-write-wins: envia a versão carregada; o UPDATE só
            # aplica se ela ainda for a atual no banco
            dados["atualizado_em"] = getattr(
                self._registro_carregado, "atualizado_em", None)
        return dados

    def _preencher(self, registro):
        self._limpar_campos()
        self._w_sequencia().setText(str(registro.sequencia))
        data = registro.data
        self._w_data().setDate(QDate(data.year, data.month, data.day))
        self._popular_grade(registro)
        ajustar_larguras(self._w_grade(),
                         coluna_stretch=self.COLUNA_STRETCH_GRADE)
        self._atualizar_total()
        # last-write-wins: guarda a versão carregada para o salvar
        self._registro_carregado = registro
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()

    # ---------------- auxiliares ----------------

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
