# -*- coding: utf-8 -*-
"""Service de usuários: regras de negócio.

A senha chega em texto puro do controller (campo "senha") e é
convertida em hash aqui — o repository só vê senha_hash. Na edição,
senha vazia significa "manter a senha atual".
"""
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.utils.logger import get_logger
from app.utils.senha import gerar_hash

logger = get_logger("usuario_service")


class UsuarioService:

    def __init__(self):
        self._repo = UsuarioRepository()

    def salvar(self, dados: dict) -> Usuario:
        senha = str(dados.get("senha", "") or "")
        if not senha:
            raise ValueError("Informe a senha do usuário.")
        usuario = Usuario.from_dict(
            {**dados, "senha_hash": gerar_hash(senha)})
        return self._repo.salvar(usuario)

    def atualizar(self, dados: dict) -> bool:
        dados = dict(dados)
        senha = str(dados.get("senha", "") or "")
        if senha:
            dados["senha_hash"] = gerar_hash(senha)
        else:
            # senha vazia na edição: mantém o hash atual
            atual = self._repo.buscar_por_codigo(
                str(dados.get("codigo", "")))
            dados["senha_hash"] = atual.senha_hash if atual else ""
        return self._repo.atualizar(Usuario.from_dict(dados))

    def excluir(self, codigo: str) -> bool:
        return self._repo.excluir(codigo)

    def buscar_por_codigo(self, codigo: str) -> Usuario | None:
        return self._repo.buscar_por_codigo(codigo)

    def buscar_por_login(self, login: str) -> Usuario | None:
        return self._repo.buscar_por_login(login)

    def pesquisar(self, filtro: str = "",
                  ativo: bool | None = None) -> list[Usuario]:
        return self._repo.pesquisar(filtro, ativo=ativo)
