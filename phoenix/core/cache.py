from __future__ import annotations

"""Cache simples em memoria para dados reutilizados entre navegacoes."""

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic
from typing import Generic, TypeVar

CacheT = TypeVar("CacheT")


@dataclass(slots=True)
class CacheEntry(Generic[CacheT]):
    """Representa um item armazenado com controle de expiracao."""

    value: CacheT
    expires_at: float | None


class MemoryCache:
    """Cache em memoria com TTL opcional por chave."""

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry[object]] = {}

    def get(self, key: str) -> object | None:
        """Retorna o valor armazenado para uma chave se ainda estiver valido."""

        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at is not None and entry.expires_at < monotonic():
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: object, ttl_seconds: float | None = None) -> None:
        """Armazena uma chave com TTL opcional."""

        expires_at = monotonic() + ttl_seconds if ttl_seconds is not None else None
        self._store[key] = CacheEntry(value=value, expires_at=expires_at)

    def get_or_set(self, key: str, factory: Callable[[], CacheT], ttl_seconds: float | None = None) -> CacheT:
        """Busca uma chave existente ou calcula e armazena seu valor."""

        cached = self.get(key)
        if cached is not None:
            return cached  # type: ignore[return-value]
        value = factory()
        self.set(key, value, ttl_seconds)
        return value

    def invalidate(self, prefix: str | None = None) -> None:
        """Invalida uma chave especifica por prefixo ou todo o cache."""

        if prefix is None:
            self._store.clear()
            return
        keys = [key for key in self._store if key.startswith(prefix)]
        for key in keys:
            self._store.pop(key, None)
