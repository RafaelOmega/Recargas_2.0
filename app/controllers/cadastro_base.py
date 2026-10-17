# -*- coding: utf-8 -*-
"""Base dos cadastros simples (colaboradores, usuários, saldo da conta
e caminhões).

Absorve o esqueleto comum às quatro telas — máquina de estados, busca
por código, salvar/excluir com proteção multiusuário e mensagens —
para que um ajuste de comportamento comum seja feito UMA vez aqui e
valha para todos os cadastros.

Contrato do filho:
  - no __init__: criar a UI (self.ui), definir self._service,
    self._w_pesquisar, self._w_campos, self._w_foco_novo e chamar
    self._inicializar() por último;
  - implementar: _definir_tab_order(), _pesquisar(), _nome_registro(),
    _nome_service(), _msg_duplicidade(), _validar_obrigatorios(),
    _coletar_dados(), _preencher_campos(registro), _limpar_especifico();
  - opcional: _foco_erro_validacao() (ex.: senha curta do usuário).

Estados (iguais em todos os cadastros):
  inicial      -> busca por código liberada; só "..." e "+" ativos
  novo         -> campos liberados, Salvar grava (código automático)
  visualizacao -> registro carregado (somente leitura)
  edicao       -> "Editar" liberou os campos; Salvar atualiza

Multiusuário:
  - atualizar/excluir retornam False quando o registro não existe
    mais (excluído por outro usuário) — a tela avisa e limpa em vez
    de fingir sucesso;
  - last-write-wins: a base guarda a versão carregada (atualizado_em)
    e a injeta no salvar em edição; alterada por outro usuário, o
    service levanta ConflitoEdicaoError — a tela avisa e recarrega a
    versão mais recente em vez de sobrescrever calado.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox, QWidget

from app.utils.erros import ConflitoEdicaoError, mensagem_erro
from app.utils.logger import get_logger

logger = get_logger("cadastro_base")

ESTADO_INICIAL = "inicial"
ESTADO_NOVO = "novo"
ESTADO_VISUALIZACAO = "visualizacao"
ESTADO_EDICAO = "edicao"

_MSG_REGISTRO_SUMIU = ("Registro não encontrado — provavelmente foi "
                       "excluído por outro usuário. A tela será limpa.")
_MSG_CONFLITO_EDICAO = (
    "Registro alterado por outro usuário — a tela foi atualizada com "
    "a versão mais recente. Revise e salve novamente se necessário.")


class CadastroBase(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._modo = ESTADO_INICIAL
        self._registro_carregado = None   # versão p/ last-write-wins

    # ---------------- fase 2 (chamada pelo filho) ----------------

    def _inicializar(self):
        """Conecta sinais, tab order, limpa e foca — chamar no fim do
        __init__ do filho, após definir _service e os widgets _w_*."""
        if getattr(self, "_service", None) is None:
            logger.warning("%s: service nao encontrado - acoes desativadas",
                           type(self).__name__)
        self._conectar_botoes()
        self._conectar_teclas()
        self._definir_tab_order()
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    # ---------------- conexões ----------------

    def _conectar_botoes(self):
        self.ui.bt_Novo.clicked.connect(self._novo)
        self._w_pesquisar.clicked.connect(self._pesquisar)
        self.ui.bt_Salvar.clicked.connect(self._salvar)
        self.ui.bt_Editar.clicked.connect(self._liberar_edicao)
        self.ui.bt_Limpar.clicked.connect(self._limpar_campos)
        self.ui.bt_Excluir.clicked.connect(self._excluir)

    def _conectar_teclas(self):
        # Enter no código: com texto busca direto; vazio abre a pesquisa
        self.ui.txt_Codigo.returnPressed.connect(self._enter_codigo)
        self._at_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self._at_f2.activated.connect(self._novo)

    # ---------------- estados da tela ----------------

    def _grupo(self, widgets, habilitar: bool):
        for widget in widgets:
            widget.setEnabled(habilitar)

    def _estado_inicial(self):
        self.ui.txt_Codigo.setEnabled(True)   # campo de busca liberado
        self._w_pesquisar.setEnabled(True)
        self.ui.bt_Novo.setEnabled(True)

        self._grupo(self._w_campos, False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Limpar.setEnabled(False)

    def _estado_novo(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é automático
        self.ui.txt_Codigo.clear()
        self._grupo(self._w_campos, True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Excluir.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self._w_pesquisar.setEnabled(False)

    def _estado_visualizacao(self):
        self.ui.txt_Codigo.setEnabled(False)  # evita alterar a chave
        self._grupo(self._w_campos, False)
        self.ui.bt_Salvar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self._w_pesquisar.setEnabled(False)
        self.ui.bt_Editar.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)

    def _estado_edicao(self):
        self.ui.txt_Codigo.setEnabled(False)  # código é a chave
        self._grupo(self._w_campos, True)
        self.ui.bt_Salvar.setEnabled(True)
        self.ui.bt_Excluir.setEnabled(True)
        self.ui.bt_Limpar.setEnabled(True)
        self.ui.bt_Editar.setEnabled(False)
        self.ui.bt_Novo.setEnabled(False)
        self._w_pesquisar.setEnabled(False)

    # ---------------- ações de tela ----------------

    def _iniciar_novo(self):
        self._limpar_campos()
        self._modo = ESTADO_NOVO
        self._estado_novo()
        self._w_foco_novo.setFocus()

    def _novo(self):
        if self._modo != ESTADO_INICIAL:
            return
        self._iniciar_novo()

    def _liberar_edicao(self):
        if self._modo != ESTADO_VISUALIZACAO:
            return
        self._modo = ESTADO_EDICAO
        self._estado_edicao()
        self._w_foco_novo.setFocus()

    def _enter_codigo(self):
        """Enter no código: com texto busca direto; vazio abre pesquisa."""
        if self.ui.txt_Codigo.text().strip():
            self._buscar_por_codigo()
        else:
            self._pesquisar()

    def _buscar_por_codigo(self):
        """Carrega o registro do código digitado direto do banco."""
        if self._service is None:
            self._aviso_service()
            return
        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            return
        try:
            registro = self._service.buscar_por_codigo(codigo)
        except Exception as exc:
            logger.exception("Falha ao buscar %s %s",
                             self._nome_registro(), codigo)
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível buscar o {self._nome_registro()}:"
                f"\n{self._mensagem_erro(exc)}")
            return
        if registro is None:
            QMessageBox.information(
                self, "Não encontrado",
                f"{self._nome_registro().capitalize()} {codigo} "
                "não encontrado.")
            self.ui.txt_Codigo.setFocus()
            self.ui.txt_Codigo.selectAll()
            return
        self._carregar_registro(registro)

    def _carregar_registro(self, registro):
        """Limpa, preenche código + campos do filho e entra em
        visualização.

        O código é responsabilidade da BASE: sem ele o salvar em
        edição gravaria um UPDATE com WHERE codigo = '' (nunca casa,
        falso 'não existe mais' — bug corrigido em 16/10/2026).
        A versão carregada (atualizado_em) fica guardada para o
        last-write-wins no salvar em edição.
        """
        self._limpar_campos()
        self.ui.txt_Codigo.setText(str(registro.codigo))
        self._preencher_campos(registro)
        self._registro_carregado = registro
        self._modo = ESTADO_VISUALIZACAO
        self._estado_visualizacao()

    def _salvar(self):
        if self._service is None:
            self._aviso_service()
            return
        if not self._validar_obrigatorios():
            return
        dados = self._coletar_dados()
        try:
            if self._modo == ESTADO_NOVO:
                registro = self._service.salvar(dados)
                # exibe o código gerado automaticamente
                self.ui.txt_Codigo.setText(str(registro.codigo))
            elif self._modo == ESTADO_EDICAO:
                if not dados.get("codigo"):
                    # guarda defensiva: edição sem código não tem
                    # o que atualizar (evita UPDATE WHERE codigo = '')
                    QMessageBox.warning(
                        self, "Atenção",
                        "Nenhum registro carregado para atualizar.")
                    return
                # last-write-wins: envia a versão carregada; o UPDATE
                # só aplica se ela ainda for a atual no banco
                dados["atualizado_em"] = getattr(
                    self._registro_carregado, "atualizado_em", None)
                if not self._service.atualizar(dados):
                    # outro usuário excluiu o registro enquanto a
                    # edição estava aberta
                    logger.warning(
                        "Atualização sem efeito: %s %s não existe mais",
                        self._nome_registro(), dados.get("codigo"))
                    QMessageBox.warning(self, "Atenção",
                                        _MSG_REGISTRO_SUMIU)
                    self._limpar_campos()
                    self.ui.txt_Codigo.setFocus()
                    return
            else:
                return
        except ConflitoEdicaoError:
            logger.warning("Conflito de edição: %s %s alterado por "
                           "outro usuário",
                           self._nome_registro(), dados.get("codigo"))
            QMessageBox.warning(self, "Atenção", _MSG_CONFLITO_EDICAO)
            registro = None
            try:
                registro = self._service.buscar_por_codigo(
                    str(dados.get("codigo")))
            except Exception:
                logger.exception("Falha ao recarregar após conflito")
            if registro is not None:
                self._carregar_registro(registro)
            else:
                self._limpar_campos()
                self.ui.txt_Codigo.setFocus()
            return
        except ValueError as exc:
            QMessageBox.warning(self, "Atenção", str(exc))
            self._foco_erro_validacao()
            return
        except Exception as exc:
            logger.exception("Falha ao salvar %s", self._nome_registro())
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível salvar o {self._nome_registro()}:"
                f"\n{self._mensagem_erro(exc)}")
            return

        logger.info("%s salvo", self._nome_registro().capitalize())
        QMessageBox.information(
            self, "Sucesso",
            f"{self._nome_registro().capitalize()} salvo com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    def _excluir(self):
        if self._service is None:
            self._aviso_service()
            return
        codigo = self.ui.txt_Codigo.text().strip()
        if not codigo:
            return
        resposta = QMessageBox.question(
            self, "Excluir",
            f"Excluir o {self._nome_registro()} {codigo}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resposta != QMessageBox.StandardButton.Yes:
            return
        try:
            excluido = self._service.excluir(codigo)
        except Exception as exc:
            logger.exception("Falha ao excluir %s", self._nome_registro())
            QMessageBox.critical(
                self, "Erro",
                f"Não foi possível excluir:\n{self._mensagem_erro(exc)}")
            return
        if not excluido:
            # outro usuário já havia excluído
            logger.warning("Exclusão sem efeito: %s %s não existe mais",
                           self._nome_registro(), codigo)
            QMessageBox.warning(
                self, "Atenção",
                f"{self._nome_registro().capitalize()} não encontrado — "
                "provavelmente já foi excluído por outro usuário.")
            self._limpar_campos()
            self.ui.txt_Codigo.setFocus()
            return
        logger.info("%s excluído: %s",
                    self._nome_registro().capitalize(), codigo)
        QMessageBox.information(
            self, "Sucesso",
            f"{self._nome_registro().capitalize()} excluído com sucesso.")
        self._limpar_campos()
        self.ui.txt_Codigo.setFocus()

    # ---------------- mensagens ----------------

    def _aviso_service(self):
        QMessageBox.critical(
            self, "Erro",
            f"Service de {self._nome_service()} indisponível.")

    def _mensagem_erro(self, exc: Exception) -> str:
        return mensagem_erro(exc, duplicidade=self._msg_duplicidade())

    # ---------------- campos ----------------

    def _limpar_campos(self):
        self.ui.txt_Codigo.clear()
        self._limpar_especifico()
        self._registro_carregado = None
        self._modo = ESTADO_INICIAL
        self._estado_inicial()

    # ---------------- hooks do filho (obrigatórios) ----------------

    def _definir_tab_order(self):
        raise NotImplementedError

    def _pesquisar(self):
        """Abre a pesquisa da tela e chama _carregar_registro com o
        registro selecionado."""
        raise NotImplementedError

    def _nome_registro(self):
        raise NotImplementedError

    def _nome_service(self):
        raise NotImplementedError

    def _msg_duplicidade(self):
        raise NotImplementedError

    def _validar_obrigatorios(self):
        raise NotImplementedError

    def _coletar_dados(self):
        raise NotImplementedError

    def _preencher_campos(self, registro):
        raise NotImplementedError

    def _limpar_especifico(self):
        raise NotImplementedError

    # ---------------- hooks do filho (opcionais) ----------------

    def _foco_erro_validacao(self):
        """Foco após ValueError no salvar (ex.: senha curta do usuário)."""
        pass
