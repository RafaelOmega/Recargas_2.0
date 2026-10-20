# -*- coding: utf-8 -*-
"""Testes dos repositories com conexão FAKE (nenhum banco).

Por que existem: toda a lógica crítica do sistema (SQL, transações,
substituição de itens, last-write-wins) vivia fora da suíte — os
testes cobriam só controllers com services falsos. Foi assim que o
vazamento de conexão dos relatórios passou despercebido.

Infra: a conexão fake imita o protocolo do psycopg2 que os
repositories usam:
  - `with conn:`          -> contexto transacional (commit/rollback)
  - `conn.cursor()`       -> contexto do cursor
  - `cur.execute(sql, p)` -> registra a consulta e consome o roteiro
  - `cur.fetchone()` / `cur.fetchall()` / `cur.rowcount`

Cada `execute` consome uma entrada do roteiro programado para ele,
então o teste descreve exatamente o que o banco devolveria em cada
passo (UPDATE sem casar, SELECT de existência, etc.).

O `get_connection` é substituído por módulo; assim os testes provam
o ciclo abrir -> usar -> FECHAR, que é a correção do vazamento.
"""
import importlib
from datetime import date, datetime
from types import SimpleNamespace

import pytest

from app.models.abastecimento import Abastecimento
from app.models.recarga import Recarga, RecargaItem
from app.repositories.abastecimento_repository import (
    AbastecimentoRepository,
)
from app.repositories.recarga_repository import RecargaRepository
from app.repositories.relatorio_abastecimento_repository import (
    RelatorioAbastecimentoRepository,
)
from app.repositories.relatorio_recarga_colaborador_repository import (
    RelatorioRecargaColaboradorRepository,
)
from app.utils.erros import ConflitoEdicaoError

_MODULOS = (
    "app.repositories.recarga_repository",
    "app.repositories.abastecimento_repository",
    "app.repositories.relatorio_abastecimento_repository",
    "app.repositories.relatorio_recarga_colaborador_repository",
)


# ---------------- infraestrutura fake ----------------

