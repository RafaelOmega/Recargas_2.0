# -*- coding: utf-8 -*-
"""Repositório de recargas: acesso a dados (PostgreSQL).

Schema:
  recargas       (id, sequencia, data, descricao,
                  atualizado_em, pelo_usuario)
  recargas_itens (id, recarga_id, nome, documento, valor,
                  beneficio, carga, sem_carga)

A sequência visível é automática: vem da SEQUENCE
seq_recargas_sequencia, criada e sincronizada pelo
app.database.schema (concorrente-safe).

Cabeçalho e itens são gravados na mesma transação; na edição
os itens existentes são substituídos pelos atuais da tela.

Last-write-wins: o INSERT carimba atualizado_em/pelo_usuario; o
UPDATE só aplica se a versão enviada ainda for a atual no banco —
não casou e a recarga existe -> ConflitoEdicaoError; não existe
mais -> False (excluída por outro usuário).

Conexão por operação: cada método abre, usa e fecha a conexão —
queda de rede ou restart do PostgreSQL não deixa o app preso a
uma conexão morta; a próxima operação reconecta sozinha.
"""
from contextlib import contextmanager

from app.database import get_connection
from app.models.recarga import Recarga, RecargaItem
from app.utils import sessao
from app.utils.erros import ConflitoEdicaoError
from app.utils.logger import get_logger

logger = get_logger("recarga_repository")
_PROXIMA_SEQUENCIA = "nextval('seq_recargas_sequencia')"


