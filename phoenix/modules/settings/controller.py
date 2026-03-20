from __future__ import annotations

from pathlib import Path
from typing import Any

from dynaconf import Dynaconf

from phoenix.core.backup import export_database
from phoenix.core.database import db_operation_class
from phoenix.core.theme_engine import ThemeEngine
from phoenix.utils.constants import DEFAULT_THEME, THEME_PRESETS

settings = Dynaconf(settings_files=[str(Path(__file__).resolve().parents[2] / "settings.toml")])


@db_operation_class
class SettingsController:
    def current_theme(self) -> str:
        theme = self.get_theme()
        return str(theme.get("name", settings.get("app.theme", "dark")))

    def available_presets(self) -> list[str]:
        return sorted(THEME_PRESETS.keys())

    def get_theme(self) -> dict[str, Any]:
        current = ThemeEngine.instance().get_current()
        if current:
            return current
        return ThemeEngine.instance().load_saved()

    def apply_preset(self, name: str) -> dict[str, Any]:
        normalized = "light" if name == "light" else "dark"
        payload = dict(THEME_PRESETS.get(normalized, DEFAULT_THEME))
        payload["name"] = normalized
        ThemeEngine.instance().apply(payload)
        settings.set("app.theme", normalized)
        return payload

    def apply_custom_theme(self, theme: dict[str, Any]) -> dict[str, Any]:
        payload = dict(self.get_theme())
        payload.update(theme)
        payload["name"] = str(theme.get("name", "custom"))
        ThemeEngine.instance().apply(payload)
        settings.set("app.theme", payload["name"])
        return payload

    def set_theme(self, theme: str) -> str:
        applied = self.apply_preset(theme)
        return str(applied.get("name", "dark"))

    def focus_sound_path(self) -> str:
        """Retorna caminho do som customizado do Pomodoro."""

        return str(settings.get("app.focus_sound_path", ""))

    def set_focus_sound_path(self, sound_path: str) -> str:
        """Persiste caminho de arquivo WAV para notificacao de foco."""

        settings.set("app.focus_sound_path", sound_path)
        return sound_path

    def export_backup(self, destination: Path) -> Path:
        return export_database(destination)
