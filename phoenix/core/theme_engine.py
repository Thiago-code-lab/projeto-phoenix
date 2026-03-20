from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from phoenix.utils.constants import DEFAULT_THEME


class ThemeEngine(QObject):
    theme_changed = pyqtSignal(dict)

    _instance: "ThemeEngine | None" = None

    @classmethod
    def instance(cls) -> "ThemeEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        self._current: dict[str, Any] = {}
        self._app: QApplication | None = None
        self._base_dir = Path(__file__).resolve().parents[1]
        self._template_path = self._base_dir / "ui" / "styles" / "phoenix_theme_template.qss"
        self._storage_path = self._base_dir / "data" / "theme.json"

    def set_app(self, app: QApplication) -> None:
        self._app = app

    def apply(self, theme: dict[str, Any]) -> None:
        if self._app is None:
            return
        normalized = self._normalized_theme(theme)
        self._current = normalized
        qss = self._build_qss(normalized)
        self._app.setStyleSheet(qss)
        self._apply_font(normalized)
        self.theme_changed.emit(dict(normalized))
        self._save(normalized)

    def _build_qss(self, t: dict[str, Any]) -> str:
        template = self._template_path.read_text(encoding="utf-8")
        rendered = template
        for key, value in t.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def _apply_font(self, t: dict[str, Any]) -> None:
        if self._app is None:
            return
        font = QFont(str(t.get("font_family", "Segoe UI")), int(t.get("font_size", 13)))
        self._app.setFont(font)

    def _save(self, t: dict[str, Any]) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(json.dumps(t, ensure_ascii=True, indent=2), encoding="utf-8")

    def load_saved(self) -> dict[str, Any]:
        if not self._storage_path.exists():
            return self._normalized_theme(dict(DEFAULT_THEME))
        try:
            loaded = json.loads(self._storage_path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                return self._normalized_theme(dict(DEFAULT_THEME))
            return self._normalized_theme(loaded)
        except Exception:  # noqa: BLE001
            return self._normalized_theme(dict(DEFAULT_THEME))

    def get_current(self) -> dict[str, Any]:
        if not self._current:
            self._current = self.load_saved()
        return dict(self._current)

    def _normalized_theme(self, theme: dict[str, Any]) -> dict[str, Any]:
        merged = dict(DEFAULT_THEME)
        merged.update(theme)

        for color_key in (
            "PRIMARY",
            "SECONDARY",
            "ACCENT",
            "BG_ROOT",
            "BG_SURFACE",
            "BG_ELEVATED",
            "BORDER",
            "BORDER_HOVER",
            "TEXT_PRIMARY",
            "TEXT_SECONDARY",
            "TEXT_HINT",
            "SUCCESS",
            "WARNING",
            "ERROR",
        ):
            merged[color_key] = self._normalize_hex(str(merged[color_key]))

        merged["PRIMARY_RGB"] = self._hex_to_rgb(merged["PRIMARY"])
        merged["SECONDARY_RGB"] = self._hex_to_rgb(merged["SECONDARY"])
        merged["ACCENT_RGB"] = self._hex_to_rgb(merged["ACCENT"])
        merged["TEXT_PRIMARY_RGB"] = self._hex_to_rgb(merged["TEXT_PRIMARY"])
        merged["SUCCESS_RGB"] = self._hex_to_rgb(merged["SUCCESS"])
        merged["WARNING_RGB"] = self._hex_to_rgb(merged["WARNING"])
        merged["ERROR_RGB"] = self._hex_to_rgb(merged["ERROR"])

        merged["font_family"] = str(merged.get("font_family", "Segoe UI"))
        merged["font_size"] = int(merged.get("font_size", 13))
        return merged

    def _normalize_hex(self, value: str) -> str:
        candidate = value.strip().upper()
        if not candidate.startswith("#"):
            candidate = f"#{candidate}"
        if len(candidate) == 4:
            candidate = "#" + "".join(ch * 2 for ch in candidate[1:])
        if len(candidate) != 7:
            return "#000000"
        return candidate

    def _hex_to_rgb(self, value: str) -> str:
        cleaned = value.lstrip("#")
        if len(cleaned) != 6:
            return "0,0,0"
        r = int(cleaned[0:2], 16)
        g = int(cleaned[2:4], 16)
        b = int(cleaned[4:6], 16)
        return f"{r},{g},{b}"
