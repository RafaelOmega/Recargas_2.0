# -*- coding: utf-8 -*-
"""Repositório do relatório de abastecimento por caminhão (PostgreSQL)."""
from app.database import get_connection
from app.models.relatorio_abastecimento import ItemAbastecimentoRelatorio
from app.utils.logger import get_logger

logger = get_logger("relatorio_abastecimento_repository")


class RelatorioAbastecimentoRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

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
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT a.sequencia, a.data, ai.caminhao_codigo, "
                    "       ai.caminhao_modelo, COALESCE(c.placa, ''), "
                    "       ai.colaborador_nome, ai.destino, "
                    "       ai.km_inicio, ai.km_final, ai.litros "
                    "FROM abastecimentos_itens ai "
                    "JOIN abastecimentos a ON a.id = ai.abastecimento_id "
                    "LEFT JOIN caminhoes c ON c.codigo = ai.caminhao_codigo "
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
