# -*- coding: utf-8 -*-
"""Repositório de colaboradores: acesso a dados (PostgreSQL)."""
from app.database import get_connection
from app.models.colaborador import Colaborador
from app.utils.logger import get_logger

logger = get_logger("colaborador_repository")

# Colunas para INSERT/UPDATE (id é auto-gerado pelo banco)
_COLUNAS = "codigo, nome, documento"

# SELECT base
_SELECT_BASE = "SELECT id, codigo, nome, documento FROM colaboradores"


class ColaboradorRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    # ---------------- geração de código ----------------

    def proximo_codigo(self) -> str:
        """Gera o próximo código sequencial (ex.: '00001')."""
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute("SELECT MAX(codigo) FROM colaboradores")
                linha = cur.fetchone()
        maior = linha[0] if linha else None
        try:
            numero = int(maior) if maior else 0
        except (TypeError, ValueError):
            numero = 0
        return f"{numero + 1:05d}"

    # ---------------- operações ----------------

    def inserir(self, colaborador: Colaborador) -> Colaborador:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO colaboradores ({_COLUNAS}) "
                    "VALUES (%s, %s, %s) RETURNING id",
                    (colaborador.codigo, colaborador.nome,
                     colaborador.documento),
                )
                colaborador.id = cur.fetchone()[0]
        logger.info("Colaborador inserido: %s (id=%s)",
                    colaborador.codigo, colaborador.id)
        return colaborador

    def atualizar(self, colaborador: Colaborador) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE colaboradores
                       SET nome = %s, documento = %s
                     WHERE codigo = %s
                    """,
                    (colaborador.nome, colaborador.documento,
                     colaborador.codigo),
                )
                alterou = cur.rowcount > 0
        logger.info("Colaborador atualizado: %s", colaborador.codigo)
        return alterou

    def excluir(self, codigo: str) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM colaboradores WHERE codigo = %s", (codigo,))
                excluiu = cur.rowcount > 0
        logger.info("Colaborador excluído: %s", codigo)
        return excluiu

    def buscar_por_codigo(self, codigo: str) -> Colaborador | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(f"{_SELECT_BASE} WHERE codigo = %s", (codigo,))
                linha = cur.fetchone()
        return self._linha_para_colaborador(linha)

    def pesquisar(self, filtro: str = "") -> list[Colaborador]:
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    {_SELECT_BASE}
                     WHERE codigo ILIKE %s OR nome ILIKE %s
                     ORDER BY codigo
                    """,
                    (termo, termo),
                )
                linhas = cur.fetchall()
        return [c for c in
                (self._linha_para_colaborador(l) for l in linhas) if c]

    @staticmethod
    def _linha_para_colaborador(linha) -> Colaborador | None:
        if not linha:
            return None
        return Colaborador(
            id=linha[0],
            codigo=linha[1],
            nome=linha[2],
            documento=linha[3] or "",
        )
