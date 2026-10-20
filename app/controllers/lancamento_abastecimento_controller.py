# -*- coding: utf-8 -*-
"""Controller do lançamento de abastecimentos.

Herda de LancamentoBase (app/controllers/lancamento_base.py), que
concentra o esqueleto comum dos lançamentos: máquina de estados
(inicial -> novo -> aberta -> pronta -> visualizacao/edicao), busca
por sequência (Enter com texto busca direto; vazio abre a pesquisa),
F2 = novo, grade em memória (Confirmar adiciona; duplo clique/Enter
recarrega o item — Confirmar atualiza, não duplica), total, salvar/
excluir e last-write-wins (conflito avisa e recarrega a versão mais
recente). Aqui ficam apenas as particularidades da tela.

Vínculos POR ITEM: caminhão e colaborador pertencem a cada item da
grade (não ao cabeçalho, que fica só com sequência e data). Com o
lançamento aberto, digite o código e pressione Enter (campo vazio +
Enter abre la pesquisa) ou clique em "..." — a descrição (modelo/nome)
é preenchida automaticamente e fica somente leitura; digitar no
código invalida a seleção.

Itens: destino + KM início/final (livres) + litros (> 0). A grade tem
7 colunas; a columna Caminhão mostra a PLACA (código no Qt.UserRole
da célula 0) e o código do colaborador fica no Qt.UserRole da célula
2 (para o snapshot na gravação). Snapshots antigos são localizados no
cadastro cargado na reedição (_localizar_caminhao/
_localizar_colaborador); sem cadastro, viram entrada temporária.

Navegación (Tab) em modo Z: esquerda para a direita e de cima para
baixo — com o abastecimento aberto, os widgets fora do fluxo de itens
estão desabilitados e são pulados pelo Qt.
"""
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMessageBox

from app.controllers.lancamento_base import LancamentoBase
from app.models.caminhao import Caminhao
from app.models.colaborador import Colaborador
from app.utils.logger import get_logger
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

# grade: código do caminhão fica no Qt.UserRole da célula 0 (placa à
# vista) e código do colaborador no Qt.UserRole da célula 2
COLUNAS_ITENS = ["Caminhão", "Modelo", "Colaborador", "Destino",
                 "KM Início", "KM Final", "Litros"]


