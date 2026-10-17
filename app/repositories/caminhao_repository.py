# -*- coding: utf-8 -*-
"""Repositório de caminhões: acesso a dados (PostgreSQL).

Schema:
  caminhoes (id, codigo, modelo, placa, ativo,
             atualizado_em, pelo_usuario)

O código é automático: vem da SEQUENCE seq_caminhoes_codigo
(1, 2, 3, ...), criada e sincronizada pelo app.database.schema.
Concorrente-safe: dois usuários salvando ao mesmo tempo nunca
recebem o mesmo código (cada INSERT consome um nextval).

Last-write-wins: INSERT/UPDATE carimbam atualizado_em/pelo_usuario;
o UPDATE só aplica quando a versão carregada ainda é a atual —
alterada por outro usuário levanta ConflitoEdicaoError.
"""
from contextlib import contextmanager

from app.database import get_connection
from app.models.caminhao import Caminhao
from app.utils import sessao
from app.utils.erros import ConflitoEdicaoError
from app.utils.logger import get_logger

logger = get_logger("caminhao_repository")

_COLUNAS = "codigo, modelo, placa, ativo, atualizado_em, pelo_usuario"

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
                        f"INSERT INTO caminhoes ({_COLUNAS}) "
                        f"VALUES ({_PROXIMO_CODIGO}, %s, %s, %s, "
                        "CURRENT_TIMESTAMP, %s) "
                        "RETURNING id, codigo",
                        (caminhao.modelo, caminhao.placa, caminhao.ativo,
                         sessao.usuario_atual()),
                    )
                    linha = cur.fetchone()
                    caminhao.id, caminhao.codigo = linha[0], linha[1]
        logger.info("Caminhão inserido: %s - %s",
                    caminhao.codigo, caminhao.modelo)
        return caminhao

    def atualizar(self, caminhao: Caminhao) -> bool:
        """Atualiza modelo/placa/ativo pelo código apenas se a versão
        carregada for a atual; código nunca muda.

        Levanta ConflitoEdicaoError quando o registro foi alterado por
        outro usuário; retorna False quando foi excluído.
        """
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE caminhoes "
                        "SET modelo = %s, placa = %s, ativo = %s, "
                        "    atualizado_em = CURRENT_TIMESTAMP, "
                        "    pelo_usuario = %s "
                        "WHERE codigo = %s "
                        "  AND atualizado_em IS NOT DISTINCT FROM %s",
                        (caminhao.modelo, caminhao.placa, caminhao.ativo,
                         sessao.usuario_atual(), caminhao.codigo,
                         caminhao.atualizado_em),
                    )
                    atualizado = cur.rowcount > 0
                    if not atualizado:
                        # distingue 'excluído' de 'alterado por outro'
                        cur.execute(
                            "SELECT 1 FROM caminhoes WHERE codigo = %s",
                            (caminhao.codigo,),
                        )
                        if cur.fetchone() is not None:
                            raise ConflitoEdicaoError(
                                f"Caminhão {caminhao.codigo} "
                                "alterado por outro usuário.")
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
                        f"SELECT id, {_COLUNAS} "
                        "FROM caminhoes WHERE codigo = %s",
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
        (id_, codigo, modelo, placa, ativo,
         atualizado_em, pelo_usuario) = linha
        return Caminhao(id=id_, codigo=codigo, modelo=modelo,
                        placa=placa, ativo=ativo,
                        atualizado_em=atualizado_em,
                        pelo_usuario=pelo_usuario or "")
