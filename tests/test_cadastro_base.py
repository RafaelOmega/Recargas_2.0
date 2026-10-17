# -*- coding: utf-8 -*-
"""Testes da CadastroBase — valem para os 4 cadastros que herdam dela
(colaboradores, usuários, saldo da conta e caminhões).

Estratégia: um filho mínimo (_CadastroFake) construído em código com os
widgets do contrato (txt_Codigo, botões do frm_Crud, campos) e um
service falso em memória. Cobre a máquina de estados, a busca por
código, salvar/excluir, a proteção multiusuário e o last-write-wins —
incluindo a regressão do bug do código vazio corrigido em 16/10/2026.

Atalhos e teclas são disparados pelos SINAIS (activated.emit,
returnPressed.emit) — determinístico, sem depender de janela ativa.
"""
from dataclasses import dataclass
from datetime import datetime

import pytest
from PySide6.QtWidgets import (QCheckBox, QLineEdit, QMessageBox,
                               QPushButton, QWidget)

from app.controllers.cadastro_base import (ESTADO_EDICAO, ESTADO_INICIAL,
                                           ESTADO_NOVO,
                                           ESTADO_VISUALIZACAO,
                                           CadastroBase)
from app.utils import sessao
from app.utils.erros import ConflitoEdicaoError


# ---------------- infraestrutura falsa ----------------

@dataclass
class RegistroFake:
    codigo: str
    nome: str
    ativo: bool = True
    atualizado_em: datetime | None = None
    pelo_usuario: str = ""


class ServiceFake:
    """Substitui o service real — mesma interface, sem banco.

    Reproduz o contrato last-write-wins: atualizar levanta
    ConflitoEdicaoError quando a versão enviada difere da atual;
    retorna False quando o registro não existe mais (excluído).

    buscar_por_codigo devolve uma CÓPIA do registro — igual ao
    repository real, que constrói um novo model a partir da linha do
    banco. Sem a cópia, a versão guardada pela base (_registro_carregado)
    seria o MESMO objeto vivo: simular outro usuário alteraria também a
    versão carregada e o conflito nunca seria detectado (bug dos testes
    de conflito, corrigido em 17/10/2026).
    """

    def __init__(self):
        self.registros = {}
        self.proximo_codigo = 1
        self.chamadas = []
        self.erro_salvar = None      # exceção simulada no salvar
        self.atualizar_ok = True     # False simula 'registro sumiu'
        self.falhar_busca = False    # True simula falha na recarga
        self.agora = datetime(2026, 10, 17, 12, 0, 0)  # relógio fixo

    def salvar(self, dados):
        self.chamadas.append(("salvar", dict(dados)))
        if self.erro_salvar is not None:
            raise self.erro_salvar
        codigo = str(self.proximo_codigo)
        self.proximo_codigo += 1
        registro = RegistroFake(codigo=codigo, nome=dados["nome"],
                                ativo=dados["ativo"],
                                atualizado_em=self.agora,
                                pelo_usuario=sessao.usuario_atual())
        self.registros[codigo] = registro
        return registro

    def atualizar(self, dados):
        self.chamadas.append(("atualizar", dict(dados)))
        if not self.atualizar_ok:
            return False
        registro = self.registros.get(str(dados.get("codigo")))
        if registro is None:
            return False
        if registro.atualizado_em != dados.get("atualizado_em"):
            raise ConflitoEdicaoError(
                f"Registro {registro.codigo} alterado por outro usuário.")
        registro.nome = dados["nome"]
        registro.ativo = dados["ativo"]
        registro.atualizado_em = self.agora
        registro.pelo_usuario = sessao.usuario_atual()
        return True

    def excluir(self, codigo):
        self.chamadas.append(("excluir", str(codigo)))
        return self.registros.pop(str(codigo), None) is not None

    def buscar_por_codigo(self, codigo):
        self.chamadas.append(("buscar", str(codigo)))
        if self.falhar_busca:
            raise RuntimeError("falha de banco")
        registro = self.registros.get(str(codigo))
        if registro is None:
            return None
        # cópia: o repository real devolve um NOVO model da linha do
        # banco — a versão carregada pela base é um snapshot
        return RegistroFake(codigo=registro.codigo, nome=registro.nome,
                            ativo=registro.ativo,
                            atualizado_em=registro.atualizado_em,
                            pelo_usuario=registro.pelo_usuario)


class _UiFake:
    """Widgets do contrato da CadastroBase, parentados na tela."""

    def __init__(self, tela: QWidget):
        self.txt_Codigo = QLineEdit(tela)
        self.bt_Novo = QPushButton(tela)
        self.bt_Salvar = QPushButton(tela)
        self.bt_Editar = QPushButton(tela)
        self.bt_Limpar = QPushButton(tela)
        self.bt_Excluir = QPushButton(tela)
        self.bt_Pesquisar = QPushButton(tela)
        self.txt_Nome = QLineEdit(tela)
        self.chk_Ativo = QCheckBox(tela)


