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

    # ---------------- conversão (padrão Produto do Fábrica) ----------------

    @classmethod
    def from_dict(cls, dados: dict) -> "Colaborador":
        """Cria uma instância a partir de um dict vindo do controller."""
        return cls(
            codigo=str(dados.get("codigo", "")).strip(),
            nome=str(dados.get("nome", "")).strip(),
            documento=str(dados.get("documento", "") or "").strip(),
        )

    def to_dict(self) -> dict:
        """Converte para dict pronto para as telas."""
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "documento": self.documento,
        }
