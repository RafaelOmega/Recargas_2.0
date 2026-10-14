# -*- coding: utf-8 -*-
"""Repositório de saldo da conta Biz: acesso a dados (PostgreSQL).

Schema:
  saldo_conta (id, codigo, data, valor)

O código visível é automático: vem da SEQUENCE
seq_saldo_conta_codigo, criada e sincronizada pelo
app.database.schema (concorrente-safe).
"""
from app.database import get_connection
from app.models.saldo_conta import SaldoConta
from app.utils.logger import get_logger

logger = get_logger("saldo_conta_repository")

_PROXIMO_CODIGO = "nextval('seq_saldo_conta_codigo')"


class SaldoContaRepository:

    def __init__(self, conn=None):
        self._conn = conn or get_connection()

    # ---------------- escrita ----------------

    def salvar(self, saldo: SaldoConta) -> SaldoConta:
        """Insere o lançamento (código automático)."""
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO saldo_conta (codigo, data, valor) "
                    f"VALUES ({_PROXIMO_CODIGO}, %s, %s) "
                    "RETURNING id, codigo",
                    (saldo.data, saldo.valor),
                )
                linha = cur.fetchone()
                saldo.id, saldo.codigo = linha[0], str(linha[1])
        logger.info("Saldo conta inserido: código %s", saldo.codigo)
        return saldo

    def atualizar(self, saldo: SaldoConta) -> bool:
        """Atualiza data e valor pelo código."""
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "UPDATE saldo_conta SET data = %s, valor = %s "
                    "WHERE codigo = %s",
                    (saldo.data, saldo.valor, saldo.codigo),
                )
                atualizado = cur.rowcount > 0
        logger.info("Saldo conta atualizado: código %s (%s)",
                    saldo.codigo, atualizado)
        return atualizado

    def excluir(self, codigo: str) -> bool:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM saldo_conta WHERE codigo = %s",
                    (codigo,),
                )
                excluido = cur.rowcount > 0
        logger.info("Saldo conta excluído: código %s (%s)",
                    codigo, excluido)
        return excluido

    # ---------------- leitura ----------------

    def saldo_atual(self) -> float:
        """Saldo da conta: soma dos saldos - soma das recargas.

        Uma única consulta: diferença entre o total dos lançamentos
        de saldo (cargas na conta) e o total lançado nos itens de
        recarga (consumo).
        """
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT "
                    "(SELECT COALESCE(SUM(valor), 0) "
                    "       FROM saldo_conta) "
                    "- (SELECT COALESCE(SUM(valor), 0) "
                    "       FROM recargas_itens)"
                )
                linha = cur.fetchone()
        saldo = float(linha[0] or 0) if linha else 0.0
        logger.info("Saldo da conta calculado: %s", saldo)
        return saldo

    def buscar_por_codigo(self, codigo: str) -> SaldoConta | None:
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT id, codigo, data, valor "
                    "FROM saldo_conta WHERE codigo = %s",
                    (codigo,),
                )
                linha = cur.fetchone()
        if linha is None:
            return None
        return self._linha_para_saldo(linha)

    def pesquisar(self, filtro: str = "") -> list[SaldoConta]:
        """Pesquisa por código ou data (dd/mm/aaaa ou ISO).

        Ordenação padrão: código DESCENDENTE (mais recente primeiro).
        """
        termo = f"%{filtro}%"
        with self._conn:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, codigo, data, valor
                      FROM saldo_conta
                     WHERE (%s = ''
                            OR codigo ILIKE %s
                            OR TO_CHAR(data, 'DD/MM/YYYY') ILIKE %s
                            OR CAST(data AS TEXT) ILIKE %s)
                     ORDER BY CAST(codigo AS INTEGER) DESC
                    """,
                    (filtro, termo, termo, termo),
                )
                saldos = [self._linha_para_saldo(l)
                          for l in cur.fetchall()]
        logger.info("Pesquisa saldo conta: %s registro(s)", len(saldos))
        return saldos

    # ---------------- auxiliares de leitura ----------------

    @staticmethod
    def _linha_para_saldo(linha) -> SaldoConta:
        return SaldoConta(
            id=linha[0],
            codigo=str(linha[1]),
            data=linha[2],
            valor=float(linha[3] or 0),
        )
