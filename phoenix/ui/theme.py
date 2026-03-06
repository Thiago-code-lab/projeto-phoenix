from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf
from PyQt6.QtWidgets import QApplication

BASE_DIR = Path(__file__).resolve().parents[1]
STYLES_DIR = BASE_DIR / "ui" / "styles"
settings = Dynaconf(settings_files=[str(BASE_DIR / "settings.toml")])


class ThemeManager:
    def __init__(self) -> None:
        self.current_theme = settings.get("app.theme", "dark")

    def load_stylesheet(self) -> str:
        components = (STYLES_DIR / "components.qss").read_text(encoding="utf-8")
        theme_file = STYLES_DIR / ("dark.qss" if self.current_theme == "dark" else "light.qss")
        return theme_file.read_text(encoding="utf-8") + "\n" + components

    def stylesheet(self) -> str:
        return self.load_stylesheet()

    def apply(self, app: QApplication) -> None:
        app.setStyleSheet(self.load_stylesheet())

    def toggle(self, app: QApplication) -> str:
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        settings.set("app.theme", self.current_theme)
        self.apply(app)
        return self.current_theme
