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
                              documento: str = ""
                              ) -> list[ItemRecargaRelatorio]:
        """Itens de recarga de um colaborador, em ordem cronológica.

        Filtro prioriza o documento (apenas dígitos) quando informado;
        senão, correspondência parcial no nome do item.
        """
        doc = "".join(c for c in (documento or "") if c.isdigit())
        if doc:
            where = ("regexp_replace(ri.documento, '[^0-9]', '', 'g')"
                     " = %s")
            params: tuple = (doc,)
        elif nome:
            where = "ri.nome ILIKE %s"
            params = (f"%{nome}%",)
        else:
            return []
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT r.sequencia, r.data, ri.nome, ri.documento, "
                    "       ri.carga, ri.sem_carga, ri.valor, "
                    "       ri.beneficio "
                    "FROM recargas_itens ri "
                    "JOIN recargas r ON r.id = ri.recarga_id "
                    f"WHERE {where} "
                    "ORDER BY r.data, r.sequencia, ri.nome",
                    params,
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
