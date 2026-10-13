# -*- coding: utf-8 -*-
"""Controller do lançamento de recargas.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao RecargaService (cabeçalho + itens
na mesma transação) e ao ColaboradorService (combo de itens).

Fluxo mestre-detalhe:
  - "+" prepara uma nova recarga: escolhe a data e clica em
    "Abrir Recarga" para liberar a inclusão de itens;
  - "..." abre a pesquisa e carrega a recarga selecionada;
  - "Abrir Recarga" habilita o fluxo próprio dos itens (em registro
    novo E na edição): cada item é confirmado em memória (grade) com
    o botão Confirmar; duplo clique num item da grade o recarrega nos
    campos para edição (o Confirmar atualiza a linha em vez de
    adicionar outra);
  - "Sair Recarga" finaliza o lançamento dos itens e libera o
    bt_Salvar — enquanto a recarga está aberta, salvar é bloqueado;
  - Salvar grava cabeçalho e itens de uma vez (na edição os itens
    são substituídos).

A sequência é automática (gerada no salvar): o campo txt_Recargas é
somente leitura. O benefício é fixo em "Refeição" (padrão do banco).

Navegação (Tab) em modo Z: esquerda para a direita e de cima para
baixo. Com a recarga aberta, o Z efetivo percorre apenas o fluxo
próprio dos itens (combo -> carga -> sem carga -> valor -> confirmar
-> grade -> limpar -> excluir -> sair), pois os demais widgets estão
desabilitados e são pulados automaticamente pelo Qt.
"""
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QKeySequence, QShortcut, QStandardItem
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QMessageBox, QWidget

from app.models.colaborador import Colaborador
from app.utils.erros import mensagem_erro
from app.utils.logger import get_logger
from app.utils.table_utils import ajustar_larguras, configurar_tabela
from app.views.ui_lancamento_recargas import Ui_Lancamento_Recargas

try:
    from app.services.recarga_service import RecargaService
except ImportError:
    RecargaService = None

try:
    from app.services.colaborador_service import ColaboradorService
except ImportError:
    ColaboradorService = None

logger = get_logger("lancamento_recargas")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"       # aguardando "Abrir Recarga"
ESTADO_ABERTA = "aberta"   # lançando/editando itens em memória
ESTADO_PRONTA = "pronta"   # itens finalizados; salvar liberado
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"   # carregada e liberada para edição

BENEFICIO_PADRAO = "Refeição"
COLUNAS_ITENS = ["Colaborador", "CPF", "Carga", "Sem Carga", "Valor"]
COLUNA_STRETCH_ITENS = 0


