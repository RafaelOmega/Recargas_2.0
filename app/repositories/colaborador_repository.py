# -*- coding: utf-8 -*-
"""Repositório de colaboradores: acesso a dados (PostgreSQL via SQLAlchemy)."""
from sqlalchemy import func, select

from app.database import get_session
from app.models.colaborador import Colaborador
from app.utils.logger import get_logger

logger = get_logger("colaborador_repository")


class ColaboradorRepository:
    """CRUD de colaboradores. Cada método abre e fecha a própria sessão."""

    def proximo_codigo(self) -> str:
        """Gera o próximo código sequencial (ex.: '00001')."""
        with get_session() as session:
            maior = session.scalar(select(func.max(Colaborador.codigo)))
        try:
            numero = int(maior) if maior else 0
        except (TypeError, ValueError):
            numero = 0
        return f"{numero + 1:05d}"

    def inserir(self, colaborador: Colaborador) -> Colaborador:
        with get_session() as session:
            session.add(colaborador)
            session.commit()
            session.refresh(colaborador)
        logger.info("Colaborador inserido: %s", colaborador.codigo)
        return colaborador

    def atualizar(self, colaborador: Colaborador) -> bool:
        with get_session() as session:
            registro = session.get(Colaborador, colaborador.id)
            if registro is None:
                registro = session.scalar(
                    select(Colaborador).where(
                        Colaborador.codigo == colaborador.codigo))
            if registro is None:
                return False
            registro.codigo = colaborador.codigo
            registro.nome = colaborador.nome
            registro.documento = colaborador.documento
            session.commit()
        logger.info("Colaborador atualizado: %s", colaborador.codigo)
        return True

    def excluir(self, codigo: str) -> bool:
        with get_session() as session:
            registro = session.scalar(
                select(Colaborador).where(Colaborador.codigo == codigo))
            if registro is None:
                return False
            session.delete(registro)
            session.commit()
        logger.info("Colaborador excluído: %s", codigo)
        return True

    def buscar_por_codigo(self, codigo: str) -> Colaborador | None:
        with get_session() as session:
            return session.scalar(
                select(Colaborador).where(Colaborador.codigo == codigo))

    def pesquisar(self, filtro: str = "") -> list[Colaborador]:
        with get_session() as session:
            termo = f"%{filtro}%"
            return list(session.scalars(
                select(Colaborador)
                .where(Colaborador.codigo.ilike(termo)
                       | Colaborador.nome.ilike(termo))
                .order_by(Colaborador.codigo)
            ).all())
