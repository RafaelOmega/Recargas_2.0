# -*- coding: utf-8 -*-
"""Controller do lançamento de recargas.

Herda de LancamentoBase (app/controllers/lancamento_base.py), que
concentra o esqueleto comum dos lançamentos: máquina de estados
(inicial -> novo -> aberta -> pronta -> visualizacao/edicao), busca
por sequência (Enter com texto busca direto; vazio abre a pesquisa),
F2 = novo, grade em memória (Confirmar adiciona; duplo clique/Enter
recarrega o item — Confirmar atualiza, não duplica), total, salvar/
excluir e last-write-wins (conflito avisa e recarrega a versão mais
recente). Aqui ficam apenas as particularidades da tela.

Seleção de colaborador por código: digite o código em
txt_Cod_Colaborador e pressione Enter (campo vazio + Enter abre a
pesquisa de colaboradores), ou clique em "..." para abrir a pesquisa.
O nome é preenchido automaticamente em txt_Nome (somente leitura).

Itens: colaborador (obrigatório) + carga/sem_carga (livres) + valor
(> 0). A sequência é automática; o benefício é fixo ("Refeição") e a
coluna descricao do cabeçalho é gravada vazia. O total exibe com
prefixo "R$ " e as mensagens de sucesso usam o feminino ("recarga").

Navegação (Tab) em modo Z: esquerda para a direita e de cima para
baixo — com a recarga aberta, os demais widgets estão desabilitados
e são pulados pelo Qt.
"""
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMessageBox

from app.controllers.lancamento_base import LancamentoBase
from app.models.colaborador import Colaborador
from app.utils.logger import get_logger
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

BENEFICIO_PADRAO = "Refeição"
COLUNAS_ITENS = ["Colaborador", "CPF", "Carga", "Sem Carga", "Valor"]


