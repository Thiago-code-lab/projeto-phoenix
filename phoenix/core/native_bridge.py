from __future__ import annotations

"""Bridge para extensao Rust com fallback Python puro."""

import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

try:
    from phoenix_native import (  # type: ignore[import-not-found]
        py_calculate_heatmap,
        py_calculate_streak,
        py_fuzzy_search,
        py_longest_streak,
    )

    NATIVE_AVAILABLE = True
    logger.info("phoenix_native Rust extension carregada.")
except ImportError:
    NATIVE_AVAILABLE = False
    logger.warning("phoenix_native nao disponivel, usando fallback Python.")


def calculate_streak(dates: list[str]) -> int:
    """Calcula streak atual em dias consecutivos.

    Args:
        dates: Lista de datas no formato ISO YYYY-MM-DD.

    Returns:
        Quantidade de dias consecutivos ate hoje.
    """

    if NATIVE_AVAILABLE:
        return int(py_calculate_streak(dates))

    if not dates:
        return 0

    valid_dates: list[date] = []
    for ds in set(dates):
        try:
            valid_dates.append(date.fromisoformat(ds))
        except ValueError:
            continue

    if not valid_dates:
        return 0

    unique = sorted(valid_dates, reverse=True)
    streak = 0
    current = date.today()
    for d in unique:
        if d == current:
            streak += 1
            current -= timedelta(days=1)
        elif d < current:
            break
    return streak


def longest_streak(dates: list[str]) -> int:
    """Calcula maior streak historico em dias consecutivos.

    Args:
        dates: Lista de datas no formato ISO YYYY-MM-DD.

    Returns:
        Maior sequencia consecutiva encontrada.
    """

    if NATIVE_AVAILABLE:
        return int(py_longest_streak(dates))

    if not dates:
        return 0

    parsed: list[date] = []
    for ds in set(dates):
        try:
            parsed.append(date.fromisoformat(ds))
        except ValueError:
            continue

    if not parsed:
        return 0

    unique = sorted(parsed)
    best = 1
    cur = 1
    for i in range(1, len(unique)):
        if (unique[i] - unique[i - 1]).days == 1:
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
    return best


def calculate_heatmap(dates: list[str], year: int) -> list[int]:
    """Retorna intensidades diarias (0-4) para um ano.

    Args:
        dates: Lista de datas no formato ISO YYYY-MM-DD.
        year: Ano alvo.

    Returns:
        Lista com ate 366 posicoes representando intensidade por dia.
    """

    if NATIVE_AVAILABLE:
        return list(py_calculate_heatmap(dates, year))

    counts: dict[str, int] = {}
    for ds in dates:
        if ds.startswith(str(year)):
            counts[ds] = counts.get(ds, 0) + 1

    start = date(year, 1, 1)
    result: list[int] = []
    for i in range(366):
        day = start + timedelta(days=i)
        if day.year != year:
            break
        result.append(min(counts.get(day.isoformat(), 0), 4))
    return result


def fuzzy_search(query: str, items: list[str], limit: int = 20) -> list[tuple[int, float]]:
    """Realiza busca fuzzy e retorna pares indice/score.

    Args:
        query: Texto de busca.
        items: Lista de itens candidatos.
        limit: Limite maximo de retornos.

    Returns:
        Lista ordenada por score decrescente no formato (indice, score).
    """

    if NATIVE_AVAILABLE:
        return list(py_fuzzy_search(query, items, limit))

    q = query.lower().strip()
    if not q:
        return [(idx, 1.0) for idx in range(min(len(items), limit))]

    scored: list[tuple[int, float]] = []
    for i, item in enumerate(items):
        s = item.lower()
        if q == s:
            score = 1.0
        elif q in s:
            score = 0.8 + (len(q) / max(len(s), 1)) * 0.2
        else:
            common = len(set(q) & set(s))
            score = common / max(len(set(q + s)), 1)
        if score > 0.2:
            scored.append((i, float(score)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]
