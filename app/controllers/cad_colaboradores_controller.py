# -*- coding: utf-8 -*-
"""Controller do cadastro de colaboradores.

Responsabilidade: APENAS controle de tela. Máquina de estados, busca
por código, salvar/excluir e mensagens comuns vêm de CadastroBase —
aqui ficam apenas os widgets, a validação e os dados do colaborador.

O código é gerado automaticamente no salvar, mas o campo txt_Codigo
fica HABILITADO no estado inicial como campo de busca: digitar um
código e Enter carrega o colaborador direto do banco (mesmo resultado
de selecionar na pesquisa); Enter com o campo vazio abre a pesquisa
completa. Em novo/edição o campo volta a bloquear (o código é gerado
ou é a chave do update).
"""
from PySide6.QtWidgets import QMessageBox, QWidget

from app.controllers.cadastro_base import CadastroBase
from app.views.ui_cad_colaboradores import Ui_Cad_Colaboradores

try:
    from app.services.colaborador_service import ColaboradorService
except ImportError:
    ColaboradorService = None


class CadColaboradoresController(CadastroBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Cad_Colaboradores()
        self.ui.setupUi(self)

        self._service = (ColaboradorService()
                         if ColaboradorService else None)

        self._w_pesquisar = self.ui.bt_Pesquisar_Colaborador
        self._w_campos = [self.ui.txt_Nome, self.ui.txt_Documento,
                          self.ui.chk_Ativo]
        self._w_foco_novo = self.ui.txt_Nome

        self._inicializar()

    # ---------------- pesquisa ----------------

    def _pesquisar(self):
        from app.controllers.pesquisa_colaborador_controller import (
            PesquisaColaboradorController,
        )
        dialogo = PesquisaColaboradorController(self)
        if dialogo.exec():
            colaborador = dialogo.colaborador_selecionado()
            if colaborador:
                self._carregar_registro(colaborador)

    # ---------------- hooks do CadastroBase ----------------

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda->direita, cima->baixo).

        Linha 1 (frm_Codigo):  txt_Codigo -> bt_Pesquisar -> bt_Novo
        Linha 2 (frm_Corpo):   txt_Nome -> txt_Documento -> chk_Ativo
        Linha 3 (frm_Crud):    bt_Salvar -> bt_Editar -> bt_Limpar
                               -> bt_Excluir
        """
        self.setTabOrder(self.ui.txt_Codigo,
                         self.ui.bt_Pesquisar_Colaborador)
        self.setTabOrder(self.ui.bt_Pesquisar_Colaborador, self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.txt_Nome)
        self.setTabOrder(self.ui.txt_Nome, self.ui.txt_Documento)
        self.setTabOrder(self.ui.txt_Documento, self.ui.chk_Ativo)
        self.setTabOrder(self.ui.chk_Ativo, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    def _nome_registro(self) -> str:
        return "colaborador"

    def _nome_service(self) -> str:
        return "colaboradores"

    def _msg_duplicidade(self) -> str:
        return "Já existe um colaborador com esse código."

    def _validar_obrigatorios(self) -> bool:
        if not self.ui.txt_Nome.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o nome.")
            self.ui.txt_Nome.setFocus()
            return False
        return True

    def _coletar_dados(self) -> dict:
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "nome": self.ui.txt_Nome.text().strip(),
            "documento": self.ui.txt_Documento.text().strip(),
            "ativo": self.ui.chk_Ativo.isChecked(),
        }

    def _preencher_campos(self, colaborador):
        self.ui.txt_Nome.setText(colaborador.nome)
        self.ui.txt_Documento.setText(colaborador.documento)
        self.ui.chk_Ativo.setChecked(colaborador.ativo)

    def _limpar_especifico(self):
        self.ui.txt_Nome.clear()
        self.ui.txt_Documento.clear()
        self.ui.chk_Ativo.setChecked(True)  # novo colaborador nasce ativo
