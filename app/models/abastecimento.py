# -*- coding: utf-8 -*-
"""Modelos de domínio dos abastecimentos (cabeçalho + itens)."""
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class AbastecimentoItem:
    """Item de um abastecimento (um trecho/destino por linha).

    Caminhão e colaborador são SNAPSHOTS do item (código + descrição
    gravados no momento do lançamento) — o histórico não muda se o
    cadastro for renomeado depois.
    """
    id: int | None = None
    abastecimento_id: int | None = None
    caminhao_codigo: str = ""
    caminhao_modelo: str = ""
    colaborador_codigo: str = ""
    colaborador_nome: str = ""
    destino: str = ""
    km_inicio: int = 0
    km_final: int = 0
    litros: float = 0.0

    @classmethod
    def from_dict(cls, dados: dict) -> "AbastecimentoItem":
        return cls(
            id=dados.get("id"),
            abastecimento_id=dados.get("abastecimento_id"),
            caminhao_codigo=dados.get("caminhao_codigo", "") or "",
            caminhao_modelo=dados.get("caminhao_modelo", "") or "",
            colaborador_codigo=dados.get("colaborador_codigo", "") or "",
            colaborador_nome=dados.get("colaborador_nome", "") or "",
            destino=dados.get("destino", "") or "",
            km_inicio=int(dados.get("km_inicio", 0) or 0),
            km_final=int(dados.get("km_final", 0) or 0),
            litros=float(dados.get("litros", 0) or 0),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "abastecimento_id": self.abastecimento_id,
            "caminhao_codigo": self.caminhao_codigo,
            "caminhao_modelo": self.caminhao_modelo,
            "colaborador_codigo": self.colaborador_codigo,
            "colaborador_nome": self.colaborador_nome,
            "destino": self.destino,
            "km_inicio": self.km_inicio,
            "km_final": self.km_final,
            "litros": self.litros,
        }


@dataclass
class Abastecimento:
    """Cabeçalho de um abastecimento (lançamento diário de frota).

    Fica só com sequência e data — caminhão e colaborador vivem nos
    itens (um vínculo por linha).
    """
    id: int | None = None
    sequencia: int | None = None
    data: date = field(default_factory=date.today)
    itens: list[AbastecimentoItem] = field(default_factory=list)
    # last-write-wins: versão do registro (None = nunca atualizado)
    atualizado_em: datetime | None = None
    pelo_usuario: str = ""

    @classmethod
    def from_dict(cls, dados: dict) -> "Abastecimento":
        data = dados.get("data")
        if isinstance(data, str):
            try:
                data = datetime.strptime(data, "%Y-%m-%d").date()
            except ValueError:
                data = datetime.strptime(data, "%d/%m/%Y").date()
        elif data is None:
            data = date.today()
        itens = [AbastecimentoItem.from_dict(i)
                 for i in dados.get("itens", [])]
        return cls(
            id=dados.get("id"),
            sequencia=dados.get("sequencia"),
            data=data,
            itens=itens,
            atualizado_em=dados.get("atualizado_em"),
            pelo_usuario=str(dados.get("pelo_usuario", "") or ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sequencia": self.sequencia,
            "data": self.data,
            "itens": [i.to_dict() for i in self.itens],
            "atualizado_em": self.atualizado_em,
            "pelo_usuario": self.pelo_usuario,
        }