class _CursorFake:
    """Cursor que consome um roteiro programado pelo teste."""

    def __init__(self, conexao):
        self._conexao = conexao
        self._atual: dict = {}
        self.rowcount = 0

    def execute(self, sql, params=None):
        self._conexao.consultas.append(
            (" ".join(str(sql).split()), params))
        self._atual = (self._conexao.roteiro.pop(0)
                       if self._conexao.roteiro else {})
        self.rowcount = self._atual.get("rowcount", 0)

    def fetchone(self):
        return self._atual.get("fetchone")

    def fetchall(self):
        return self._atual.get("fetchall", [])

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _ConexaoFake:
    """Conexão que registra commits, rollbacks, consultas e o close."""

    def __init__(self, roteiro=None):
        self.roteiro = list(roteiro or [])
        self.consultas: list = []
        self.commits = 0
        self.rollbacks = 0
        self.fechada = False

    def cursor(self):
        return _CursorFake(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.commits += 1
        else:
            self.rollbacks += 1
        return False

    def close(self):
        self.fechada = True


@pytest.fixture
def conexoes(monkeypatch):
    """Substitui get_connection nos 4 módulos por conexões fake.

    Uso:
      conexoes.programar([{...}])  # roteiro da PRÓXIMA conexão
      conexoes.criadas             # conexões abertas por get_connection
    """
    roteiros: list = []
    criadas: list = []

    def _get_connection():
        roteiro = roteiros.pop(0) if roteiros else []
        conn = _ConexaoFake(roteiro)
        criadas.append(conn)
        return conn

    def _programar(roteiro):
        roteiros.append(roteiro)

    for nome in _MODULOS:
        modulo = importlib.import_module(nome)
        monkeypatch.setattr(modulo, "get_connection", _get_connection)

    return SimpleNamespace(programar=_programar, criadas=criadas)


def _recarga(sequencia=7, itens=None) -> Recarga:
    return Recarga(
        sequencia=sequencia,
        data=date(2026, 10, 20),
        itens=itens if itens is not None else [
            RecargaItem(nome="Ana", documento="123", valor=50.0)],
    )


def _abastecimento(sequencia=5, itens=None) -> Abastecimento:
    return Abastecimento(
        sequencia=sequencia,
        data=date(2026, 10, 20),
        itens=itens if itens is not None else [],
    )


# ---------------- vazamento de conexão (regressão 2.8.2) ----------------

def test_relatorio_abastecimento_fecha_a_conexao(conexoes):
    """A consulta do relatório abre E fecha a conexão.

    Regressão do vazamento: antes o __init__ abria a conexão e nunca
    a fechava, esgotando o max_connections do PostgreSQL.
    """
    conexoes.programar([{"fetchall": []}])

    RelatorioAbastecimentoRepository().itens_por_caminhao()

    assert len(conexoes.criadas) == 1
    assert conexoes.criadas[0].fechada is True


def test_relatorio_recarga_fecha_a_conexao(conexoes):
    """Mesma garantia para o relatório de recargas por colaborador."""
    conexoes.programar([{"fetchall": []}])

    RelatorioRecargaColaboradorRepository().itens_por_colaborador()

    assert len(conexoes.criadas) == 1
    assert conexoes.criadas[0].fechada is True


def test_relatorio_abre_uma_conexao_por_consulta(conexoes):
    """Duas consultas = duas conexões, ambas fechadas."""
    conexoes.programar([{"fetchall": []}, {"fetchall": []}])
    repo = RelatorioAbastecimentoRepository()

    repo.itens_por_caminhao()
    repo.itens_por_caminhao()

    assert len(conexoes.criadas) == 2
    assert all(c.fechada for c in conexoes.criadas)


def test_conn_injetado_nao_e_fechado(conexoes):
    """Conexão injetada em teste é do chamador — não fechamos."""
    conn = _ConexaoFake([{"fetchall": []}])

    RelatorioAbastecimentoRepository(conn=conn).itens_por_caminhao()

    assert conn.fechada is False


def test_filtro_nao_interpola_entrada_no_sql(conexoes):
    """A placa vira parâmetro — nunca entra no texto do SQL."""
    conexoes.programar([{"fetchall": []}])

    RelatorioAbastecimentoRepository().itens_por_caminhao(
        "ABC; DROP TABLE caminhoes")

    sql, params = conexoes.criadas[0].consultas[0]
    assert "DROP TABLE" not in sql
    assert any("DROP TABLE" in str(p) for p in params)


# ---------------- recarga_repository: escrita ----------------

def test_recarga_salvar_grava_cabecalho_e_itens(conexoes):
    """Salvar insere o cabeçalho e um INSERT por item, na mesma transação."""
    conexoes.programar([
        {"fetchone": (1, 7, datetime(2026, 10, 20, 12, 0, 0))},  # cabeçalho
        {"fetchone": (10,)},                                     # item 1
        {"fetchone": (11,)},                                     # item 2
    ])
    recarga = _recarga(itens=[
        RecargaItem(nome="Ana", valor=50.0),
        RecargaItem(nome="Bruno", valor=30.0),
    ])

    gravada = RecargaRepository().salvar(recarga)

    assert gravada.id == 1
    assert gravada.sequencia == 7
    assert len(gravada.itens) == 2
    conn = conexoes.criadas[0]
    assert conn.commits == 1          # tudo em UMA transação
    assert conn.fechada is True
    assert len(conn.consultas) == 3   # 1 cabeçalho + 2 itens


def test_recarga_salvar_fecha_conexao_em_falha(conexoes):
    """Erro no meio da gravação: rollback e conexão fechada."""
    conexoes.programar([{"fetchone": None}])   # RETURNING sem linha

    with pytest.raises(Exception):
        RecargaRepository().salvar(_recarga())

    conn = conexoes.criadas[0]
    assert conn.rollbacks == 1
    assert conn.fechada is True


def test_recarga_atualizar_retorna_true_quando_casa(conexoes):
    """UPDATE que casa a versão: substitui os itens e confirma."""
    conexoes.programar([
        {"fetchone": (1, datetime(2026, 10, 20, 13, 0, 0))},  # UPDATE
        {},                                                    # DELETE itens
        {"fetchone": (20,)},                                   # item
    ])

    atualizado = RecargaRepository().atualizar(_recarga())

    assert atualizado is True
    assert conexoes.criadas[0].commits == 1
    assert conexoes.criadas[0].fechada is True


def test_recarga_atualizar_levanta_conflito(conexoes):
    """UPDATE não casou mas a recarga existe -> ConflitoEdicaoError."""
    conexoes.programar([
        {"fetchone": None},              # UPDATE não casou
        {"fetchone": (1,)},              # SELECT 1: existe
    ])

    with pytest.raises(ConflitoEdicaoError):
        RecargaRepository().atualizar(_recarga())

    conn = conexoes.criadas[0]
    assert conn.rollbacks == 1           # nada foi gravado
    assert conn.fechada is True


def test_recarga_atualizar_retorna_false_quando_excluida(conexoes):
    """UPDATE não casou e a recarga não existe mais -> False."""
    conexoes.programar([
        {"fetchone": None},              # UPDATE não casou
        {"fetchone": None},              # SELECT 1: não existe
    ])

    assert RecargaRepository().atualizar(_recarga()) is False
    assert conexoes.criadas[0].fechada is True


# ---------------- recarga_repository: exclusão ----------------

def test_recarga_excluir_retorna_true_quando_havia_registro(conexoes):
    conexoes.programar([{"rowcount": 1}])

    assert RecargaRepository().excluir(7) is True
    assert conexoes.criadas[0].commits == 1
    assert conexoes.criadas[0].fechada is True


def test_recarga_excluir_retorna_false_quando_nao_existe(conexoes):
    """Excluir algo já removido por outro usuário devolve False."""
    conexoes.programar([{"rowcount": 0}])

    assert RecargaRepository().excluir(7) is False
    assert conexoes.criadas[0].fechada is True


# ---------------- recarga_repository: leitura ----------------

def test_recarga_buscar_por_sequencia_devolve_none_quando_nao_existe(
        conexoes):
    conexoes.programar([{"fetchone": None}])

    assert RecargaRepository().buscar_por_sequencia(99) is None
    assert conexoes.criadas[0].fechada is True


def test_recarga_buscar_por_sequencia_carrega_cabecalho_e_itens(conexoes):
    conexoes.programar([
        {"fetchone": (1, 7, date(2026, 10, 20), "",
                      datetime(2026, 10, 20, 12, 0, 0), "rafael")},
        {"fetchall": [(10, 1, "Ana", "123", 50.0, "Refeição", "", "")]},
    ])

    recarga = RecargaRepository().buscar_por_sequencia(7)

    assert recarga.sequencia == 7
    assert recarga.pelo_usuario == "rafael"
    assert len(recarga.itens) == 1
    assert recarga.itens[0].nome == "Ana"


def test_recarga_pesquisar_agrupa_itens_por_recarga(conexoes):
    """A pesquisa carrega os itens de todas as recargas em UMA consulta."""
    conexoes.programar([
        {"fetchall": [
            (1, 7, date(2026, 10, 20), "", None, ""),
            (2, 8, date(2026, 10, 20), "", None, ""),
        ]},
        {"fetchall": [
            (10, 1, "Ana", "123", 50.0, "Refeição", "", ""),
            (11, 2, "Bruno", "456", 30.0, "Refeição", "", ""),
        ]},
    ])

    recargas = RecargaRepository().pesquisar("")

    assert len(recargas) == 2
    assert recargas[0].itens[0].nome == "Ana"
    assert recargas[1].itens[0].nome == "Bruno"
    conn = conexoes.criadas[0]
    assert len(conn.consultas) == 2   # sem N+1
    assert conn.fechada is True


# ---------------- abastecimento_repository ----------------

def test_abastecimento_salvar_grava_cabecalho_e_itens(conexoes):
    from app.models.abastecimento import AbastecimentoItem

    conexoes.programar([
        {"fetchone": (1, 5, datetime(2026, 10, 20, 12, 0, 0))},
        {"fetchone": (30,)},
    ])
    abastecimento = _abastecimento(itens=[
        AbastecimentoItem(caminhao_codigo="C1", destino="Centro",
                          km_inicio=100, km_final=200, litros=150.0),
    ])

    gravado = AbastecimentoRepository().salvar(abastecimento)

    assert gravado.id == 1
    assert gravado.sequencia == 5
    assert conexoes.criadas[0].commits == 1
    assert conexoes.criadas[0].fechada is True


def test_abastecimento_atualizar_levanta_conflito(conexoes):
    conexoes.programar([
        {"fetchone": None},              # UPDATE não casou
        {"fetchone": (1,)},              # SELECT 1: existe
    ])

    with pytest.raises(ConflitoEdicaoError):
        AbastecimentoRepository().atualizar(_abastecimento())

    assert conexoes.criadas[0].rollbacks == 1
    assert conexoes.criadas[0].fechada is True


def test_abastecimento_excluir_retorna_false_quando_nao_existe(conexoes):
    conexoes.programar([{"rowcount": 0}])

    assert AbastecimentoRepository().excluir(5) is False
    assert conexoes.criadas[0].fechada is True
