# -*- coding: utf-8 -*-
"""Service de colaboradores: regras de negócio + acesso a dados.

Os controllers chamam estes métodos passando/recebendo dicts.
Erros de negócio levantam ValueError com mensagem pronta para o usuário.
"""
from app.models.colaborador import Colaborador
from app.repositories.colaborador_repository import ColaboradorRepository
from app.utils.logger import get_logger

logger = get_logger("colaborador_service")


class ColaboradorService:
    """Operações de CRUD de colaboradores."""

    def __init__(self):
        self._repo = ColaboradorRepository()

    # ---------------- regras de negócio ----------------

    def _validar(self, dados: dict, ignorar_id: int | None = None) -> None:
        codigo = str(dados.get("codigo", "")).strip()
        nome = str(dados.get("nome", "")).strip()
        if not codigo:
            raise ValueError("Informe o código do colaborador.")
        if not nome:
            raise ValueError("Informe o nome do colaborador.")

        existente = self._repo.buscar_por_codigo(codigo)
        if existente is not None and existente.id != ignorar_id:
            raise ValueError("Já existe um colaborador com esse código.")

    def _para_dict(self, c: Colaborador) -> dict:
        return {
            "id": c.id,
            "codigo": c.codigo,
            "nome": c.nome,
            "documento": c.documento or "",
        }

    # ---------------- operações ----------------

    def salvar(self, dados: dict) -> dict:
        """Insere um novo colaborador e retorna os dados gravados."""
        self._validar(dados)
        colaborador = Colaborador(
            codigo=str(dados["codigo"]).strip(),
            nome=str(dados["nome"]).strip(),
            documento=str(dados.get("documento", "") or "").strip(),
        )
        self._repo.inserir(colaborador)
        return self._para_dict(colaborador)

    def atualizar(self, dados: dict) -> dict:
        """Atualiza o colaborador existente (localizado pelo código)."""
        codigo = str(dados.get("codigo", "")).strip()
        existente = self._repo.buscar_por_codigo(codigo)
        if existente is None:
            raise ValueError("Colaborador não encontrado para atualizar.")
        self._validar(dados, ignorar_id=existente.id)
        existente.nome = str(dados["nome"]).strip()
        existente.documento = str(dados.get("documento", "") or "").strip()
        self._repo.atualizar(existente)
        return self._para_dict(existente)

    def excluir(self, codigo: str) -> bool:
        """Remove o colaborador pelo código."""
        if not self._repo.excluir(str(codigo).strip()):
            raise ValueError("Colaborador não encontrado para excluir.")
        return True

    def pesquisar(self, filtro: str = "") -> list[dict]:
        """Busca colaboradores filtrando por código/nome."""
        return [self._para_dict(c) for c in self._repo.pesquisar(filtro)]
