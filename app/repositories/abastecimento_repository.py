# -*- coding: utf-8 -*-
"""Repositório de abastecimentos: acesso a dados (PostgreSQL).

Schema:
  abastecimentos       (id, sequencia, data,
                        atualizado_em, pelo_usuario)
  abastecimentos_itens (id, abastecimento_id, caminhao_codigo,
                        caminhao_modelo, colaborador_codigo,
                        colaborador_nome, destino, km_inicio,
                        km_final, litros)

A sequência visível é automática: vem da SEQUENCE
seq_abastecimentos_sequencia, criada e sincronizada pelo
app.database.schema (concorrente-safe).

Caminhão e colaborador são snapshot POR ITEM. Cabeçalho e itens são
gravados na mesma transação; na edição os itens existentes são
substituídos pelos atuais da tela.

Last-write-wins: o INSERT carimba atualizado_em/pelo_usuario; o
UPDATE só aplica se a versão enviada ainda for a atual no banco —
não casou e o abastecimento existe -> ConflitoEdicaoError; não
existe mais -> False (excluído por outro usuário).

Conexão por operação: cada método abre, usa e fecha a conexão —
queda de rede ou restart do PostgreSQL não deixa o app preso a
uma conexão morta; a próxima operação reconecta sozinha.
"""
from contextlib import contextmanager

from app.database import get_connection
from app.models.abastecimento import Abastecimento, AbastecimentoItem
from app.utils import sessao
from app.utils.erros import ConflitoEdicaoError
from app.utils.logger import get_logger

logger = get_logger("abastecimento_repository")
_PROXIMA_SEQUENCIA = "nextval('seq_abastecimentos_sequencia')"