class RecargaRepository:

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

    def salvar(self, recarga: Recarga) -> Recarga:
        """Insere a recarga e seus itens (sequência automática).

        Last-write-wins: o INSERT carimba atualizado_em (agora) e
        pelo_usuario (sessão) e devolve a versão gravada.
        """
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO recargas "
                        "  (sequencia, data, descricao, "
                        "   atualizado_em, pelo_usuario) "
                        f"VALUES ({_PROXIMA_SEQUENCIA}, %s, %s, "
                        "         CURRENT_TIMESTAMP, %s) "
                        "RETURNING id, sequencia, atualizado_em",
                        (recarga.data, recarga.descricao,
                         sessao.usuario_atual()),
                    )
                    linha = cur.fetchone()
                    recarga.id, recarga.sequencia = linha[0], linha[1]
                    recarga.atualizado_em = linha[2]
                    self._inserir_itens(cur, recarga)
                    logger.info("Recarga inserida: seq %s (%d itens)",
                                recarga.sequencia, len(recarga.itens))
        return recarga

    def atualizar(self, recarga: Recarga) -> bool:
        """Atualiza o cabeçalho e substitui os itens existentes.

        Last-write-wins: o UPDATE só aplica se a versão enviada
        (recarga.atualizado_em) ainda for a atual no banco.
          - Não casou e a recarga existe -> ConflitoEdicaoError.
          - Não casou e a recarga não existe mais -> False (excluída).
        Cabeçalho e itens continuam na MESMA transação.
        """
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE recargas "
                        "SET data = %s, descricao = %s, "
                        "    atualizado_em = CURRENT_TIMESTAMP, "
                        "    pelo_usuario = %s "
                        "WHERE sequencia = %s "
                        "  AND atualizado_em IS NOT DISTINCT FROM %s "
                        "RETURNING id, atualizado_em",
                        (recarga.data, recarga.descricao,
                         sessao.usuario_atual(), recarga.sequencia,
                         recarga.atualizado_em),
                    )
                    linha = cur.fetchone()
                    if linha is None:
                        cur.execute(
                            "SELECT 1 FROM recargas WHERE sequencia = %s",
                            (recarga.sequencia,),
                        )
                        if cur.fetchone() is None:
                            return False
                        raise ConflitoEdicaoError(
                            f"Recarga {recarga.sequencia} alterada por "
                            "outro usuário.")
                    recarga.id, recarga.atualizado_em = linha[0], linha[1]
                    cur.execute(
                        "DELETE FROM recargas_itens WHERE recarga_id = %s",
                        (recarga.id,),
                    )
                    self._inserir_itens(cur, recarga)
                    logger.info("Recarga atualizada: seq %s (%d itens)",
                                recarga.sequencia, len(recarga.itens))
        return True

    def excluir(self, sequencia: int) -> bool:
        """Exclui a recarga; itens caem por ON DELETE CASCADE."""
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM recargas WHERE sequencia = %s",
                        (sequencia,),
                    )
                    excluido = cur.rowcount > 0
        logger.info("Recarga excluída: seq %s (%s)", sequencia, excluido)
        return excluido

    def _inserir_itens(self, cur, recarga: Recarga) -> None:
        for item in recarga.itens:
            cur.execute(
                "INSERT INTO recargas_itens "
                "(recarga_id, nome, documento, valor, beneficio, "
                " carga, sem_carga) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (recarga.id, item.nome, item.documento, item.valor,
                 item.beneficio, item.carga, item.sem_carga),
            )
            item.id, item.recarga_id = cur.fetchone()[0], recarga.id

    # ---------------- leitura ----------------

    def buscar_por_sequencia(self, sequencia: int) -> Recarga | None:
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, sequencia, data, descricao, "
                        "       atualizado_em, pelo_usuario "
                        "FROM recargas WHERE sequencia = %s",
                        (sequencia,),
                    )
                    cabecalho = cur.fetchone()
                    if cabecalho is None:
                        return None
                    recarga = self._linha_para_recarga(cabecalho)
                    cur.execute(
                        "SELECT id, recarga_id, nome, documento, valor, "
                        "       beneficio, carga, sem_carga "
                        "FROM recargas_itens WHERE recarga_id = %s "
                        "ORDER BY id",
                        (recarga.id,),
                    )
                    recarga.itens = [
                        self._linha_para_item(l) for l in cur.fetchall()
                    ]
        return recarga

    def pesquisar(self, filtro: str = "") -> list[Recarga]:
        """Pesquisa por sequência/descrição/nome de item.

        Cada recarga vem com os itens carregados, para a grade da
        pesquisa exibir os itens em linha na coluna Descrição.
        """
        termo = f"%{filtro}%"
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, sequencia, data, descricao,
                               atualizado_em, pelo_usuario
                          FROM recargas
                         WHERE CAST(sequencia AS TEXT) ILIKE %s
                            OR descricao ILIKE %s
                            OR EXISTS (
                                SELECT 1 FROM recargas_itens ri
                                 WHERE ri.recarga_id = recargas.id
                                   AND ri.nome ILIKE %s)
                         ORDER BY sequencia
                        """,
                        (termo, termo, termo),
                    )
                    recargas = [r for r in (self._linha_para_recarga(l)
                                            for l in cur.fetchall()) if r]
                    self._carregar_itens(cur, recargas)
        return recargas

    def _carregar_itens(self, cur, recargas: list[Recarga]) -> None:
        """Carrega os itens de várias recargas em uma única consulta."""
        if not recargas:
            return
        ids = [r.id for r in recargas]
        cur.execute(
            "SELECT id, recarga_id, nome, documento, valor, "
            "       beneficio, carga, sem_carga "
            "FROM recargas_itens WHERE recarga_id = ANY(%s) "
            "ORDER BY recarga_id, id",
            (ids,),
        )
        por_recarga = {r.id: r for r in recargas}
        for linha in cur.fetchall():
            recarga = por_recarga.get(linha[1])
            if recarga is None:
                continue
            if recarga.itens is None:
                recarga.itens = []
            recarga.itens.append(self._linha_para_item(linha))

    # ---------------- auxiliares de leitura ----------------

    @staticmethod
    def _linha_para_recarga(linha) -> Recarga:
        return Recarga(
            id=linha[0],
            sequencia=linha[1],
            data=linha[2],
            descricao=linha[3] or "",
            atualizado_em=linha[4],
            pelo_usuario=linha[5] or "",
        )

    @staticmethod
    def _linha_para_item(linha) -> RecargaItem:
        return RecargaItem(
            id=linha[0],
            recarga_id=linha[1],
            nome=linha[2] or "",
            documento=linha[3] or "",
            valor=float(linha[4] or 0),
            beneficio=linha[5] or "",
            carga=linha[6] or "",
            sem_carga=linha[7] or "",
        )
