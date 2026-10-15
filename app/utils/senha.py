# -*- coding: utf-8 -*-
"""Hash e verificação de senhas (PBKDF2-HMAC-SHA256).

Formato armazenado: pbkdf2_sha256$<iterações>$<salt hex>$<hash hex>
Sem dependências externas — hashlib + secrets da biblioteca padrão.
O salt é aleatório por senha: dois usuários com a mesma senha geram
hashes diferentes.
"""
import hashlib
import secrets

_ALGORITMO = "pbkdf2_sha256"
_ITERACOES = 100_000
_TAM_SALT = 16  # bytes


def gerar_hash(senha: str) -> str:
    """Gera o hash armazenável de uma senha em texto puro."""
    salt = secrets.token_bytes(_TAM_SALT)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, _ITERACOES)
    return (f"{_ALGORITMO}${_ITERACOES}${salt.hex()}$"
            f"{hash_bytes.hex()}")


def verificar_senha(senha: str, armazenado: str) -> bool:
    """Confere uma senha em texto puro contra o hash armazenado."""
    try:
        algoritmo, iteracoes, salt_hex, hash_hex = armazenado.split("$")
        if algoritmo != _ALGORITMO:
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"),
            bytes.fromhex(salt_hex), int(iteracoes))
        return secrets.compare_digest(calculado.hex(), hash_hex)
    except (ValueError, AttributeError, TypeError):
        return False
