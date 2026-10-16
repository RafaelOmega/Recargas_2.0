# -*- coding: utf-8 -*-
"""Repositório de colaboradores: acesso a dados (PostgreSQL).

Schema:
  colaboradores (id, codigo, nome, documento, ativo)

O código é automático: vem da SEQUENCE seq_colaboradores_codigo
(1, 2, 3, ...), criada e sincronizada pelo app.database.schema.
Concorrente-safe: dois usuários salvando ao mesmo tempo nunca
geram o mesmo código.

Conexão por operação: cada método abre, usa e fecha a conexão —
queda de rede ou restart do PostgreSQL não deixa o app preso a
uma conexão morta; a próxima operação reconecta sozinha.
"""
from contextlib import contextmanager

from app.database import get_connection
from app.models.colaborador import Colaborador
from app.utils.logger import get_logger

logger = get_logger("colaborador_repository")

_COLUNAS = "codigo, nome, documento, ativo"

_PROXIMO_CODIGO = "nextval('seq_colaboradores_codigo')::TEXT"


class ColaboradorRepository:

    def __init__(self, conn=None):
        """conn opcional (injeção em testes); None = conexão por operação."""
        self._conn = conn

    @contextmanager
    def _conexao(self):
        """Conexão da operação: injetada (testes) ou nova (produção)."""
        conn = self._conn if self._conn is not None else get_connection()
        try:
            yield conn
        finally:
            if self._conn is None:
                conn.close()

    # ---------------- escrita ----------------

    def salvar(self, colaborador: Colaborador) -> Colaborador:
        """Insere o colaborador; o código é gerado automaticamente."""
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"INSERT INTO colaboradores ({_COLUNAS}) "
                        f"VALUES ({_PROXIMO_CODIGO}, %s, %s, %s) "
                        "RETURNING id, codigo",
                        (colaborador.nome, colaborador.documento,
                         colaborador.ativo),
                    )
                    linha = cur.fetchone()
                    colaborador.id, colaborador.codigo = linha[0], linha[1]
        logger.info("Colaborador inserido: %s", colaborador.codigo)
        return colaborador

    def atualizar(self, colaborador: Colaborador) -> bool:
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE colaboradores "
                        "SET nome = %s, documento = %s, ativo = %s "
                        "WHERE codigo = %s",
                        (colaborador.nome, colaborador.documento,
                         colaborador.ativo, colaborador.codigo),
                    )
                    atualizado = cur.rowcount > 0
        logger.info("Colaborador atualizado: %s (%s)",
                    colaborador.codigo, atualizado)
        return atualizado

    def excluir(self, codigo: str) -> bool:
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM colaboradores WHERE codigo = %s",
                        (codigo,),
                    )
                    excluido = cur.rowcount > 0
        logger.info("Colaborador excluído: %s (%s)", codigo, excluido)
        return excluido

    # ---------------- leitura ----------------

    def buscar_por_codigo(self, codigo: str) -> Colaborador | None:
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, codigo, nome, documento, ativo "
                        "FROM colaboradores WHERE codigo = %s",
                        (codigo,),
                    )
                    linha = cur.fetchone()
        return self._linha_para_colaborador(linha)

    def pesquisar(self, filtro: str = "",
                  ativo: bool | None = None) -> list[Colaborador]:
        """Pesquisa por código ou nome.

        ativo=True somente ativos; ativo=False somente inativos;
        ativo=None traz todos.
        """
        termo = f"%{filtro}%"
        clausulas = ["(codigo ILIKE %s OR nome ILIKE %s)"]
        params: list = [termo, termo]
        if ativo is not None:
            clausulas.append("ativo = %s")
            params.append(ativo)
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT id, codigo, nome, documento, ativo
                          FROM colaboradores
                         WHERE {" AND ".join(clausulas)}
                         ORDER BY codigo
                        """,
                        tuple(params),
                    )
                    linhas = cur.fetchall()
        return [c for c in (self._linha_para_colaborador(l)
                            for l in linhas) if c]

    # ---------------- auxiliares de leitura ----------------

    @staticmethod
    def _linha_para_colaborador(linha) -> Colaborador | None:
        if not linha:
            return None
        return Colaborador(
            id=linha[0],
            codigo=linha[1] or "",
            nome=linha[2] or "",
            documento=linha[3] or "",
            ativo=bool(linha[4]),
        )
