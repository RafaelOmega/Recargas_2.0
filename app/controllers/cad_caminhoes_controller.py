# -*- coding: utf-8 -*-
"""Controller do cadastro de caminhões.

Responsabilidade: APENAS controle de tela. Máquina de estados, busca
por código, salvar/excluir e mensagens comuns vêm de CadastroBase —
aqui ficam apenas os widgets, a validação e os dados do caminhão.

O código é gerado automaticamente no salvar, mas o campo txt_Codigo
fica HABILITADO no estado inicial como campo de busca: digitar um
código e Enter carrega o caminhão direto do banco (mesmo resultado
de selecionar na pesquisa); Enter com o campo vazio abre a pesquisa
completa. Em novo/edição o campo volta a bloquear (o código é gerado
ou é a chave do update).
"""
from PySide6.QtWidgets import QMessageBox, QWidget

from app.controllers.cadastro_base import CadastroBase
from app.views.ui_cad_caminhoes import Ui_Cad_Caminhoes

try:
    from app.services.caminhao_service import CaminhaoService
except ImportError:
    CaminhaoService = None


class CadCaminhoesController(CadastroBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Cad_Caminhoes()
        self.ui.setupUi(self)

        self._service = (CaminhaoService()
                         if CaminhaoService else None)

        self._w_pesquisar = self.ui.bt_Pesquisar_Caminhoes
        self._w_campos = [self.ui.txt_Modelo, self.ui.txt_Placa,
                          self.ui.chk_Ativo]
        self._w_foco_novo = self.ui.txt_Modelo

        self._inicializar()

    # ---------------- pesquisa ----------------

    def _pesquisar(self):
        from app.controllers.pesquisa_caminhoes_controller import (
            PesquisaCaminhoesController,
        )
        dialogo = PesquisaCaminhoesController(self)
        if dialogo.exec():
            caminhao = dialogo.caminhao_selecionado()
            if caminhao:
                self._carregar_registro(caminhao)

    # ---------------- hooks do CadastroBase ----------------

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda->direita, cima->baixo).

        Linha 1 (frm_Codigo):  txt_Codigo -> bt_Pesquisar -> bt_Novo
        Linha 2 (frm_Corpo):   txt_Modelo -> txt_Placa -> chk_Ativo
        Linha 3 (frm_Crud):    bt_Salvar -> bt_Editar -> bt_Limpar
                               -> bt_Excluir
        """
        self.setTabOrder(self.ui.txt_Codigo,
                         self.ui.bt_Pesquisar_Caminhoes)
        self.setTabOrder(self.ui.bt_Pesquisar_Caminhoes, self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.txt_Modelo)
        self.setTabOrder(self.ui.txt_Modelo, self.ui.txt_Placa)
        self.setTabOrder(self.ui.txt_Placa, self.ui.chk_Ativo)
        self.setTabOrder(self.ui.chk_Ativo, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    def _nome_registro(self) -> str:
        return "caminhão"

    def _nome_service(self) -> str:
        return "caminhões"

    def _msg_duplicidade(self) -> str:
        return "Já existe um caminhão com esse código."

    def _validar_obrigatorios(self) -> bool:
        if not self.ui.txt_Modelo.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o modelo.")
            self.ui.txt_Modelo.setFocus()
            return False
        return True

    def _coletar_dados(self) -> dict:
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "modelo": self.ui.txt_Modelo.text().strip(),
            "placa": self.ui.txt_Placa.text().strip(),
            "ativo": self.ui.chk_Ativo.isChecked(),
        }

    def _preencher_campos(self, caminhao):
        self.ui.txt_Modelo.setText(caminhao.modelo)
        self.ui.txt_Placa.setText(caminhao.placa)
        self.ui.chk_Ativo.setChecked(caminhao.ativo)

    def _limpar_especifico(self):
        self.ui.txt_Modelo.clear()
        self.ui.txt_Placa.clear()
        self.ui.chk_Ativo.setChecked(True)  # novo caminhão nasce ativo
