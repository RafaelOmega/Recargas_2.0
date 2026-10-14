# -*- coding: utf-8 -*-
"""Repositório do relatório de recargas por colaborador (PostgreSQL)."""
from app.database import get_connection
from app.models.relatorio_recarga_colaborador import ItemRecargaRelatorio
from app.utils.logger import get_logger

logger = get_logger("relatorio_recarga_colaborador_repository")


class RelatorioRecargaColaboradorRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    def itens_por_colaborador(self, nome: str = "",
                              documento: str = "",
                              data_inicial=None,
                              data_final=None
                              ) -> list[ItemRecargaRelatorio]:
        """Itens de recarga agrupados por colaborador (relatório).

        Ordem: nome do colaborador (alfabética), depois data e
        sequência — os blocos consecutivos alimentam os subtotais.

        Colaborador: prioriza o documento (apenas dígitos) quando
        informado; senão, correspondência parcial no nome do item;
        sem colaborador informado, traz TODOS. Período opcional
        restringe pela data da recarga (inclusivo nas duas pontas).
        """
        clausulas: list[str] = []
        params: list = []

        doc = "".join(c for c in (documento or "") if c.isdigit())
        if doc:
            clausulas.append(
                "regexp_replace(ri.documento, '[^0-9]', '', 'g') = %s")
            params.append(doc)
        elif nome:
            clausulas.append("ri.nome ILIKE %s")
            params.append(f"%{nome}%")
        # sem documento e sem nome: todos os colaboradores

        if data_inicial is not None:
            clausulas.append("r.data >= %s")
            params.append(data_inicial)
        if data_final is not None:
            clausulas.append("r.data <= %s")
            params.append(data_final)

        where = " AND ".join(clausulas) if clausulas else "TRUE"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT r.sequencia, r.data, ri.nome, ri.documento, "
                    "       ri.carga, ri.sem_carga, ri.valor, "
                    "       ri.beneficio "
                    "FROM recargas_itens ri "
                    "JOIN recargas r ON r.id = ri.recarga_id "
                    f"WHERE {where} "
                    "ORDER BY ri.nome, r.data, r.sequencia",
                    tuple(params),
                )
                registros = [
                    ItemRecargaRelatorio(
                        sequencia=l[0], data=l[1], nome=l[2] or "",
                        documento=l[3] or "", carga=l[4] or "",
                        sem_carga=l[5] or "", valor=float(l[6] or 0),
                        beneficio=l[7] or "",
                    )
                    for l in cur.fetchall()
                ]
        logger.info("Relatório: %s item(s) carregado(s)", len(registros))
        return registros
