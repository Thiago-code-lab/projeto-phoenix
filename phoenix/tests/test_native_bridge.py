from __future__ import annotations

from phoenix.core.native_bridge import calculate_heatmap, calculate_streak, fuzzy_search, longest_streak


def test_streak_fallback() -> None:
    assert calculate_streak([]) == 0


def test_heatmap_fallback() -> None:
    result = calculate_heatmap(["2026-01-01", "2026-01-01"], 2026)
    assert isinstance(result, list)
    assert result[0] >= 1


def test_fuzzy_search() -> None:
    rows = fuzzy_search("fin", ["Financas", "Habitos", "Metas"], 5)
    assert rows
    assert rows[0][0] == 0


def test_longest_streak() -> None:
    assert longest_streak(["2026-01-01", "2026-01-02", "2026-01-03"]) >= 3
