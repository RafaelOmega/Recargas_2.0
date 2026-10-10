# -*- coding: utf-8 -*-
"""Service de colaboradores: regras de negócio + acesso a dados.

Os controllers chamam estes métodos passando/recebendo dicts.
Erros de negócio levantam ValueError com mensagem pronta para o usuário.
O código do colaborador é gerado automaticamente (sequencial) — nunca
digitado pelo usuário.
"""
from sqlalchemy.exc import IntegrityError

from app.models.colaborador import Colaborador
from app.repositories.colaborador_repository import ColaboradorRepository
from app.utils.logger import get_logger

logger = get_logger("colaborador_service")


class ColaboradorService:
    """Operações de CRUD de colaboradores."""

    def __init__(self):
        self._repo = ColaboradorRepository()

    # ---------------- regras de negócio ----------------

    def _validar(self, dados: dict) -> None:
        nome = str(dados.get("nome", "")).strip()
        if not nome:
            raise ValueError("Informe o nome do colaborador.")

    # ---------------- conversão ----------------

    @staticmethod
    def _para_dict(c: Colaborador) -> dict:
        return c.to_dict()

    # ---------------- operações ----------------

    def proximo_codigo(self) -> str:
        """Próximo código sequencial (para exibição no formulário)."""
        return self._repo.proximo_codigo()

    def salvar(self, dados: dict) -> dict:
        """Insere um novo colaborador; o código é gerado automaticamente."""
        self._validar(dados)
        colaborador = Colaborador(
            codigo=self._repo.proximo_codigo(),
            nome=str(dados["nome"]).strip(),
            documento=str(dados.get("documento", "") or "").strip(),
        )
        try:
            gravado = self._repo.inserir(colaborador)
        except IntegrityError as exc:
            # dois usuários salvaram ao mesmo tempo -> mesmo código gerado
            logger.error("Código duplicado ao inserir colaborador: %s", exc)
            raise ValueError(
                "Não foi possível gerar um código livre. "
                "Tente salvar novamente.")
        logger.info("Colaborador salvo: %s", gravado.codigo)
        return self._para_dict(gravado)

    def atualizar(self, dados: dict) -> dict:
        """Atualiza o colaborador carregado (buscado pelo código)."""
        codigo = str(dados.get("codigo", "")).strip()
        existente = self._repo.buscar_por_codigo(codigo)
        if existente is None:
            raise ValueError("Colaborador não encontrado para atualizar.")
        self._validar(dados)
        existente.nome = str(dados["nome"]).strip()
        existente.documento = str(dados.get("documento", "") or "").strip()
        if not self._repo.atualizar(existente):
            raise ValueError("Colaborador não encontrado para atualizar.")
        logger.info("Colaborador atualizado: %s", existente.codigo)
        return self._para_dict(existente)

    def excluir(self, codigo: str) -> bool:
        """Remove o colaborador pelo código."""
        if not self._repo.excluir(str(codigo).strip()):
            raise ValueError("Colaborador não encontrado para excluir.")
        return True

    def buscar_por_codigo(self, codigo: str) -> dict | None:
        """Busca um colaborador pelo código (ou None se não existir)."""
        c = self._repo.buscar_por_codigo(str(codigo).strip())
        return self._para_dict(c) if c is not None else None

    def pesquisar(self, filtro: str = "") -> list[dict]:
        """Busca colaboradores filtrando por código/nome."""
        return [self._para_dict(c) for c in self._repo.pesquisar(filtro)]
