# -*- coding: utf-8 -*-
"""Controller do cadastro de colaboradores.

O código é gerado automaticamente pelo sistema (sequencial) — o campo
fica sempre desabilitado. Fluxo: "+" prepara um novo registro, "..."
abre a pesquisa e carrega o registro selecionado. Salvar grava (novo
ou existente), Editar habilita a edição, Limpar zera e Excluir remove.
"""
from PySide6.QtWidgets import QMessageBox, QWidget

from app.services.colaborador_service import ColaboradorService
from app.utils.logger import get_logger
from app.views.ui_cad_colaboradores import Ui_Cad_Colaboradores

logger = get_logger("cad_colaboradores")


class CadColaboradoresController(QWidget):
    """Tela de cadastro de colaboradores (subjanela do MDI)."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_Cad_Colaboradores()
        self.ui.setupUi(self)

        self._service = ColaboradorService()
        self._codigo_carregado: str | None = None  # None = novo registro

        self._conectar_botoes()
        self._definir_tab_order()
        self._limpar_formulario()

        logger.info("Cadastro de colaboradores iniciado")

    # ---------------- configuração ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._ao_novo)
        self.ui.bt_Pesquisar_Colaborador.clicked.connect(self._ao_pesquisar)
        self.ui.bt_Salvar.clicked.connect(self._ao_salvar)
        self.ui.bt_Editar.clicked.connect(self._ao_editar)
        self.ui.bt_Limpar.clicked.connect(self._limpar_formulario)
        self.ui.bt_Excluir.clicked.connect(self._ao_excluir)

    def _definir_tab_order(self):
        """Ordem de tabulação: Nome -> CPF -> botões de ação.

        O txt_Codigo fica desabilitado (código automático) e não
        recebe foco, por isso não entra na cadeia.
        """
        self.setTabOrder(self.ui.txt_Nome, self.ui.txt_Documento)
        self.setTabOrder(self.ui.txt_Documento, self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.bt_Pesquisar_Colaborador)
        self.setTabOrder(self.ui.bt_Pesquisar_Colaborador, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    # ---------------- eventos ----------------

    def _ao_novo(self):
        """Prepara o formulário para um novo registro."""
        self._limpar_formulario()
        self.ui.txt_Nome.setFocus()

    def _ao_pesquisar(self):
        """Abre a tela de pesquisa e carrega o registro selecionado."""
        from app.controllers.pesquisa_colaborador_controller import (
            PesquisaColaboradorController,
        )

        dialogo = PesquisaColaboradorController(self)
        if dialogo.exec() != dialogo.DialogCode.Accepted:
            return

        codigo = dialogo.codigo_selecionado
        if not codigo:
            return

        registros = self._service.pesquisar(codigo)
        registro = next(
            (r for r in registros if r["codigo"] == codigo), None)
        if registro is None:
            QMessageBox.warning(
                self, "Colaboradores",
                f"Colaborador {codigo} não encontrado.")
            return

        self._carregar(registro)

    def _ao_salvar(self):
        """Grava o registro: novo (inserir) ou carregado (atualizar)."""
        dados = {
            "codigo": self._codigo_carregado or "",
            "nome": self.ui.txt_Nome.text(),
            "documento": self.ui.txt_Documento.text(),
        }
        try:
            if self._codigo_carregado is None:
                gravado = self._service.salvar(dados)
            else:
                gravado = self._service.atualizar(dados)
        except ValueError as exc:
            QMessageBox.warning(self, "Colaboradores", str(exc))
            return
        except Exception as exc:
            logger.exception("Falha ao gravar colaborador")
            QMessageBox.critical(
                self, "Colaboradores",
                f"Falha ao gravar o colaborador:\n{exc}")
            return

        self._carregar(gravado)
        QMessageBox.information(
            self, "Colaboradores", "Colaborador gravado com sucesso.")

    def _ao_editar(self):
        """Habilita a edição do registro carregado."""
        if self._codigo_carregado is None:
            QMessageBox.information(
                self, "Colaboradores",
                "Nenhum registro carregado. Use o botão \"...\" para "
                "localizar um colaborador.")
            return
        self.ui.txt_Nome.setEnabled(True)
        self.ui.txt_Documento.setEnabled(True)
        self.ui.txt_Nome.setFocus()

    def _ao_excluir(self):
        """Exclui o registro carregado, com confirmação."""
        if self._codigo_carregado is None:
            QMessageBox.information(
                self, "Colaboradores", "Nenhum registro carregado.")
            return

        resposta = QMessageBox.question(
            self, "Colaboradores",
            f"Excluir o colaborador {self._codigo_carregado}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self._service.excluir(self._codigo_carregado)
        except ValueError as exc:
            QMessageBox.warning(self, "Colaboradores", str(exc))
            return
        except Exception as exc:
            logger.exception("Falha ao excluir colaborador")
            QMessageBox.critical(
                self, "Colaboradores",
                f"Falha ao excluir o colaborador:\n{exc}")
            return

        self._limpar_formulario()
        QMessageBox.information(
            self, "Colaboradores", "Colaborador excluído com sucesso.")

    # ---------------- apoio ----------------

    def _carregar(self, registro: dict):
        """Preenche o formulário com o registro e trava o código."""
        self._codigo_carregado = registro["codigo"]
        self.ui.txt_Codigo.setText(registro["codigo"])
        self.ui.txt_Nome.setText(registro["nome"])
        self.ui.txt_Documento.setText(registro["documento"])
        self.ui.txt_Codigo.setEnabled(False)
        self.ui.txt_Nome.setEnabled(True)
        self.ui.txt_Documento.setEnabled(True)

    def _limpar_formulario(self):
        """Zera o formulário e volta ao modo novo registro."""
        self._codigo_carregado = None
        self.ui.txt_Nome.clear()
        self.ui.txt_Documento.clear()
        self.ui.txt_Codigo.setEnabled(False)
        self.ui.txt_Nome.setEnabled(True)
        self.ui.txt_Documento.setEnabled(True)
        # mostra o próximo código como prévia (o definitivo é gerado ao salvar)
        try:
            self.ui.txt_Codigo.setText(self._service.proximo_codigo())
        except Exception:
            self.ui.txt_Codigo.setText("")
        self.ui.txt_Nome.setFocus()