class LancamentoRecargasController(LancamentoBase):

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

        self._colaboradores = []                 # cadastro p/ localizar snapshot
        self._colaborador_selecionado: Colaborador | None = None

        self.ui.txt_Total.setReadOnly(True)
        self.ui.txt_Nome.setReadOnly(True)  # nome vem do código/pesquisa
        self.ui.dbs_Valor.setDecimals(2)
        self.ui.dbs_Valor.setMaximum(9999999.0)

        # a base monta a grade, conecta botões/teclas, define o estado
        # inicial e dá o foco — chamar POR ÚLTIMO
        self._inicializar()
        self._carregar_colaboradores()

    # ================= hooks da LancamentoBase =================

    def _w_sequencia(self):
        return self.ui.txt_Recargas

    def _w_data(self):
        return self.ui.dt_Data

    def _w_grade(self):
        return self.ui.tb_Itens

    def _w_total(self):
        return self.ui.txt_Total

    def _bt_novo(self):
        return self.ui.bt_Novo

    def _bt_pesquisar(self):
        return self.ui.bt_Pesquisar_Recargas

    def _bt_abrir(self):
        return self.ui.bt_Abrir_Recargas

    def _bt_sair(self):
        return self.ui.bt_Sair_Recarga

    def _bt_confirmar_item(self):
        return self.ui.bt_Confirmar_Item

    def _bt_limpar_item(self):
        return self.ui.bt_Limpar_Item

    def _bt_excluir_item(self):
        return self.ui.bt_Excluir_Item

    def _bt_salvar(self):
        return self.ui.bt_Salvar

    def _bt_editar(self):
        return self.ui.bt_Editar

    def _bt_limpar(self):
        return self.ui.bt_Limpar

    def _bt_excluir(self):
        return self.ui.bt_Excluir

    # ---------------- contrato ----------------

    def _colunas_grade(self):
        return COLUNAS_ITENS

    def _coluna_valor(self):
        return 4  # Valor

    def _area_itens(self, habilitar: bool):
        """Habilita/desabilita o fluxo próprio dos itens."""
        self.ui.txt_Cod_Colaborador.setEnabled(habilitar)
        self.ui.bt_Pesquisar_Colaborador.setEnabled(habilitar)
        self.ui.txt_Nome.setEnabled(habilitar)
        self.ui.txt_Carga.setEnabled(habilitar)
        self.ui.txt_Sem_Carga.setEnabled(habilitar)
        self.ui.dbs_Valor.setEnabled(habilitar)
        self.ui.bt_Confirmar_Item.setEnabled(habilitar)
        self.ui.bt_Limpar_Item.setEnabled(habilitar)
        self.ui.bt_Excluir_Item.setEnabled(habilitar)
        self.ui.bt_Sair_Recarga.setEnabled(habilitar)

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
                         self.ui.txt_Cod_Colaborador)
        self.setTabOrder(self.ui.txt_Cod_Colaborador,
                         self.ui.bt_Pesquisar_Colaborador)
        self.setTabOrder(self.ui.bt_Pesquisar_Colaborador,
                         self.ui.txt_Nome)
        self.setTabOrder(self.ui.txt_Nome, self.ui.txt_Carga)
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

    def _conectar_especifico(self):
        """Código do colaborador: Enter resolve; digitar invalida."""
        self.ui.txt_Cod_Colaborador.returnPressed.connect(
            self._buscar_colaborador_por_codigo)
        self.ui.txt_Cod_Colaborador.textEdited.connect(
            self._colaborador_digitado)

    def _foco_apos_abrir(self):
        self.ui.txt_Cod_Colaborador.setFocus()

    def _foco_primeiro_item(self):
        self.ui.txt_Cod_Colaborador.setFocus()

    def _foco_apos_item(self):
        self.ui.txt_Cod_Colaborador.setFocus()

    def _validar_item(self) -> bool:
        colaborador = self._colaborador_selecionado
        if (colaborador is None
                and self.ui.txt_Cod_Colaborador.text().strip()):
            # código digitado sem Enter: tenta resolver antes de validar
            # (sem avisar aqui: a validação exibe UM único aviso)
            colaborador = self._buscar_colaborador_por_codigo(avisar=False)
        if colaborador is None:
            QMessageBox.warning(
                self, "Atenção",
                "Selecione o colaborador (código ou pesquisa).")
            self.ui.txt_Cod_Colaborador.setFocus()
            return False

        valor = self.ui.dbs_Valor.value()
        if valor <= 0:
            QMessageBox.warning(
                self, "Atenção", "Informe um valor maior que zero.")
            self.ui.dbs_Valor.setFocus()
            return False
        return True

    def _linha_item(self):
        colaborador = self._colaborador_selecionado
        return [
            QStandardItem(colaborador.nome),
            QStandardItem(colaborador.documento or ""),
            QStandardItem(self.ui.txt_Carga.text().strip()),
            QStandardItem(self.ui.txt_Sem_Carga.text().strip()),
            QStandardItem(self._formatar_valor(self.ui.dbs_Valor.value())),
        ]

    def _carregar_item_campos(self, linha: int):
        nome = self._modelo.item(linha, 0).text()
        documento = self._modelo.item(linha, 1).text()
        colaborador = self._localizar_colaborador(nome, documento)
        if colaborador is None:
            # snapshot sem cadastro: entrada temporária para edição
            colaborador = Colaborador(id=None, codigo="", nome=nome,
                                      documento=documento)
        self._aplicar_colaborador(colaborador)
        self.ui.txt_Carga.setText(self._modelo.item(linha, 2).text())
        self.ui.txt_Sem_Carga.setText(self._modelo.item(linha, 3).text())
        self.ui.dbs_Valor.setValue(
            self._valor_para_float(self._modelo.item(linha, 4).text()))

    def _limpar_item_campos(self):
        self._colaborador_selecionado = None
        self.ui.txt_Cod_Colaborador.clear()
        self.ui.txt_Nome.clear()
        self.ui.txt_Carga.clear()
        self.ui.txt_Sem_Carga.clear()
        self.ui.dbs_Valor.setValue(0.0)

    def _abrir_pesquisa(self):
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
            return None
        if dialogo.exec() != dialogo.DialogCode.Accepted:
            return None
        return dialogo.recarga_selecionada()

    def _popular_grade(self, recarga):
        for item in recarga.itens:
            self._modelo.appendRow([
                QStandardItem(item.nome),
                QStandardItem(item.documento or ""),
                QStandardItem(item.carga or ""),
                QStandardItem(item.sem_carga or ""),
                QStandardItem(self._formatar_valor(item.valor)),
            ])

    def _coletar_itens(self):
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
        return itens

    def _dados_cabecalho(self) -> dict:
        # descricao é coluna morta (sempre "") no schema atual
        return {"descricao": ""}

    def _nome_registro(self) -> str:
        return "recarga"

    def _msg_duplicidade(self) -> str:
        return "Já existe uma recarga com essa sequência."

    def _msg_salvo(self) -> str:
        return "Recarga salva com sucesso."

    def _msg_excluido(self) -> str:
        return "Recarga excluída com sucesso."

    def _validar_obrigatorios(self) -> bool:
        if self._modelo.rowCount() == 0:
            QMessageBox.warning(
                self, "Atenção", "Inclua pelo menos um item na recarga.")
            self.ui.txt_Cod_Colaborador.setFocus()
            return False
        return True

    def _atualizar_total(self):
        total = 0.0
        for linha in range(self._modelo.rowCount()):
            item = self._modelo.item(linha, self._coluna_valor())
            if item is None:
                continue
            total += self._valor_para_float(item.text())
        self._w_total().setText(f"R$ {self._formatar_valor(total)}")

    # ---------------- selecao de colaborador ----------------

    def _carregar_colaboradores(self):
        """Carrega o cadastro para localizar snapshots no duplo clique."""
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
            self.ui.txt_Carga.setFocus()

    def _aplicar_colaborador(self, colaborador: Colaborador):
        """Preenche código/nome e guarda o colaborador selecionado."""
        self._colaborador_selecionado = colaborador
        self.ui.txt_Cod_Colaborador.setText(colaborador.codigo or "")
        self.ui.txt_Nome.setText(colaborador.nome)

    @staticmethod
    def _so_digitos(texto: str) -> str:
        return "".join(c for c in (texto or "") if c.isdigit())

    def _localizar_colaborador(self, nome: str,
                               documento: str) -> Colaborador | None:
        """Localiza o colaborador no cadastro por documento e nome.

        1) documento igual (apenas dígitos, ignora formatação);
        2) nome igual ignorando maiúsculas/minúsculas e espaços.
        Snapshots antigos podem divergir do cadastro atual, então a
        comparação nunca é textual estrita.
        """
        doc = self._so_digitos(documento)
        nome_norm = " ".join(nome.split()).casefold()

        if doc:
            for col in self._colaboradores:
                if self._so_digitos(col.documento) == doc:
                    return col
        for col in self._colaboradores:
            if " ".join(col.nome.split()).casefold() == nome_norm:
                return col
        return None
