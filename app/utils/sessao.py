# -*- coding: utf-8 -*-
"""Sessão do usuário logado (por processo).

O login autenticado no main.py é registrado aqui; os repositories
usam usuario_atual() para carimbar pelo_usuario em INSERT/UPDATE
(last-write-wins). Sem login (ex.: testes), devolve ''.
"""

_usuario = ""


def definir_usuario(login: str) -> None:
    """Registra o login da sessão (chamado pelo main.py após o login)."""
    global _usuario
    _usuario = (login or "").strip()


def usuario_atual() -> str:
    """Login da sessão atual; '' quando não há usuário definido."""
    return _usuario


def limpar() -> None:
    """Limpa a sessão (encerramento/testes)."""
    global _usuario
    _usuario = ""