class CadastroFake(CadastroBase):
    """Filho mínimo: só o que o contrato da base exige."""

    def __init__(self, service: ServiceFake):
        super().__init__()
        self.ui = _UiFake(self)
        self._service = service
        self._w_pesquisar = self.ui.bt_Pesquisar
        self._w_campos = [self.ui.txt_Nome, self.ui.chk_Ativo]
        self._w_foco_novo = self.ui.txt_Nome
        self.pesquisas = 0
        self._registro_pesquisa = None
        self._inicializar()

    # ---------------- hooks obrigatórios ----------------

    def _definir_tab_order(self):
        pass

    def _pesquisar(self):
        self.pesquisas += 1
        if self._registro_pesquisa is not None:
            self._carregar_registro(self._registro_pesquisa)

    def _nome_registro(self):
        return "registro"

    def _nome_service(self):
        return "testes"

    def _msg_duplicidade(self):
        return "Registro duplicado."

    def _validar_obrigatorios(self):
        if not self.ui.txt_Nome.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o nome.")
            self.ui.txt_Nome.setFocus()
            return False
        return True

    def _coletar_dados(self):
        return {"codigo": self.ui.txt_Codigo.text().strip(),
                "nome": self.ui.txt_Nome.text().strip(),
                "ativo": self.ui.chk_Ativo.isChecked()}

    def _preencher_campos(self, registro):
        self.ui.txt_Nome.setText(registro.nome)
        self.ui.chk_Ativo.setChecked(registro.ativo)

    def _limpar_especifico(self):
        self.ui.txt_Nome.clear()
        self.ui.chk_Ativo.setChecked(True)


# ---------------- fixtures ----------------

@pytest.fixture(autouse=True)
def _sessao_limpa():
    """Sessão vazia em todos os testes (isolamento do carimbo)."""
    sessao.limpar()
    yield
    sessao.limpar()


@pytest.fixture
def service():
    return ServiceFake()


@pytest.fixture
def tela(qtbot, service, caixas):
    tela = CadastroFake(service)
    qtbot.addWidget(tela)
    return tela


# ---------------- estados ----------------

def test_estado_inicial(tela):
    """Abertura: busca liberada; só '...' e '+' ativos."""
    assert tela._modo == ESTADO_INICIAL
    assert tela.ui.txt_Codigo.isEnabled()
    assert tela.ui.bt_Pesquisar.isEnabled()
    assert tela.ui.bt_Novo.isEnabled()
    assert not tela.ui.txt_Nome.isEnabled()
    assert not tela.ui.bt_Salvar.isEnabled()
    assert not tela.ui.bt_Editar.isEnabled()
    assert not tela.ui.bt_Excluir.isEnabled()
    assert not tela.ui.bt_Limpar.isEnabled()


def test_novo_libera_campos(tela):
    tela.ui.bt_Novo.click()
    assert tela._modo == ESTADO_NOVO
    assert not tela.ui.txt_Codigo.isEnabled()   # código é automático
    assert tela.ui.txt_Codigo.text() == ""
    assert tela.ui.txt_Nome.isEnabled()
    assert tela.ui.bt_Salvar.isEnabled()
    assert tela.ui.bt_Limpar.isEnabled()
    assert not tela.ui.bt_Editar.isEnabled()
    assert not tela.ui.bt_Excluir.isEnabled()
    assert not tela.ui.bt_Novo.isEnabled()
    assert not tela.ui.bt_Pesquisar.isEnabled()


def test_novo_somente_do_estado_inicial(tela):
    tela._carregar_registro(RegistroFake(codigo="1", nome="Um"))
    tela._novo()                     # guarda: ignorado fora do inicial
    assert tela._modo == ESTADO_VISUALIZACAO


def test_f2_abre_novo(tela):
    tela._at_f2.activated.emit()     # dispara o atalho F2 da base
    assert tela._modo == ESTADO_NOVO


def test_limpar_volta_ao_inicial(tela):
    tela.ui.bt_Novo.click()
    tela.ui.txt_Nome.setText("Alguém")
    tela.ui.bt_Limpar.click()
    assert tela._modo == ESTADO_INICIAL
    assert tela.ui.txt_Nome.text() == ""
    assert tela.ui.chk_Ativo.isChecked()   # novo registro nasce ativo


def test_liberar_edicao_somente_da_visualizacao(tela):
    tela._liberar_edicao()           # do inicial: ignorado
    assert tela._modo == ESTADO_INICIAL


# ---------------- busca por código ----------------

