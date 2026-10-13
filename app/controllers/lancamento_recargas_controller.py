# -*- coding: utf-8 -*-
"""Controller do lançamento de recargas.

Responsabilidade: APENAS controle de tela (botões, campos, navegação).
Operações de dados são delegadas ao RecargaService (cabeçalho + itens
na mesma transação) e ao ColaboradorService (combo de itens).

Fluxo mestre-detalhe:
  - "+" prepara uma nova recarga: escolhe a data e clica em
    "Abrir Recarga" para liberar a inclusão de itens;
  - "..." abre a pesquisa e carrega a recarga selecionada;
  - Confirmar adiciona o item à grade (em memória); Salvar grava
    cabeçalho e itens de uma vez; na edição os itens são substituídos;
  - "Sair Recarga" cancela e volta ao estado inicial.

A sequência é automática (gerada no salvar): o campo txt_Recargas é
somente leitura. O benefício é fixo em "Refeição" (padrão do banco).

Navegação (Tab) em modo Z: esquerda para a direita e de cima para baixo.
"""
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QKeySequence, QShortcut, QStandardItem
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QMessageBox, QWidget

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
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"

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

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda->direita, cima->baixo)."""
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
        """Habilita/desabilita a inclusão e a grade de itens."""
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

        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
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
        self.ui.txt_Recargas.setEnabled(False)  # sequência é a chave
        self.ui.bt_Pesquisar_Recargas.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)

        self.ui.dt_Data.setEnabled(True)
        self.ui.bt_Abrir_Recargas.setEnabled(False)  # já aberta
        self._area_itens(True)

        self.ui.bt_Salvar.setEnabled(True)
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
        """Libera a inclusão de itens da recarga em modo novo."""
        if self._modo != ESTADO_NOVO:
            return
        self._area_itens(True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.cmb_Colaboradores.setFocus()

    def _sair_recarga(self):
        """Cancela a recarga em curso e volta ao estado inicial."""
        self._limpar_campos()

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
            if self._modo == ESTADO_NOVO:
                recarga = self._service.salvar(dados)
                # exibe a sequência gerada automaticamente
                self.ui.txt_Recargas.setText(str(recarga.sequencia))
            elif self._modo == ESTADO_EDICAO:
                self._service.atualizar(dados)
            else:
                return
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

    def _confirmar_item(self):
        colaborador = self.ui.cmb_Colaboradores.currentData()
        if colaborador is None:
            QMessageBox.warning(
                self, "Atenção", "Selecione o colaborador.")
            self.ui.cmb_Colaboradores.setFocus()
            return

        valor = float(self.ui.dbs_Valor.value())
        if valor <= 0:
            QMessageBox.warning(
                self, "Atenção", "Informe um valor maior que zero.")
            self.ui.dbs_Valor.setFocus()
            return

        self._modelo.appendRow([
            QStandardItem(colaborador.nome),
            QStandardItem(colaborador.documento or ""),
            QStandardItem(self.ui.txt_Carga.text().strip()),
            QStandardItem(self.ui.txt_Sem_Carga.text().strip()),
            QStandardItem(self._formatar_valor(valor)),
        ])
        self._atualizar_total()
        self._limpar_item()
        self.ui.cmb_Colaboradores.setFocus()

    def _excluir_item(self):
        indice = self.ui.tb_Itens.currentIndex()
        if not indice.isValid():
            QMessageBox.warning(
                self, "Atenção", "Selecione um item na grade.")
            return
        self._modelo.removeRow(indice.row())
        self._atualizar_total()

    def _limpar_item(self):
        self.ui.cmb_Colaboradores.setCurrentIndex(-1)
        self.ui.txt_Carga.clear()
        self.ui.txt_Sem_Carga.clear()
        self.ui.dbs_Valor.setValue(0.0)

    def _atualizar_total(self):
        total = 0.0
        for linha in range(self._modelo.rowCount()):
            item = self._modelo.item(linha, 4)
            if item is None:
                continue
            texto = item.text().replace(".", "").replace(",", ".")
            try:
                total += float(texto)
            except ValueError:
                pass
        self.ui.txt_Total.setText(f"R$ {self._formatar_valor(total)}")

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
        itens = []
        for linha in range(self._modelo.rowCount()):
            valor_texto = (self._modelo.item(linha, 4).text()
                           .replace(".", "").replace(",", "."))
            itens.append({
                "nome": self._modelo.item(linha, 0).text(),
                "documento": self._modelo.item(linha, 1).text(),
                "carga": self._modelo.item(linha, 2).text(),
                "sem_carga": self._modelo.item(linha, 3).text(),
                "valor": float(valor_texto),
                "beneficio": BENEFICIO_PADRAO,
            })
        dados = {
            "data": self.ui.dt_Data.date().toPyDate(),
            "descricao": "",
            "itens": itens,
        }
        if self._modo == ESTADO_EDICAO:
            dados["sequencia"] = int(self.ui.txt_Recargas.text())
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
