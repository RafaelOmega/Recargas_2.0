# -*- coding: utf-8 -*-
"""Tradução de erros de banco em mensagens amigáveis.

Centraliza o _mensagem_erro que estava duplicado nos controllers.
A lógica de identificar a exceção fica aqui; cada controller apenas
informa os textos do seu contexto.
"""


class ConflitoEdicaoError(Exception):
    """Registro alterado por outro usuário entre a carga e o salvar.

    Levantada pelos repositories quando o UPDATE não casa a versão
    carregada (atualizado_em) mas o registro ainda existe — o
    last-write-wins detecta a edição concorrente antes de sobrescrever.
    """


def mensagem_erro(exc: Exception, duplicidade: str = "",
                  contexto: str = "", prefixo: str = "") -> str:
    """Mensagem amigável para o usuário a partir da exceção.

    duplicidade: mensagem para código duplicado (UniqueViolation),
      ex.: "Já existe um produto com esse código."
    contexto: detalhe da FK violada (ForeignKeyViolation),
      ex.: "motivo/produto" -> "Registro relacionado não existe (motivo/produto)."
    prefixo: antecede o detalhe técnico no fallback,
      ex.: "Erro ao gerar o relatório".
    """
    nome = type(exc).__name__
    if nome == "UniqueViolation":
        return duplicidade or "Já existe um registro com esse código."
    if nome == "ForeignKeyViolation":
        return ("Registro relacionado não existe "
                f"({contexto})." if contexto else
                "Registro relacionado não existe.")
    if nome == "OperationalError":
        return "Falha de conexão com o banco de dados."
    detalhe = str(exc) or nome
    return f"{prefixo}: {detalhe}" if prefixo else detalhe
