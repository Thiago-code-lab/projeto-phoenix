from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf

from phoenix.core.backup import export_database
from phoenix.core.database import db_operation_class

settings = Dynaconf(settings_files=[str(Path(__file__).resolve().parents[2] / "settings.toml")])


@db_operation_class
class SettingsController:
    def current_theme(self) -> str:
        return settings.get("app.theme", "dark")

    def set_theme(self, theme: str) -> str:
        """Persiste tema global do aplicativo."""

        value = "light" if theme == "light" else "dark"
        settings.set("app.theme", value)
        return value

    def focus_sound_path(self) -> str:
        """Retorna caminho do som customizado do Pomodoro."""

        return str(settings.get("app.focus_sound_path", ""))

    def set_focus_sound_path(self, sound_path: str) -> str:
        """Persiste caminho de arquivo WAV para notificacao de foco."""

        settings.set("app.focus_sound_path", sound_path)
        return sound_path

    def export_backup(self, destination: Path) -> Path:
        return export_database(destination)