def test_enter_com_codigo_busca_direto(tela, service):
    service.registros["7"] = RegistroFake(codigo="7", nome="Sete")
    tela.ui.txt_Codigo.setText("7")
    tela.ui.txt_Codigo.returnPressed.emit()
    assert ("buscar", "7") in service.chamadas
    assert tela._modo == ESTADO_VISUALIZACAO
    assert tela.ui.txt_Nome.text() == "Sete"
    assert tela.ui.bt_Editar.isEnabled()


def test_enter_vazio_abre_pesquisa(tela):
    tela.ui.txt_Codigo.returnPressed.emit()
    assert tela.pesquisas == 1


def test_codigo_inexistente_avisa(tela, caixas):
    tela.ui.txt_Codigo.setText("99")
    tela._enter_codigo()
    assert caixas.alguma("não encontrado")
    assert tela._modo == ESTADO_INICIAL
    assert tela.ui.txt_Codigo.selectedText() == "99"  # selectAll aplicado


def test_carregar_registro_preenche_codigo(tela):
    """REGRESSÃO do bug de 16/10/2026: a base repõe o txt_Codigo.
    Sem isso, o salvar em edição gravava UPDATE com código vazio
    (falso 'não existe mais')."""
    tela._carregar_registro(RegistroFake(codigo="42", nome="Resposta"))
    assert tela.ui.txt_Codigo.text() == "42"
    assert tela.ui.txt_Nome.text() == "Resposta"
    assert tela._modo == ESTADO_VISUALIZACAO


# ---------------- salvar ----------------

def test_salvar_novo_grava(tela, service, caixas):
    tela.ui.bt_Novo.click()
    tela.ui.txt_Nome.setText("Novo Registro")
    tela.ui.bt_Salvar.click()
    assert ("salvar", {"codigo": "", "nome": "Novo Registro",
                       "ativo": True}) in service.chamadas
    assert caixas.do_tipo("information")          # sucesso
    assert tela._modo == ESTADO_INICIAL           # tela limpa após salvar
    assert tela.ui.txt_Nome.text() == ""


def test_salvar_bloqueia_sem_obrigatorio(tela, service, caixas):
    tela.ui.bt_Novo.click()
    tela.ui.bt_Salvar.click()                     # nome vazio
    assert not any(t == "salvar" for (t, _) in service.chamadas)
    assert caixas.do_tipo("warning")


def test_salvar_edicao_atualiza(tela, service):
    service.registros["3"] = RegistroFake(codigo="3", nome="Original")
    tela.ui.txt_Codigo.setText("3")
    tela._enter_codigo()
    tela.ui.bt_Editar.click()
    tela.ui.txt_Nome.setText("Editado")
    tela.ui.bt_Salvar.click()
    assert ("atualizar", {"codigo": "3", "nome": "Editado",
                          "ativo": True,
                          "atualizado_em": None}) in service.chamadas
    assert service.registros["3"].nome == "Editado"


def test_salvar_edicao_sem_codigo_bloqueado(tela, service, caixas):
    """Guarda defensiva: edição sem código não dispara UPDATE."""
    tela._modo = ESTADO_EDICAO
    tela._estado_edicao()
    tela.ui.txt_Nome.setText("Sem código")
    tela.ui.bt_Salvar.click()
    assert not any(t == "atualizar" for (t, _) in service.chamadas)
    assert caixas.alguma("Nenhum registro carregado")


def test_salvar_edicao_registro_sumiu(tela, service, caixas):
    """Multiusuário: outro usuário excluiu durante a edição."""
    service.registros["5"] = RegistroFake(codigo="5", nome="Some")
    tela.ui.txt_Codigo.setText("5")
    tela._enter_codigo()
    tela.ui.bt_Editar.click()
    service.atualizar_ok = False      # simula exclusão concorrente
    tela.ui.bt_Salvar.click()
    assert caixas.alguma("excluído por outro usuário")
    assert tela._modo == ESTADO_INICIAL
    assert tela.ui.txt_Codigo.text() == ""


def test_salvar_valueerror_vira_aviso(tela, service, caixas):
    tela.ui.bt_Novo.click()
    tela.ui.txt_Nome.setText("Com erro")
    service.erro_salvar = ValueError("senha curta")
    tela.ui.bt_Salvar.click()
    assert caixas.alguma("senha curta")
    assert caixas.do_tipo("warning")
    assert not caixas.do_tipo("critical")


def test_salvar_erro_inesperado_vira_critico(tela, service, caixas):
    tela.ui.bt_Novo.click()
    tela.ui.txt_Nome.setText("Com falha")
    service.erro_salvar = RuntimeError("falha de banco")
    tela.ui.bt_Salvar.click()
    assert caixas.do_tipo("critical")


