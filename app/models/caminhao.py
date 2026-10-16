# -*- coding: utf-8 -*-
"""Modelo de domínio Caminhão."""
from dataclasses import asdict, dataclass


@dataclass
class Caminhao:
    codigo: str
    modelo: str
    placa: str = ""
    ativo: bool = True
    id: int | None = None

    @classmethod
    def from_dict(cls, dados: dict) -> "Caminhao":
        """Cria uma instância a partir de um dict vindo do controller."""
        return cls(
            codigo=str(dados.get("codigo", "")).strip(),
            modelo=str(dados.get("modelo", "")).strip(),
            placa=str(dados.get("placa", "") or "").strip(),
            ativo=bool(dados.get("ativo", True)),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)
