from __future__ import annotations

from phoenix.core.achievements.catalog import CATALOG


def test_catalog_seed_non_empty() -> None:
    assert len(CATALOG) >= 10


def test_catalog_has_unique_keys() -> None:
    keys = [row["key"] for row in CATALOG]
    assert len(keys) == len(set(keys))