class LancamentoRecargasController(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Lancamento_Recargas()
        self.ui.setupUi(self)

        self._service = RecargaService() if RecargaService else None
        self._colaborador_service = (ColaboradorService()
                                     if ColaboradorService else None)
        if self._service is None:
            logger.warning(
                "RecargaService nao encontrado - acoes desativadas")

        self._modo = ESTADO_INICIAL
        self._item_em_edicao: int | None = None  # linha da grade em edição
        self._colaboradores = []

        self.ui.txt_Recargas.setReadOnly(True)
        self.ui.txt_Total.setReadOnly(True)
        self.ui.dbs_Valor.setDecimals(2)
        self.ui.dbs_Valor.setMaximum(9999999.0)

        self._montar_grade()
        self._conectar_botoes()
        self._conectar_teclas()
        self._definir_tab_order()
        self._carregar_colaboradores()
        self._limpar_campos()

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
        self.ui.bt_Pesquisar_Recargas.clicked.connect(self._pesquisar)
        self.ui.bt_Abrir_Recargas.clicked.connect(self._abrir_recarga)
        self.ui.bt_Confirmar_Item.clicked.connect(self._confirmar_item)
        self.ui.bt_Limpar_Item.clicked.connect(self._limpar_item)
        self.ui.bt_Excluir_Item.clicked.connect(self._excluir_item)
        self.ui.bt_Sair_Recarga.clicked.connect(self._sair_recarga)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        # sequência é automática: Enter no campo abre a pesquisa
        self.ui.txt_Recargas.returnPressed.connect(self._pesquisar)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)
        # duplo clique na grade carrega o item para edição
        self.ui.tb_Itens.doubleClicked.connect(self._carregar_item_edicao)

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda->direita, cima->baixo).

        Com a recarga aberta, os widgets fora do fluxo de itens estão
        desabilitados e o Z efetivo fica restrito aos itens.
        """
        self.setTabOrder(self.ui.txt_Recargas,
                         self.ui.bt_Pesquisar_Recargas)
        self.setTabOrder(self.ui.bt_Pesquisar_Recargas, self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.dt_Data)
        self.setTabOrder(self.ui.dt_Data, self.ui.bt_Abrir_Recargas)
        self.setTabOrder(self.ui.bt_Abrir_Recargas,
                         self.ui.cmb_Colaboradores)
        self.setTabOrder(self.ui.cmb_Colaboradores, self.ui.txt_Carga)
        self.setTabOrder(self.ui.txt_Carga, self.ui.txt_Sem_Carga)
        self.setTabOrder(self.ui.txt_Sem_Carga, self.ui.dbs_Valor)
        self.setTabOrder(self.ui.dbs_Valor, self.ui.bt_Confirmar_Item)
        self.setTabOrder(self.ui.bt_Confirmar_Item, self.ui.tb_Itens)
        self.setTabOrder(self.ui.tb_Itens, self.ui.bt_Limpar_Item)
        self.setTabOrder(self.ui.bt_Limpar_Item, self.ui.bt_Excluir_Item)
        self.setTabOrder(self.ui.bt_Excluir_Item, self.ui.bt_Sair_Recarga)
        self.setTabOrder(self.ui.bt_Sair_Recarga, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    # ---------------- estados da tela ----------------

    def _area_itens(self, habilitar: bool):
        """Habilita/desabilita o fluxo próprio dos itens."""
        self.ui.cmb_Colaboradores.setEnabled(habilitar)
        self.ui.txt_Carga.setEnabled(habilitar)
        self.ui.txt_Sem_Carga.setEnabled(habilitar)
        self.ui.dbs_Valor.setEnabled(habilitar)
        self.ui.bt_Confirmar_Item.setEnabled(habilitar)
        self.ui.bt_Limpar_Item.setEnabled(habilitar)
        self.ui.bt_Excluir_Item.setEnabled(habilitar)
        self.ui.bt_Sair_Recarga.setEnabled(habilitar)

    def _estado_inicial(self):
        self.ui.txt_Recargas.setEnabled(False)  # sequência é automática
        self.ui.bt_Pesquisar_Recargas.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self.ui.dt_Data.setEnabled(False)
        self.ui.bt_Abrir_Recargas.setEnabled(False)
        self._area_itens(False)

        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Recargas.setEnabled(False)  # sequência é automática
        self.ui.txt_Recargas.clear()
        self.ui.bt_Pesquisar_Recargas.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(True)
        self.ui.dt_Data.setDate(QDate.currentDate())
        self.ui.bt_Abrir_Recargas.setEnabled(True)
        self._area_itens(False)  # liberada ao clicar em Abrir Recarga

        self.ui.bt_Salvar.setEnabled(False)  # só após "Sair Recarga"
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)

    def _estado_aberta(self):
        """Recarga aberta: fluxo de itens ativo, salvar bloqueado."""
        self.ui.txt_Recargas.setEnabled(False)
        self.ui.bt_Pesquisar_Recargas.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(False)  # data travada no lançamento
        self.ui.bt_Abrir_Recargas.setEnabled(False)
        self._area_itens(True)

        self.ui.bt_Salvar.setEnabled(False)  # só após "Sair Recarga"
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(True)

    def _estado_pronta(self):
        """Itens finalizados: salvar liberado."""
        self.ui.txt_Recargas.setEnabled(False)
        self.ui.bt_Pesquisar_Recargas.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(False)
        self.ui.bt_Abrir_Recargas.setEnabled(False)
        self._area_itens(False)

        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(
            bool(self.ui.txt_Recargas.text().strip()))
        self.ui.bt_Limpar.setEnabled(True)

    def _estado_visualizacao(self):
        self.ui.txt_Recargas.setEnabled(False)
        self.ui.bt_Pesquisar_Recargas.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(False)
        self.ui.bt_Abrir_Recargas.setEnabled(False)
        self._area_itens(False)

        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)

    def _estado_edicao(self):
        """Carregada e liberada: data editável; salvar e itens exigem
        o ciclo Abrir Recarga -> Sair Recarga."""
        self.ui.txt_Recargas.setEnabled(False)  # sequência é a chave
        self.ui.bt_Pesquisar_Recargas.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(True)
        self.ui.bt_Abrir_Recargas.setEnabled(True)
        self._area_itens(False)

        self.ui.bt_Salvar.setEnabled(False)  # só após "Sair Recarga"
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)

    # ---------------- mensagens ----------------

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(
            exc, duplicidade="Já existe uma recarga com essa sequência.")

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

    def _abrir_recarga(self):
        """Abre a recarga para lançamento/edição de itens em memória."""
        if self._modo not in (ESTADO_NOVO, ESTADO_EDICAO):
            return
        self._modo = ESTADO_ABERTA
        self._item_em_edicao = None
        self._estado_aberta()
        self.ui.cmb_Colaboradores.setFocus()

    def _sair_recarga(self):
        """Finaliza o lançamento dos itens e libera o botão Salvar."""
        if self._modo != ESTADO_ABERTA:
            return
        self._item_em_edicao = None
        self._limpar_item()
        self._modo = ESTADO_PRONTA
        self._estado_pronta()
        self.ui.bt_Salvar.setFocus()

    def _pesquisar(self):
        from app.controllers.pesquisa_recargas_controller import (
            PesquisaRecargasController,
        )
        try:
            dialogo = PesquisaRecargasController(self)
        except Exception as exc:
            logger.exception("Erro ao abrir pesquisa")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível abrir a pesquisa:\n{exc}")
            return
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            recarga = dialogo.recarga_selecionada()
            if recarga:
                self._preencher(recarga)

    def _validar_obrigatorios(self) -> bool:
        if self._modelo.rowCount() == 0:
            QMessageBox.warning(
                self, "Atenção", "Inclua pelo menos um item na recarga.")
            self.ui.cmb_Colaboradores.setFocus()
            return False
        return True

    def _salvar(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de recargas indisponível.")
            return
        if not self._validar_obrigatorios():
            return

        dados = self._coletar_dados()
        try:
            if dados.get("sequencia"):
                self._service.atualizar(dados)
            else:
                recarga = self._service.salvar(dados)
                # exibe a sequência gerada automaticamente
                self.ui.txt_Recargas.setText(str(recarga.sequencia))
        except Exception as exc:
            logger.exception("Falha ao salvar recarga")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar a recarga:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("Recarga salva")
        QMessageBox.information(
            self, "Sucesso", "Recarga salva com sucesso.")
        self._limpar_campos()
        self.ui.txt_Recargas.setFocus()

    def _excluir(self):
        if self._service is None:
            QMessageBox.critical(
                self, "Erro", "Service de recargas indisponível.")
            return

        sequencia = self.ui.txt_Recargas.text().strip()
        if not sequencia:
            QMessageBox.warning(
                self, "Atenção", "Nenhuma recarga carregada para excluir.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Excluir a recarga '{sequencia}' e todos os seus itens?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self._service.excluir(int(sequencia))
        except Exception as exc:
            logger.exception("Falha ao excluir recarga")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir a recarga:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("Recarga excluída: %s", sequencia)
        QMessageBox.information(
            self, "Sucesso", "Recarga excluída com sucesso.")
        self._limpar_campos()
        self.ui.txt_Recargas.setFocus()

    # ---------------- itens da grade ----------------

    def _carregar_colaboradores(self):
        self.ui.cmb_Colaboradores.clear()
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
            return
        for colaborador in self._colaboradores:
            self.ui.cmb_Colaboradores.addItem(
                f"{colaborador.codigo} - {colaborador.nome}", colaborador)

    @staticmethod
    def _so_digitos(texto: str) -> str:
        return "".join(c for c in (texto or "") if c.isdigit())

    def _indice_colaborador(self, nome: str, documento: str) -> int:
        """Localiza o colaborador no combo por documento e nome.

        1) documento igual (apenas dígitos, ignora formatação);
        2) nome igual ignorando maiúsculas/minúsculas e espaços.
        Snapshots antigos podem divergir do cadastro atual, então a
        comparação nunca é textual estrita.
        """
        doc = self._so_digitos(documento)
        nome_norm = " ".join(nome.split()).casefold()

        if doc:
            for i in range(self.ui.cmb_Colaboradores.count()):
                col = self.ui.cmb_Colaboradores.itemData(i)
                if col and self._so_digitos(col.documento) == doc:
                    return i
        for i in range(self.ui.cmb_Colaboradores.count()):
            col = self.ui.cmb_Colaboradores.itemData(i)
            if col and " ".join(col.nome.split()).casefold() == nome_norm:
                return i
        return -1

    def _garantir_colaborador_snapshot(self, nome: str,
                                       documento: str) -> int:
        """Garante uma entrada no combo para um snapshot sem cadastro.

        Itens importados/antigos podem referenciar colaboradores que
        não estão (ou mudaram) no cadastro. Cria uma entrada temporária
        com o snapshot para o duplo clique sempre carregar o item.
        """
        pos = self._indice_colaborador(nome, documento)
        if pos >= 0:
            return pos
        snapshot = Colaborador(id=None, codigo="", nome=nome,
                               documento=documento)
        self.ui.cmb_Colaboradores.addItem(
            f"{nome} (fora do cadastro)", snapshot)
        return self.ui.cmb_Colaboradores.count() - 1

    def _confirmar_item(self):
        colaborador = self.ui.cmb_Colaboradores.currentData()
        if colaborador is None:
            QMessageBox.warning(
                self, "Atenção", "Selecione o colaborador.")
            self.ui.cmb_Colaboradores.setFocus()
            return

        valor = self.ui.dbs_Valor.value()
        if valor <= 0:
            QMessageBox.warning(
                self, "Atenção", "Informe um valor maior que zero.")
            self.ui.dbs_Valor.setFocus()
            return

        itens = [
            QStandardItem(colaborador.nome),
            QStandardItem(colaborador.documento or ""),
            QStandardItem(self.ui.txt_Carga.text().strip()),
            QStandardItem(self.ui.txt_Sem_Carga.text().strip()),
            QStandardItem(self._formatar_valor(valor)),
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
        self.ui.cmb_Colaboradores.setFocus()

    def _carregar_item_edicao(self, indice):
        """Duplo clique na grade: recarrega o item nos campos."""
        if self._modo != ESTADO_ABERTA or not indice.isValid():
            return
        linha = indice.row()
        nome = self._modelo.item(linha, 0).text()
        documento = self._modelo.item(linha, 1).text()
        pos = self._garantir_colaborador_snapshot(nome, documento)
        self.ui.cmb_Colaboradores.setCurrentIndex(pos)
        self.ui.txt_Carga.setText(self._modelo.item(linha, 2).text())
        self.ui.txt_Sem_Carga.setText(self._modelo.item(linha, 3).text())
        self.ui.dbs_Valor.setValue(
            self._valor_para_float(self._modelo.item(linha, 4).text()))
        self._item_em_edicao = linha
        self.ui.cmb_Colaboradores.setFocus()

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

    def _limpar_item(self):
        self.ui.cmb_Colaboradores.setCurrentIndex(-1)
        self.ui.txt_Carga.clear()
        self.ui.txt_Sem_Carga.clear()
        self.ui.dbs_Valor.setValue(0.0)
        self._item_em_edicao = None

    def _atualizar_total(self):
        total = 0.0
        for linha in range(self._modelo.rowCount()):
            item = self._modelo.item(linha, 4)
            if item is None:
                continue
            total += self._valor_para_float(item.text())
        self.ui.txt_Total.setText(f"R$ {self._formatar_valor(total)}")

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
        self.ui.txt_Recargas.clear()
        self.ui.dt_Data.setDate(QDate.currentDate())
        self._modelo.removeRows(0, self._modelo.rowCount())
        self._limpar_item()
        self.ui.txt_Total.clear()
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    def _coletar_dados(self) -> dict:
        qdata = self.ui.dt_Data.date()
        itens = []
        for linha in range(self._modelo.rowCount()):
            itens.append({
                "nome": self._modelo.item(linha, 0).text(),
                "documento": self._modelo.item(linha, 1).text(),
                "carga": self._modelo.item(linha, 2).text(),
                "sem_carga": self._modelo.item(linha, 3).text(),
                "valor": self._valor_para_float(
                    self._modelo.item(linha, 4).text()),
                "beneficio": BENEFICIO_PADRAO,
            })
        dados = {
            "data": date(qdata.year(), qdata.month(), qdata.day()),
            "descricao": "",
            "itens": itens,
        }
        sequencia = self.ui.txt_Recargas.text().strip()
        if sequencia:
            dados["sequencia"] = int(sequencia)
        return dados

    def _preencher(self, recarga):
        self._limpar_campos()
        self.ui.txt_Recargas.setText(str(recarga.sequencia))
        data = recarga.data
        self.ui.dt_Data.setDate(QDate(data.year, data.month, data.day))
        for item in recarga.itens:
            self._modelo.appendRow([
                QStandardItem(item.nome),
                QStandardItem(item.documento or ""),
                QStandardItem(item.carga or ""),
                QStandardItem(item.sem_carga or ""),
                QStandardItem(self._formatar_valor(item.valor)),
            ])
        self._atualizar_total()
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()