def test_salvar_em_visualizacao_ignorado(tela, service):
    service.registros["1"] = RegistroFake(codigo="1", nome="Um")
    tela.ui.txt_Codigo.setText("1")
    tela._enter_codigo()              # visualizacao
    tela._salvar()                    # guarda: não faz nada
    assert not any(t in ("salvar", "atualizar")
                   for (t, _) in service.chamadas)


# ---------------- last-write-wins ----------------

def test_base_injeta_versao_carregada(tela, service):
    """No salvar em edição, a base envia a versão carregada."""
    versao = datetime(2026, 10, 17, 11, 0, 0)
    service.registros["3"] = RegistroFake(codigo="3", nome="Original",
                                          atualizado_em=versao)
    tela.ui.txt_Codigo.setText("3")
    tela._enter_codigo()
    tela.ui.bt_Editar.click()
    tela.ui.txt_Nome.setText("Editado")
    tela.ui.bt_Salvar.click()
    assert ("atualizar", {"codigo": "3", "nome": "Editado",
                          "ativo": True,
                          "atualizado_em": versao}) in service.chamadas


def test_conflito_avisa_e_recarrega(tela, service, caixas):
    """Outro usuário salvou durante a edição: avisa e mostra a versão
    mais recente em visualização, em vez de sobrescrever calado."""
    service.registros["3"] = RegistroFake(codigo="3", nome="Original")
    tela.ui.txt_Codigo.setText("3")
    tela._enter_codigo()
    tela.ui.bt_Editar.click()
    # outro usuário salva enquanto a edição está aberta
    service.registros["3"].nome = "Editado por outro"
    service.registros["3"].atualizado_em = datetime(2026, 10, 17, 12, 30)
    tela.ui.txt_Nome.setText("Minha edição")
    tela.ui.bt_Salvar.click()
    assert caixas.alguma("alterado por outro usuário")
    assert tela._modo == ESTADO_VISUALIZACAO
    assert tela.ui.txt_Nome.text() == "Editado por outro"
    assert tela.ui.txt_Codigo.text() == "3"


def test_conflito_recarrego_falhou_limpa(tela, service, caixas):
    """Conflito detectado e a recarga da versão mais recente falhou:
    a tela é limpa (não fica presa numa edição órfã)."""
    service.registros["4"] = RegistroFake(codigo="4", nome="Some")
    tela.ui.txt_Codigo.setText("4")
    tela._enter_codigo()
    tela.ui.bt_Editar.click()
    # outro usuário salva enquanto a edição está aberta
    service.registros["4"].atualizado_em = datetime(2026, 10, 17, 12, 30)
    service.falhar_busca = True       # recarga após o conflito falha
    tela.ui.bt_Salvar.click()
    assert caixas.alguma("alterado por outro usuário")
    assert tela._modo == ESTADO_INICIAL
    assert tela.ui.txt_Codigo.text() == ""


def test_sessao_carimba_pelo_usuario(tela, service):
    """INSERT carimba o login da sessão (last-write-wins)."""
    sessao.definir_usuario("rafael")
    tela.ui.bt_Novo.click()
    tela.ui.txt_Nome.setText("Com sessão")
    tela.ui.bt_Salvar.click()
    assert service.registros["1"].pelo_usuario == "rafael"


# ---------------- excluir ----------------

def test_excluir_com_confirmacao(tela, service, caixas):
    service.registros["8"] = RegistroFake(codigo="8", nome="Oito")
    tela.ui.txt_Codigo.setText("8")
    tela._enter_codigo()
    caixas.resposta_question = QMessageBox.StandardButton.Yes
    tela.ui.bt_Excluir.click()
    assert ("excluir", "8") in service.chamadas
    assert caixas.do_tipo("information")
    assert tela._modo == ESTADO_INICIAL


def test_excluir_cancelado_nao_chama_service(tela, service, caixas):
    service.registros["8"] = RegistroFake(codigo="8", nome="Oito")
    tela.ui.txt_Codigo.setText("8")
    tela._enter_codigo()
    caixas.resposta_question = QMessageBox.StandardButton.No
    tela.ui.bt_Excluir.click()
    assert not any(t == "excluir" for (t, _) in service.chamadas)
    assert tela._modo == ESTADO_VISUALIZACAO   # registro continua na tela


def test_excluir_registro_sumiu(tela, service, caixas):
    service.registros["9"] = RegistroFake(codigo="9", nome="Nove")
    tela.ui.txt_Codigo.setText("9")
    tela._enter_codigo()
    del service.registros["9"]        # outro usuário já havia excluído
    tela.ui.bt_Excluir.click()        # confirma Sim (padrão)
    assert ("excluir", "9") in service.chamadas
    assert caixas.alguma("já foi excluído")
    assert tela._modo == ESTADO_INICIAL
