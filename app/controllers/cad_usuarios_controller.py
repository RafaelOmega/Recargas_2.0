# -*- coding: utf-8 -*-
"""Controller do cadastro de usuários.

Responsabilidade: APENAS controle de tela. Máquina de estados, busca
por código, salvar/excluir e mensagens comuns vêm de CadastroBase —
aqui ficam apenas os widgets, a validação e os dados do usuário.

O código é gerado automaticamente no salvar, mas o campo txt_Codigo
fica HABILITADO no estado inicial como campo de busca: digitar um
código e Enter carrega o usuário direto do banco (mesmo resultado
de selecionar na pesquisa); Enter com o campo vazio abre a pesquisa
completa. Em novo/edição o campo volta a bloquear (o código é gerado
ou é a chave do update).

Senha: obrigatória no novo (mínimo 4 caracteres); na edição,
vazia significa "manter a senha atual".
O hash nunca é exibido.
"""
from PySide6.QtWidgets import QMessageBox, QWidget

from app.controllers.cadastro_base import ESTADO_NOVO
from app.controllers.cadastro_base import CadastroBase
from app.views.ui_cad_usuarios import Ui_Cad_Usuarios

try:
    from app.services.usuario_service import UsuarioService
except ImportError:
    UsuarioService = None

_TAM_SENHA_MIN = 4


class CadUsuariosController(CadastroBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Cad_Usuarios()
        self.ui.setupUi(self)

        self._service = (UsuarioService()
                         if UsuarioService else None)

        self._w_pesquisar = self.ui.bt_Pesquisar_Usuario
        self._w_campos = [self.ui.txt_Nome, self.ui.txt_Documento,
                          self.ui.chk_Ativo, self.ui.txt_Usuario,
                          self.ui.txt_Senha]
        self._w_foco_novo = self.ui.txt_Nome

        self._inicializar()

    # ---------------- pesquisa ----------------

    def _pesquisar(self):
        from app.controllers.pesquisa_usuario_controller import (
            PesquisaUsuarioController,
        )
        dialogo = PesquisaUsuarioController(self)
        if dialogo.exec():
            usuario = dialogo.usuario_selecionado()
            if usuario:
                self._carregar_registro(usuario)

    # ---------------- hooks do CadastroBase ----------------

    def _definir_tab_order(self):
        """Ordem de tabulação em modo Z (esquerda->direita, cima->baixo).

        Linha 1 (frm_Codigo):   txt_Codigo -> bt_Pesquisar -> bt_Novo
        Linha 2 (frm_Corpo):    txt_Nome -> txt_Documento -> chk_Ativo
        Linha 3 (frm_Usuario):  txt_Usuario -> txt_Senha
        Linha 4 (frm_Crud):     bt_Salvar -> bt_Editar -> bt_Limpar
                                -> bt_Excluir
        """
        self.setTabOrder(self.ui.txt_Codigo,
                         self.ui.bt_Pesquisar_Usuario)
        self.setTabOrder(self.ui.bt_Pesquisar_Usuario, self.ui.bt_Novo)
        self.setTabOrder(self.ui.bt_Novo, self.ui.txt_Nome)
        self.setTabOrder(self.ui.txt_Nome, self.ui.txt_Documento)
        self.setTabOrder(self.ui.txt_Documento, self.ui.chk_Ativo)
        self.setTabOrder(self.ui.chk_Ativo, self.ui.txt_Usuario)
        self.setTabOrder(self.ui.txt_Usuario, self.ui.txt_Senha)
        self.setTabOrder(self.ui.txt_Senha, self.ui.bt_Salvar)
        self.setTabOrder(self.ui.bt_Salvar, self.ui.bt_Editar)
        self.setTabOrder(self.ui.bt_Editar, self.ui.bt_Limpar)
        self.setTabOrder(self.ui.bt_Limpar, self.ui.bt_Excluir)

    def _nome_registro(self) -> str:
        return "usuário"

    def _nome_service(self) -> str:
        return "usuários"

    def _msg_duplicidade(self) -> str:
        return "Já existe um usuário com esse código ou login."

    def _validar_obrigatorios(self) -> bool:
        if not self.ui.txt_Nome.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o nome.")
            self.ui.txt_Nome.setFocus()
            return False
        if not self.ui.txt_Usuario.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o usuário.")
            self.ui.txt_Usuario.setFocus()
            return False

        senha = self.ui.txt_Senha.text()
        if self._modo == ESTADO_NOVO or senha:
            # novo: senha obrigatória; edição: só valida se digitada
            if len(senha) < _TAM_SENHA_MIN:
                QMessageBox.warning(
                    self, "Atenção",
                    f"A senha deve ter pelo menos {_TAM_SENHA_MIN} "
                    "caracteres.")
                self.ui.txt_Senha.setFocus()
                return False
        return True

    def _coletar_dados(self) -> dict:
        return {
            "codigo": self.ui.txt_Codigo.text().strip(),
            "nome": self.ui.txt_Nome.text().strip(),
            "documento": self.ui.txt_Documento.text().strip(),
            "login": self.ui.txt_Usuario.text().strip(),
            "senha": self.ui.txt_Senha.text(),
            "ativo": self.ui.chk_Ativo.isChecked(),
        }

    def _preencher_campos(self, usuario):
        self.ui.txt_Nome.setText(usuario.nome)
        self.ui.txt_Documento.setText(usuario.documento)
        self.ui.txt_Usuario.setText(usuario.login)
        # senha nunca é exibida: vazia = manter a atual na edição
        self.ui.chk_Ativo.setChecked(usuario.ativo)

    def _limpar_especifico(self):
        self.ui.txt_Nome.clear()
        self.ui.txt_Documento.clear()
        self.ui.txt_Usuario.clear()
        self.ui.txt_Senha.clear()
        self.ui.chk_Ativo.setChecked(True)  # novo usuário nasce ativo

    def _foco_erro_validacao(self):
        self.ui.txt_Senha.setFocus()