class AbastecimentoRepository:

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

    def salvar(self, abastecimento: Abastecimento) -> Abastecimento:
        """Insere o abastecimento e seus itens (sequência automática).

        Last-write-wins: o INSERT carimba atualizado_em (agora) e
        pelo_usuario (sessão) e devolve a versão gravada.
        """
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO abastecimentos "
                        "  (sequencia, data, atualizado_em, "
                        "   pelo_usuario) "
                        f"VALUES ({_PROXIMA_SEQUENCIA}, %s, "
                        "         CURRENT_TIMESTAMP, %s) "
                        "RETURNING id, sequencia, atualizado_em",
                        (abastecimento.data, sessao.usuario_atual()),
                    )
                    linha = cur.fetchone()
                    abastecimento.id = linha[0]
                    abastecimento.sequencia = linha[1]
                    abastecimento.atualizado_em = linha[2]
                    self._inserir_itens(cur, abastecimento)
                    logger.info(
                        "Abastecimento inserido: seq %s (%d itens)",
                        abastecimento.sequencia,
                        len(abastecimento.itens))
        return abastecimento

    def atualizar(self, abastecimento: Abastecimento) -> bool:
        """Atualiza o cabeçalho e substitui os itens existentes.

        Last-write-wins: o UPDATE só aplica se a versão enviada
        (abastecimento.atualizado_em) ainda for a atual no banco.
          - Não casou e o abastecimento existe -> ConflitoEdicaoError.
          - Não casou e não existe mais -> False (excluído).
        Cabeçalho e itens continuam na MESMA transação.
        """
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE abastecimentos "
                        "SET data = %s, "
                        "    atualizado_em = CURRENT_TIMESTAMP, "
                        "    pelo_usuario = %s "
                        "WHERE sequencia = %s "
                        "  AND atualizado_em IS NOT DISTINCT FROM %s "
                        "RETURNING id, atualizado_em",
                        (abastecimento.data, sessao.usuario_atual(),
                         abastecimento.sequencia,
                         abastecimento.atualizado_em),
                    )
                    linha = cur.fetchone()
                    if linha is None:
                        cur.execute(
                            "SELECT 1 FROM abastecimentos "
                            "WHERE sequencia = %s",
                            (abastecimento.sequencia,),
                        )
                        if cur.fetchone() is None:
                            return False
                        raise ConflitoEdicaoError(
                            f"Abastecimento {abastecimento.sequencia} "
                            "alterado por outro usuário.")
                    abastecimento.id = linha[0]
                    abastecimento.atualizado_em = linha[1]
                    cur.execute(
                        "DELETE FROM abastecimentos_itens "
                        "WHERE abastecimento_id = %s",
                        (abastecimento.id,),
                    )
                    self._inserir_itens(cur, abastecimento)
                    logger.info(
                        "Abastecimento atualizado: seq %s (%d itens)",
                        abastecimento.sequencia,
                        len(abastecimento.itens))
        return True

    def excluir(self, sequencia: int) -> bool:
        """Exclui o abastecimento; itens caem por ON DELETE CASCADE."""
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM abastecimentos WHERE sequencia = %s",
                        (sequencia,),
                    )
                    excluido = cur.rowcount > 0
        logger.info("Abastecimento excluído: seq %s (%s)",
                    sequencia, excluido)
        return excluido

    def _inserir_itens(self, cur, abastecimento: Abastecimento) -> None:
        for item in abastecimento.itens:
            cur.execute(
                "INSERT INTO abastecimentos_itens "
                "(abastecimento_id, caminhao_codigo, caminhao_modelo, "
                " colaborador_codigo, colaborador_nome, destino, "
                " km_inicio, km_final, litros) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "RETURNING id",
                (abastecimento.id, item.caminhao_codigo,
                 item.caminhao_modelo, item.colaborador_codigo,
                 item.colaborador_nome, item.destino, item.km_inicio,
                 item.km_final, item.litros),
            )
            item.id = cur.fetchone()[0]
            item.abastecimento_id = abastecimento.id

    # ---------------- leitura ----------------

    def buscar_por_sequencia(self, sequencia: int) -> Abastecimento | None:
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, sequencia, data, atualizado_em, "
                        "       pelo_usuario "
                        "FROM abastecimentos WHERE sequencia = %s",
                        (sequencia,),
                    )
                    cabecalho = cur.fetchone()
                    if cabecalho is None:
                        return None
                    abastecimento = self._linha_para_abastecimento(
                        cabecalho)
                    cur.execute(
                        "SELECT id, abastecimento_id, caminhao_codigo, "
                        "       caminhao_modelo, colaborador_codigo, "
                        "       colaborador_nome, destino, km_inicio, "
                        "       km_final, litros "
                        "FROM abastecimentos_itens "
                        "WHERE abastecimento_id = %s "
                        "ORDER BY id",
                        (abastecimento.id,),
                    )
                    abastecimento.itens = [
                        self._linha_para_item(l) for l in cur.fetchall()
                    ]
        return abastecimento

    def pesquisar(self, filtro: str = "") -> list[Abastecimento]:
        """Pesquisa por sequência/caminhão/colaborador/destino do item.

        Cada abastecimento vem com os itens carregados, para a grade
        da pesquisa exibir os destinos em linha.
        """
        termo = f"%{filtro}%"
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, sequencia, data, atualizado_em,
                               pelo_usuario
                          FROM abastecimentos
                         WHERE CAST(sequencia AS TEXT) ILIKE %s
                            OR EXISTS (
                                SELECT 1 FROM abastecimentos_itens ai
                                 WHERE ai.abastecimento_id =
                                       abastecimentos.id
                                   AND (ai.caminhao_codigo ILIKE %s
                                        OR ai.colaborador_nome ILIKE %s
                                        OR ai.destino ILIKE %s))
                         ORDER BY sequencia
                        """,
                        (termo, termo, termo, termo),
                    )
                    abastecimentos = [
                        a for a in (self._linha_para_abastecimento(l)
                                    for l in cur.fetchall()) if a
                    ]
                    self._carregar_itens(cur, abastecimentos)
        return abastecimentos

    def _carregar_itens(self, cur,
                        abastecimentos: list[Abastecimento]) -> None:
        """Carrega os itens de vários abastecimentos em uma consulta."""
        if not abastecimentos:
            return
        ids = [a.id for a in abastecimentos]
        cur.execute(
            "SELECT id, abastecimento_id, caminhao_codigo, "
            "       caminhao_modelo, colaborador_codigo, "
            "       colaborador_nome, destino, km_inicio, "
            "       km_final, litros "
            "FROM abastecimentos_itens "
            "WHERE abastecimento_id = ANY(%s) "
            "ORDER BY abastecimento_id, id",
            (ids,),
        )
        por_abastecimento = {a.id: a for a in abastecimentos}
        for linha in cur.fetchall():
            abastecimento = por_abastecimento.get(linha[1])
            if abastecimento is None:
                continue
            if abastecimento.itens is None:
                abastecimento.itens = []
            abastecimento.itens.append(self._linha_para_item(linha))

    # ---------------- auxiliares de leitura ----------------

    @staticmethod
    def _linha_para_abastecimento(linha) -> Abastecimento:
        return Abastecimento(
            id=linha[0],
            sequencia=linha[1],
            data=linha[2],
            atualizado_em=linha[3],
            pelo_usuario=linha[4] or "",
        )

    @staticmethod
    def _linha_para_item(linha) -> AbastecimentoItem:
        return AbastecimentoItem(
            id=linha[0],
            abastecimento_id=linha[1],
            caminhao_codigo=linha[2] or "",
            caminhao_modelo=linha[3] or "",
            colaborador_codigo=linha[4] or "",
            colaborador_nome=linha[5] or "",
            destino=linha[6] or "",
            km_inicio=int(linha[7] or 0),
            km_final=int(linha[8] or 0),
            litros=float(linha[9] or 0),
        )
