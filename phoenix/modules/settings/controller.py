from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf

from phoenix.core.backup import export_database

settings = Dynaconf(settings_files=[str(Path(__file__).resolve().parents[2] / "settings.toml")])


class SettingsController:
    def current_theme(self) -> str:
        return settings.get("app.theme", "dark")

    def export_backup(self, destination: Path) -> Path:
        return export_database(destination)
