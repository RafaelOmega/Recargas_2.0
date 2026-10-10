# -*- coding: utf-8 -*-
"""Service de colaboradores: regras de negócio.

Os controllers chamam estes métodos passando/recebendo dicts.
Erros de banco (ex.: código duplicado) sobem como exceção do psycopg2
e são traduzidos pelo app.utils.erros.mensagem_erro nos controllers.
O código do colaborador é gerado automaticamente (sequencial) — nunca
digitado pelo usuário.
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

    @staticmethod
    def _validar(dados: dict) -> None:
        nome = str(dados.get("nome", "")).strip()
        if not nome:
            raise ValueError("Informe o nome do colaborador.")

    # ---------------- operações ----------------

    def proximo_codigo(self) -> str:
        """Próximo código sequencial (para exibição no formulário)."""
        return self._repo.proximo_codigo()

    def salvar(self, dados: dict) -> dict:
        """Insere um novo colaborador; o código é gerado automaticamente."""
        self._validar(dados)
        colaborador = Colaborador.from_dict(dados)
        colaborador.codigo = self._repo.proximo_codigo()
        gravado = self._repo.inserir(colaborador)
        logger.info("Colaborador salvo: %s", gravado.codigo)
        return gravado.to_dict()

    def atualizar(self, dados: dict) -> dict:
        """Atualiza o colaborador carregado (buscado pelo código)."""
        codigo = str(dados.get("codigo", "")).strip()
        existente = self._repo.buscar_por_codigo(codigo)
        if existente is None:
            raise ValueError("Colaborador não encontrado para atualizar.")
        self._validar(dados)
        existente.nome = str(dados.get("nome", "")).strip()
        existente.documento = str(dados.get("documento", "") or "").strip()
        if not self._repo.atualizar(existente):
            raise ValueError("Colaborador não encontrado para atualizar.")
        logger.info("Colaborador atualizado: %s", existente.codigo)
        return existente.to_dict()

    def excluir(self, codigo: str) -> bool:
        """Remove o colaborador pelo código."""
        if not self._repo.excluir(str(codigo).strip()):
            raise ValueError("Colaborador não encontrado para excluir.")
        return True

    def buscar_por_codigo(self, codigo: str) -> dict | None:
        """Busca um colaborador pelo código (ou None se não existir)."""
        c = self._repo.buscar_por_codigo(str(codigo).strip())
        return c.to_dict() if c is not None else None

    def pesquisar(self, filtro: str = "") -> list[dict]:
        """Busca colaboradores filtrando por código/nome."""
        return [c.to_dict() for c in self._repo.pesquisar(filtro)]
