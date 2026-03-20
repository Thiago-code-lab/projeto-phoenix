from __future__ import annotations

import json
from pathlib import Path

_STRINGS: dict[str, str] = {}


def _load() -> None:
    global _STRINGS
    path = Path(__file__).resolve().with_name("pt_BR.json")
    if not path.exists():
        _STRINGS = {}
        return
    _STRINGS = json.loads(path.read_text(encoding="utf-8"))


_load()


def tr(key: str, **kwargs) -> str:
    """Traduz uma chave usando dicionario pt_BR local."""

    template = _STRINGS.get(key, key)
    try:
        return template.format(**kwargs)
    except Exception:
        return template
