# -*- coding: utf-8 -*-
"""Repositório de usuários: acesso a dados (PostgreSQL).

Schema:
  usuarios (id, codigo, nome, documento, login, senha_hash, ativo,
            atualizado_em, pelo_usuario)

O código é automático: vem da SEQUENCE seq_usuarios_codigo
(1, 2, 3, ...), criada e sincronizada pelo app.database.schema.
A senha NUNCA é gravada em texto puro — o service grava o hash
(see app.utils.senha).

Conexão por operação: cada método abre, usa e fecha a conexão —
queda de rede ou restart do PostgreSQL não deixa o app preso a
uma conexão morta; a próxima operação reconecta sozinha.

Last-write-wins: INSERT/UPDATE carimbam atualizado_em/pelo_usuario;
o UPDATE só aplica quando a versão carregada ainda é a atual —
alterada por outro usuário levanta ConflitoEdicaoError.
"""
from contextlib import contextmanager

from app.database import get_connection
from app.models.usuario import Usuario
from app.utils import sessao
from app.utils.erros import ConflitoEdicaoError
from app.utils.logger import get_logger

logger = get_logger("usuario_repository")

_COLUNAS = ("codigo, nome, documento, login, senha_hash, ativo, "
            "atualizado_em, pelo_usuario")
_PROXIMO_CODIGO = "nextval('seq_usuarios_codigo')::TEXT"


class UsuarioRepository:

    def __init__(self, conn=None):
        """conn opcional (injeção em testes); None = conexão por operação."""
        self._conn = conn

    @contextmanager
    def _conexao(self):
        """Conexão da operação: injetada (testes) ou nova (produção)."""
        conn = self._conn if self._conn is not None else get_connection()
        try:
            yield conn
        finally:
            if self._conn is None:
                conn.close()

    # ---------------- escrita ----------------

    def salvar(self, usuario: Usuario) -> Usuario:
        """Insere o usuário; o código é gerado automaticamente."""
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"INSERT INTO usuarios ({_COLUNAS}) "
                        f"VALUES ({_PROXIMO_CODIGO}, %s, %s, %s, %s, %s, "
                        "CURRENT_TIMESTAMP, %s) "
                        "RETURNING id, codigo",
                        (usuario.nome, usuario.documento, usuario.login,
                         usuario.senha_hash, usuario.ativo,
                         sessao.usuario_atual()),
                    )
                    linha = cur.fetchone()
                    usuario.id, usuario.codigo = linha[0], linha[1]
        logger.info("Usuario inserido: %s", usuario.codigo)
        return usuario

    def atualizar(self, usuario: Usuario) -> bool:
        """Atualiza pelo código apenas se a versão carregada for a atual.

        Levanta ConflitoEdicaoError quando o registro foi alterado por
        outro usuário; retorna False quando foi excluído.
        """
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE usuarios "
                        "SET nome = %s, documento = %s, login = %s, "
                        "    senha_hash = %s, ativo = %s, "
                        "    atualizado_em = CURRENT_TIMESTAMP, "
                        "    pelo_usuario = %s "
                        "WHERE codigo = %s "
                        "  AND atualizado_em IS NOT DISTINCT FROM %s",
                        (usuario.nome, usuario.documento, usuario.login,
                         usuario.senha_hash, usuario.ativo,
                         sessao.usuario_atual(), usuario.codigo,
                         usuario.atualizado_em),
                    )
                    atualizado = cur.rowcount > 0
                    if not atualizado:
                        # distingue 'excluído' de 'alterado por outro'
                        cur.execute(
                            "SELECT 1 FROM usuarios WHERE codigo = %s",
                            (usuario.codigo,),
                        )
                        if cur.fetchone() is not None:
                            raise ConflitoEdicaoError(
                                f"Usuário {usuario.codigo} "
                                "alterado por outro usuário.")
        logger.info("Usuario atualizado: %s (%s)",
                    usuario.codigo, atualizado)
        return atualizado

    def excluir(self, codigo: str) -> bool:
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM usuarios WHERE codigo = %s",
                        (codigo,),
                    )
                    excluido = cur.rowcount > 0
        logger.info("Usuario excluído: %s (%s)", codigo, excluido)
        return excluido

    # ---------------- leitura ----------------

    def buscar_por_codigo(self, codigo: str) -> Usuario | None:
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, codigo, nome, documento, login, "
                        "senha_hash, ativo, atualizado_em, pelo_usuario "
                        "FROM usuarios WHERE codigo = %s",
                        (codigo,),
                    )
                    linha = cur.fetchone()
        return self._linha_para_usuario(linha)

    def buscar_por_login(self, login: str) -> Usuario | None:
        """Busca para a tela de login (login normalizado em minúsculas)."""
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, codigo, nome, documento, login, "
                        "senha_hash, ativo, atualizado_em, pelo_usuario "
                        "FROM usuarios WHERE login = %s",
                        ((login or "").strip().lower(),),
                    )
                    linha = cur.fetchone()
        return self._linha_para_usuario(linha)

    def pesquisar(self, filtro: str = "",
                  ativo: bool | None = None) -> list[Usuario]:
        """Pesquisa por código, nome, CPF ou login.

        ativo=True somente ativos; ativo=False somente inativos;
        ativo=None traz todos.
        """
        termo = f"%{filtro}%"
        clausulas = ["(codigo ILIKE %s OR nome ILIKE %s "
                     "OR documento ILIKE %s OR login ILIKE %s)"]
        params: list = [termo, termo, termo, termo]
        if ativo is not None:
            clausulas.append("ativo = %s")
            params.append(ativo)
        with self._conexao() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT id, codigo, nome, documento, login,
                               senha_hash, ativo, atualizado_em,
                               pelo_usuario
                          FROM usuarios
                         WHERE {" AND ".join(clausulas)}
                         ORDER BY codigo
                        """,
                        tuple(params),
                    )
                    linhas = cur.fetchall()
        return [u for u in (self._linha_para_usuario(l)
                            for l in linhas) if u]

    # ---------------- auxiliares de leitura ----------------

    @staticmethod
    def _linha_para_usuario(linha) -> Usuario | None:
        if not linha:
            return None
        return Usuario(
            id=linha[0],
            codigo=linha[1] or "",
            nome=linha[2] or "",
            documento=linha[3] or "",
            login=linha[4] or "",
            senha_hash=linha[5] or "",
            ativo=bool(linha[6]),
            atualizado_em=linha[7],
            pelo_usuario=linha[8] or "",
        )
