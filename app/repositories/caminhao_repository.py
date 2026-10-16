# -*- coding: utf-8 -*-
"""Repositório de caminhões: acesso a dados (PostgreSQL).

Schema:
  caminhoes (id, codigo, modelo, placa, ativo)

O código é automático: vem da SEQUENCE seq_caminhoes_codigo
(1, 2, 3, ...), criada e sincronizada pelo app.database.schema.
Concorrente-safe: dois usuários salvando ao mesmo tempo nunca
geram o mesmo código.

Conexão por operação: cada método abre, usa e fecha a conexão —
queda de rede ou restart do PostgreSQL não deixa o app preso a
uma conexão morta; a próxima operação reconecta sozinha.
"""
from contextlib import contextmanager

from app.database import get_connection
from app.models.caminhao import Caminhao
from app.utils.logger import get_logger

logger = get_logger("caminhao_repository")

_COLUNAS = "codigo, modelo, placa, ativo"

_PROXIMO_CODIGO = "nextval('seq_caminhoes_codigo')::TEXT"


class CaminhaoRepository:

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

    def salvar(self, caminhao: Caminhao) -> Caminhao:
        """Insere o caminhão; o código é gerado automaticamente."""
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        INSERT INTO caminhoes ({_COLUNAS})
                        VALUES ({_PROXIMO_CODIGO}, %s, %s, %s)
                        RETURNING id, codigo
                        """,
                        (caminhao.modelo, caminhao.placa, caminhao.ativo),
                    )
                    caminhao.id, caminhao.codigo = cur.fetchone()
        logger.info("Caminhão inserido: %s - %s",
                    caminhao.codigo, caminhao.modelo)
        return caminhao

    def atualizar(self, caminhao: Caminhao) -> bool:
        """Atualiza modelo/placa/ativo pelo código; código nunca muda."""
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE caminhoes "
                        "SET modelo = %s, placa = %s, ativo = %s "
                        "WHERE codigo = %s",
                        (caminhao.modelo, caminhao.placa,
                         caminhao.ativo, caminhao.codigo),
                    )
                    atualizado = cur.rowcount > 0
        logger.info("Caminhão atualizado: %s (%s)",
                    caminhao.codigo, atualizado)
        return atualizado

    def excluir(self, codigo: str) -> bool:
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM caminhoes WHERE codigo = %s", (codigo,))
                    excluido = cur.rowcount > 0
        logger.info("Caminhão excluído: %s (%s)", codigo, excluido)
        return excluido

    # ---------------- leitura ----------------

    def buscar_por_codigo(self, codigo: str) -> Caminhao | None:
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT id, {_COLUNAS}
                          FROM caminhoes
                         WHERE codigo = %s
                        """,
                        (codigo,),
                    )
                    linha = cur.fetchone()
        return self._mapear(linha) if linha else None

    def pesquisar(self, filtro: str = "",
                  ativo: bool | None = None) -> list[Caminhao]:
        """Lista por status; filtro encontra código, modelo ou placa."""
        sql = f"""
            SELECT id, {_COLUNAS}
              FROM caminhoes
             WHERE TRUE
        """
        params: list = []
        if ativo is not None:
            sql += " AND ativo = %s"
            params.append(ativo)
        termo = filtro.strip()
        if termo:
            sql += (" AND (codigo ILIKE %s OR modelo ILIKE %s "
                    "OR placa ILIKE %s)")
            params += [f"%{termo}%"] * 3
        sql += " ORDER BY codigo DESC"
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    linhas = cur.fetchall()
        return [self._mapear(linha) for linha in linhas]

    # ---------------- auxiliares ----------------

    @staticmethod
    def _mapear(linha) -> Caminhao:
        (id_, codigo, modelo, placa, ativo) = linha
        return Caminhao(id=id_, codigo=codigo, modelo=modelo,
                        placa=placa, ativo=ativo)
