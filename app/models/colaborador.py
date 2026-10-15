# -*- coding: utf-8 -*-
"""Modelo de domínio Colaborador."""
from dataclasses import asdict, dataclass


@dataclass
class Colaborador:
    codigo: str
    nome: str
    documento: str = ""
    ativo: bool = True
    id: int | None = None

    @classmethod
    def from_dict(cls, dados: dict) -> "Colaborador":
        """Cria uma instância a partir de um dict vindo do controller."""
        return cls(
            codigo=str(dados.get("codigo", "")).strip(),
            nome=str(dados.get("nome", "")).strip(),
            documento=str(dados.get("documento", "") or "").strip(),
            ativo=bool(dados.get("ativo", True)),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)
