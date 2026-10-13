# -*- coding: utf-8 -*-
"""Repositório de colaboradores: acesso a dados (PostgreSQL).

Schema:
  colaboradores (id, codigo, nome, documento)

O código é automático: sequencial numérico gerado no INSERT
(1, 2, 3, ...), ignorando eventuais códigos não numéricos.
"""
from app.database import get_connection
from app.models.colaborador import Colaborador
from app.utils.logger import get_logger

logger = get_logger("colaborador_repository")

_COLUNAS = "codigo, nome, documento"

# próximo código numérico existente + 1 (sem zeros à esquerda)
_PROXIMO_CODIGO = (
    "(SELECT COALESCE(MAX(CAST(codigo AS INTEGER)), 0) + 1 "
    "      FROM colaboradores WHERE codigo ~ '^[0-9]+$')::TEXT"
)


class ColaboradorRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    # ---------------- escrita ----------------

    def salvar(self, colaborador: Colaborador) -> Colaborador:
        """Insere o colaborador; o código é gerado automaticamente."""
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO colaboradores ({_COLUNAS}) "
                    f"VALUES ({_PROXIMO_CODIGO}, %s, %s) "
                    "RETURNING id, codigo",
                    (colaborador.nome, colaborador.documento),
                )
                linha = cur.fetchone()
                colaborador.id, colaborador.codigo = linha[0], linha[1]
        logger.info("Colaborador inserido: %s", colaborador.codigo)
        return colaborador

    def atualizar(self, colaborador: Colaborador) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "UPDATE colaboradores "
                    "SET nome = %s, documento = %s "
                    "WHERE codigo = %s",
                    (colaborador.nome, colaborador.documento,
                     colaborador.codigo),
                )
                atualizado = cur.rowcount > 0
        logger.info("Colaborador atualizado: %s (%s)",
                    colaborador.codigo, atualizado)
        return atualizado

    def excluir(self, codigo: str) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM colaboradores WHERE codigo = %s",
                    (codigo,),
                )
                excluido = cur.rowcount > 0
        logger.info("Colaborador excluído: %s (%s)", codigo, excluido)
        return excluido

    # ---------------- leitura ----------------

    def buscar_por_codigo(self, codigo: str) -> Colaborador | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT id, codigo, nome, documento "
                    "FROM colaboradores WHERE codigo = %s",
                    (codigo,),
                )
                linha = cur.fetchone()
        return self._linha_para_colaborador(linha)

    def pesquisar(self, filtro: str = "") -> list[Colaborador]:
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, codigo, nome, documento
                      FROM colaboradores
                     WHERE codigo ILIKE %s
                        OR nome ILIKE %s
                     ORDER BY codigo
                    """,
                    (termo, termo),
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
        )
