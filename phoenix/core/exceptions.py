from __future__ import annotations

"""Hierarquia de excecoes da aplicacao Phoenix."""


class PhoenixError(Exception):
    """Erro base da aplicacao.

    Attributes:
        message: Mensagem amigavel de erro.
    """


class DatabaseError(PhoenixError):
    """Erro relacionado a operacoes de banco de dados."""


class ValidationError(PhoenixError):
    """Erro de validacao de entrada de dados."""


class UIError(PhoenixError):
    """Erro relacionado ao fluxo ou estado da interface."""
