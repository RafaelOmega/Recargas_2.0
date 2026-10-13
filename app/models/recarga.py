# -*- coding: utf-8 -*-
"""Modelos de domínio das recargas (cabeçalho + itens)."""
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class RecargaItem:
    """Item de uma recarga (um colaborador por linha)."""
    id: int | None = None
    recarga_id: int | None = None
    nome: str = ""
    documento: str = ""
    valor: float = 0.0
    beneficio: str = "Refeição"
    carga: str = ""
    sem_carga: str = ""

    @classmethod
    def from_dict(cls, dados: dict) -> "RecargaItem":
        return cls(
            id=dados.get("id"),
            recarga_id=dados.get("recarga_id"),
            nome=dados.get("nome", "") or "",
            documento=dados.get("documento", "") or "",
            valor=float(dados.get("valor", 0) or 0),
            beneficio=dados.get("beneficio", "") or "Refeição",
            carga=dados.get("carga", "") or "",
            sem_carga=dados.get("sem_carga", "") or "",
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recarga_id": self.recarga_id,
            "nome": self.nome,
            "documento": self.documento,
            "valor": self.valor,
            "beneficio": self.beneficio,
            "carga": self.carga,
            "sem_carga": self.sem_carga,
        }


@dataclass
class Recarga:
    """Cabeçalho de uma recarga (lançamento diário)."""
    id: int | None = None
    sequencia: int | None = None
    data: date = field(default_factory=date.today)
    descricao: str = ""
    itens: list[RecargaItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, dados: dict) -> "Recarga":
        data = dados.get("data")
        if isinstance(data, str):
            try:
                data = datetime.strptime(data, "%Y-%m-%d").date()
            except ValueError:
                data = datetime.strptime(data, "%d/%m/%Y").date()
        elif data is None:
            data = date.today()
        itens = [RecargaItem.from_dict(i)
                 for i in dados.get("itens", [])]
        return cls(
            id=dados.get("id"),
            sequencia=dados.get("sequencia"),
            data=data,
            descricao=dados.get("descricao", "") or "",
            itens=itens,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sequencia": self.sequencia,
            "data": self.data,
            "descricao": self.descricao,
            "itens": [i.to_dict() for i in self.itens],
        }