class LancamentoAbastecimentoController(LancamentoBase):

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

        self._caminhoes = []      # cadastro p/ localizar snapshots
        self._colaboradores = []  # cadastro p/ localizar snapshots
        self._caminhao_selecionado: Caminhao | None = None
        self._colaborador_selecionado: Colaborador | None = None

        self.ui.txt_Total.setReadOnly(True)
        self.ui.txt_Modelo.setReadOnly(True)  # descrição vem do código
        self.ui.txt_Nome.setReadOnly(True)    # descrição vem do código
        self.ui.dbs_Litros.setDecimals(2)
        self.ui.dbs_Litros.setMaximum(9999999.0)

        # a base monta a grade, conecta botões/teclas, define o estado
        # inicial e dá o foco — chamar POR ÚLTIMO
        self._inicializar()
        self._carregar_caminhoes()
        self._carregar_colaboradores()

    # ================= hooks da LancamentoBase =================

    def _w_sequencia(self):
        return self.ui.txt_Abastecimento

    def _w_data(self):
        return self.ui.dt_Data

    def _w_grade(self):
        return self.ui.tb_Itens

    def _w_total(self):
        return self.ui.txt_Total

    def _bt_novo(self):
        return self.ui.bt_Novo

    def _bt_pesquisar(self):
        return self.ui.bt_Pesquisar_Abastecimentos

    def _bt_abrir(self):
        return self.ui.bt_Abrir_Abastecimento

    def _bt_sair(self):
        return self.ui.bt_Sair_Abastecimento

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
        return 6  # Litros

    def _area_itens(self, habilitar: bool):
        """Vínculos DO ITEM + fluxo dos itens — ativos juntos."""
        self.ui.txt_Cod_Caminhao.setEnabled(habilitar)
        self.ui.bt_Pesquisar_Caminhao.setEnabled(habilitar)
        self.ui.txt_Modelo.setEnabled(habilitar)
        self.ui.txt_Cod_Colaborador.setEnabled(habilitar)
        self.ui.bt_Pesquisar_Colaborador.setEnabled(habilitar)
        self.ui.txt_Nome.setEnabled(habilitar)
        self.ui.txt_Destino.setEnabled(habilitar)
        self.ui.spn_KM_Inicio.setEnabled(habilitar)
        self.ui.spn_KM_Final.setEnabled(habilitar)
        self.ui.dbs_Litros.setEnabled(habilitar)
        self.ui.bt_Confirmar_Item.setEnabled(habilitar)
        self.ui.bt_Limpar_Item.setEnabled(habilitar)
        self.ui.bt_Excluir_Item.setEnabled(habilitar)
        self.ui.bt_Sair_Abastecimento.setEnabled(habilitar)

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

    def _conectar_especifico(self):
        """Vínculos do item: Enter resolve; digitar invalida a seleção.

        Os botões "..." (bt_Pesquisar_Caminhao / bt_Pesquisar_Colaborador)
        abrem as pesquisas — sem essas conexões o clique não faz nada.
        """
        self.ui.txt_Cod_Caminhao.returnPressed.connect(
            self._buscar_caminhao_por_codigo)
        self.ui.txt_Cod_Caminhao.textEdited.connect(
            self._caminhao_digitado)
        self.ui.bt_Pesquisar_Caminhao.clicked.connect(
            self._pesquisar_caminhao)
        self.ui.txt_Cod_Colaborador.returnPressed.connect(
            self._buscar_colaborador_por_codigo)
        self.ui.txt_Cod_Colaborador.textEdited.connect(
            self._colaborador_digitado)
        self.ui.bt_Pesquisar_Colaborador.clicked.connect(
            self._pesquisar_colaborador)

    def _foco_apos_abrir(self):
        self.ui.txt_Cod_Caminhao.setFocus()

    def _foco_primeiro_item(self):
        self.ui.txt_Cod_Caminhao.setFocus()

    def _foco_apos_item(self):
        self.ui.txt_Cod_Caminhao.setFocus()

    def _validar_item(self) -> bool:
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
            return False
        colaborador = self._colaborador_selecionado
        if (colaborador is None
                and self.ui.txt_Cod_Colaborador.text().strip()):
            colaborador = self._buscar_colaborador_por_codigo(avisar=False)
        if colaborador is None:
            QMessageBox.warning(
                self, "Atenção",
                "Selecione o colaborador (código ou pesquisa).")
            self.ui.txt_Cod_Colaborador.setFocus()
            return False
        if not self.ui.txt_Destino.text().strip():
            QMessageBox.warning(
                self, "Atenção", "Informe o destino.")
            self.ui.txt_Destino.setFocus()
            return False
        if self.ui.dbs_Litros.value() <= 0:
            QMessageBox.warning(
                self, "Atenção",
                "Informe uma quantidade de litros maior que zero.")
            self.ui.dbs_Litros.setFocus()
            return False
        return True

    def _linha_item(self):
        caminhao = self._caminhao_selecionado
        colaborador = self._colaborador_selecionado
        cel_caminhao = QStandardItem(caminhao.placa or caminhao.codigo or "")
        # valor real no UserRole: código do caminhão para o snapshot
        cel_caminhao.setData(caminhao.codigo or "", Qt.UserRole)
        cel_colaborador = QStandardItem(colaborador.nome or "")
        # valor real no UserRole: código do colaborador para o snapshot
        cel_colaborador.setData(colaborador.codigo or "", Qt.UserRole)
        return [
            cel_caminhao,
            QStandardItem(caminhao.modelo or ""),
            cel_colaborador,
            QStandardItem(self.ui.txt_Destino.text().strip()),
            QStandardItem(str(self.ui.spn_KM_Inicio.value())),
            QStandardItem(str(self.ui.spn_KM_Final.value())),
            QStandardItem(self._formatar_valor(self.ui.dbs_Litros.value())),
        ]

    def _carregar_item_campos(self, linha: int):
        cel_caminhao = self._modelo.item(linha, 0)
        caminhao = self._localizar_caminhao(
            str(cel_caminhao.data(Qt.UserRole) or ""),
            self._modelo.item(linha, 1).text())
        if caminhao is not None:
            self._aplicar_caminhao(caminhao)
        cel_colaborador = self._modelo.item(linha, 2)
        colaborador = self._localizar_colaborador(
            str(cel_colaborador.data(Qt.UserRole) or ""),
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

    def _limpar_item_campos(self):
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

    def _abrir_pesquisa(self):
        """'...' abre a pesquisa e devolve o abastecimento escolhido."""
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
            return None
        if dialogo.exec() != dialogo.DialogCode.Accepted:
            return None
        return dialogo.abastecimento_selecionado()

    def _popular_grade(self, abastecimento):
        for item in abastecimento.itens:
            caminhao = self._localizar_caminhao(
                item.caminhao_codigo or "", item.caminhao_modelo or "")
            placa = ((caminhao.placa or caminhao.codigo)
                     if caminhao is not None
                     else (item.caminhao_codigo or ""))
            cel_caminhao = QStandardItem(placa)
            # valor real no UserRole: código do caminhão do snapshot
            cel_caminhao.setData(item.caminhao_codigo or "", Qt.UserRole)
            cel_colaborador = QStandardItem(item.colaborador_nome or "")
            # valor real no UserRole: código do colaborador do snapshot
            cel_colaborador.setData(item.colaborador_codigo or "",
                                    Qt.UserRole)
            self._modelo.appendRow([
                cel_caminhao,
                QStandardItem(item.caminhao_modelo or ""),
                cel_colaborador,
                QStandardItem(item.destino or ""),
                QStandardItem(str(item.km_inicio or 0)),
                QStandardItem(str(item.km_final or 0)),
                QStandardItem(self._formatar_valor(item.litros or 0.0)),
            ])

    def _coletar_itens(self):
        itens = []
        for linha in range(self._modelo.rowCount()):
            cel_caminhao = self._modelo.item(linha, 0)
            cel_colaborador = self._modelo.item(linha, 2)
            itens.append({
                "caminhao_codigo": str(
                    cel_caminhao.data(Qt.UserRole) or ""),
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
        return itens

    def _nome_registro(self) -> str:
        return "abastecimento"

    def _msg_duplicidade(self) -> str:
        return "Já existe um abastecimento com essa sequência."

    # ---------------- cadastros para reedicao ----------------

    def _carregar_caminhoes(self):
        """Carrega o cadastro para localizar snapshots na reedição."""
        self._caminhoes = []
        if self._caminhao_service is None:
            return
        try:
            self._caminhoes = self._caminhao_service.pesquisar("")
        except Exception as exc:
            logger.exception("Falha ao cargar caminhões")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível cargar caminhões:\n{exc}")

    def _carregar_colaboradores(self):
        """Carrega o cadastro para localizar snapshots na reedição."""
        self._colaboradores = []
        if self._colaborador_service is None:
            return
        try:
            self._colaboradores = self._colaborador_service.pesquisar("")
        except Exception as exc:
            logger.exception("Falha ao cargar colaboradores")
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível cargar colaboradores:\n{exc}")

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
        """Localiza o caminhão do snapshot no cadastro cargado.

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
        """Localiza o colaborador do snapshot no cadastro cargado.

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
