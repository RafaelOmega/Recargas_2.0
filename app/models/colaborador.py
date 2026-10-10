# -*- coding: utf-8 -*-
"""Modelo ORM: colaboradores."""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Colaborador(Base):
    __tablename__ = "colaboradores"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(120))
    documento: Mapped[str] = mapped_column(String(20), default="")
