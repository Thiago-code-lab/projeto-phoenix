from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf
from PyQt6.QtWidgets import QApplication, QWidget

from phoenix.core.theme_engine import ThemeEngine
from phoenix.utils.constants import THEME_PRESETS

BASE_DIR = Path(__file__).resolve().parents[1]
settings = Dynaconf(settings_files=[str(BASE_DIR / "settings.toml")])


class ThemeManager:
    def __init__(self) -> None:
        self.current_theme = "dark"
        self.engine = ThemeEngine.instance()

    def load_stylesheet(self) -> str:
        return self.engine._build_qss(self.engine.get_current())

    def stylesheet(self) -> str:
        return self.load_stylesheet()

    def apply(self, app: QApplication) -> None:
        self.engine.set_app(app)
        saved = self.engine.load_saved()
        self.current_theme = str(saved.get("name", settings.get("app.theme", "dark")))
        self.engine.apply(saved)

    def toggle(self, app: QApplication) -> str:
        self.engine.set_app(app)
        current = self.engine.get_current()
        name = str(current.get("name", settings.get("app.theme", "dark")))
        next_name = "light" if name == "dark" else "dark"
        preset = dict(THEME_PRESETS.get(next_name, THEME_PRESETS["dark"]))
        preset["name"] = next_name
        self.current_theme = next_name
        self.engine.apply(preset)
        settings.set("app.theme", next_name)
        return self.current_theme


def apply_theme(widget: QWidget) -> None:
    """Reaplica o tema global para dialogs e mensagens dinamicas."""

    app = QApplication.instance()
    if app is None:
        return
    widget.setStyleSheet(app.styleSheet())
