# -*- coding: utf-8 -*-
"""Repositório de colaboradores: acesso a dados (PostgreSQL).

Schema:
  colaboradores (id, codigo, nome, documento, ativo,
                 atualizado_em, pelo_usuario)

O código é automático: vem da SEQUENCE seq_colaboradores_codigo
(1, 2, 3, ...), criada e sincronizada pelo app.database.schema.
Concorrente-safe: dois usuários salvando ao mesmo tempo nunca
recebem o mesmo código (cada INSERT consome um nextval).

Last-write-wins: INSERT/UPDATE carimbam atualizado_em/pelo_usuario;
o UPDATE só aplica quando a versão carregada ainda é a atual —
alterada por outro usuário levanta ConflitoEdicaoError.
"""
from contextlib import contextmanager

from app.database import get_connection
from app.models.colaborador import Colaborador
from app.utils import sessao
from app.utils.erros import ConflitoEdicaoError
from app.utils.logger import get_logger

logger = get_logger("colaborador_repository")

_COLUNAS = "codigo, nome, documento, ativo, atualizado_em, pelo_usuario"

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
                        f"VALUES ({_PROXIMO_CODIGO}, %s, %s, %s, "
                        "CURRENT_TIMESTAMP, %s) "
                        "RETURNING id, codigo",
                        (colaborador.nome, colaborador.documento,
                         colaborador.ativo, sessao.usuario_atual()),
                    )
                    linha = cur.fetchone()
                    colaborador.id, colaborador.codigo = linha[0], linha[1]
        logger.info("Colaborador inserido: %s", colaborador.codigo)
        return colaborador

    def atualizar(self, colaborador: Colaborador) -> bool:
        """Atualiza pelo código apenas se a versão carregada for a atual.

        Levanta ConflitoEdicaoError quando o registro foi alterado por
        outro usuário; retorna False quando foi excluído.
        """
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE colaboradores "
                        "SET nome = %s, documento = %s, ativo = %s, "
                        "    atualizado_em = CURRENT_TIMESTAMP, "
                        "    pelo_usuario = %s "
                        "WHERE codigo = %s "
                        "  AND atualizado_em IS NOT DISTINCT FROM %s",
                        (colaborador.nome, colaborador.documento,
                         colaborador.ativo, sessao.usuario_atual(),
                         colaborador.codigo, colaborador.atualizado_em),
                    )
                    atualizado = cur.rowcount > 0
                    if not atualizado:
                        # distingue 'excluído' de 'alterado por outro'
                        cur.execute(
                            "SELECT 1 FROM colaboradores "
                            "WHERE codigo = %s",
                            (colaborador.codigo,),
                        )
                        if cur.fetchone() is not None:
                            raise ConflitoEdicaoError(
                                f"Colaborador {colaborador.codigo} "
                                "alterado por outro usuário.")
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
                        "SELECT id, codigo, nome, documento, ativo, "
                        "atualizado_em, pelo_usuario "
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
                        SELECT id, codigo, nome, documento, ativo,
                               atualizado_em, pelo_usuario
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
            atualizado_em=linha[5],
            pelo_usuario=linha[6] or "",
        )
