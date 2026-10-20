# -*- coding: utf-8 -*-
"""Repositório do relatório de abastecimento por caminhão (PostgreSQL).

Conexão por operação: cada consulta abre, usa e fecha a conexão —
mesmo padrão dos demais repositories. Queda de rede ou restart do
PostgreSQL não deixa o app preso a uma conexão morta; a próxima
consulta reconecta sozinha.

CORRIGIDO em 2.8.2: o construtor abria a conexão
(self._conn = conn or get_connection()) e nunca a fechava — cada
abertura da tela de relatório vazava uma conexão até esgotar o
max_connections do PostgreSQL, derrubando o banco para todos. Além
disso, se a conexão morresse, o service ficava preso a ela para
sempre. Agora a conexão é obtida dentro do método e fechada no
finally; `conn` injetado (testes) continua sendo usado e NÃO é
fechado pelo repositório.
"""
from contextlib import contextmanager

from app.database import get_connection
from app.models.relatorio_abastecimento import ItemAbastecimentoRelatorio
from app.utils.logger import get_logger

logger = get_logger("relatorio_abastecimento_repository")


class RelatorioAbastecimentoRepository:

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

    def itens_por_caminhao(self, caminhao: str = "",
                           data_inicial=None,
                           data_final=None
                           ) -> list[ItemAbastecimentoRelatorio]:
        """Itens de abastecimento agrupados por caminhão (relatório).

        Ordem: código do caminhão (alfabética), depois data e
        sequência — os blocos consecutivos alimentam os subtotais.

        Caminhão: correspondência parcial no código, modelo ou placa;
        sem caminhão informado, traz TODOS. Período opcional restringe
        pela data do abastecimento (inclusivo nas duas pontas).

        Todos os filtros vão como PARÂMETRO (%s) — a entrada do
        usuário nunca é interpolada no SQL.
        """
        clausulas: list[str] = []
        params: list = []

        termo = (caminhao or "").strip()
        if termo:
            clausulas.append(
                "(ai.caminhao_codigo ILIKE %s "
                "OR ai.caminhao_modelo ILIKE %s "
                "OR COALESCE(c.placa, '') ILIKE %s)")
            params.extend([f"%{termo}%"] * 3)
        if data_inicial is not None:
            clausulas.append("a.data >= %s")
            params.append(data_inicial)
        if data_final is not None:
            clausulas.append("a.data <= %s")
            params.append(data_final)

        where = " AND ".join(clausulas) if clausulas else "TRUE"
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT a.sequencia, a.data, ai.caminhao_codigo, "
                        "       ai.caminhao_modelo, COALESCE(c.placa, ''), "
                        "       ai.colaborador_nome, ai.destino, "
                        "       ai.km_inicio, ai.km_final, ai.litros "
                        "FROM abastecimentos_itens ai "
                        "JOIN abastecimentos a "
                        "     ON a.id = ai.abastecimento_id "
                        "LEFT JOIN caminhoes c "
                        "       ON c.codigo = ai.caminhao_codigo "
                        f"WHERE {where} "
                        "ORDER BY ai.caminhao_codigo, a.data, a.sequencia",
                        tuple(params),
                    )
                    registros = [
                        ItemAbastecimentoRelatorio(
                            sequencia=l[0], data=l[1],
                            caminhao_codigo=l[2] or "",
                            caminhao_modelo=l[3] or "",
                            placa=l[4] or "",
                            colaborador_nome=l[5] or "",
                            destino=l[6] or "",
                            km_inicio=l[7] or 0,
                            km_final=l[8] or 0,
                            litros=float(l[9] or 0),
                        )
                        for l in cur.fetchall()
                    ]
        logger.info("Relatório abastecimento: %s item(ns)", len(registros))
        return registros
