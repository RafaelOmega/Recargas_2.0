# -*- coding: utf-8 -*-
"""Modelo de domínio Usuario."""
from dataclasses import asdict, dataclass


@dataclass
class Usuario:
    codigo: str
    nome: str
    documento: str = ""
    login: str = ""
    senha_hash: str = ""
    ativo: bool = True
    id: int | None = None

    @classmethod
    def from_dict(cls, dados: dict) -> "Usuario":
        """Cria uma instância a partir de um dict vindo do controller."""
        return cls(
            codigo=str(dados.get("codigo", "")).strip(),
            nome=str(dados.get("nome", "")).strip(),
            documento=str(dados.get("documento", "") or "").strip(),
            # login normalizado em minúsculas: evita duplicidade
            # "Rafael" x "rafael"
            login=str(dados.get("login", "")).strip().lower(),
            senha_hash=str(dados.get("senha_hash", "") or ""),
            ativo=bool(dados.get("ativo", True)),
            id=dados.get("id"),
        )

    def to_dict(self) -> dict:
        return asdict(self)
