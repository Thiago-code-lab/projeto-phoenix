from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QSpacerItem, QSizePolicy, QVBoxLayout, QWidget

from phoenix.ui.widgets.nav_item import NavItem


class Sidebar(QWidget):
    navigate = pyqtSignal(int)

    _ICON_BY_KEY = {
        "dashboard": "dashboard.svg",
        "goals": "goals.svg",
        "habits": "habits.svg",
        "finances": "finances.svg",
        "library": "library.svg",
        "health": "health.svg",
        "journal": "diary.svg",
        "projects": "projects.svg",
        "focus": "focus.svg",
        "notes": "notes.svg",
        "reviews": "reviews.svg",
        "settings": "settings.svg",
    }

    def __init__(self, modules: Iterable[tuple[str, str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._buttons: list[NavItem] = []
        self._keys: list[str] = []
        self._icons_dir = Path(__file__).resolve().parents[1] / "assets" / "icons"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel("Phoenix")
        logo.setObjectName("sidebar-logo")
        layout.addWidget(logo)

        section = QLabel("Navegacao")
        section.setObjectName("sidebar-section")
        layout.addWidget(section)

        for index, (key, label) in enumerate(modules):
            icon_file = self._ICON_BY_KEY.get(key, "dashboard.svg")
            item = NavItem(label, str(self._icons_dir / icon_file), self)
            item.setToolTip(f"{label}  |  Ctrl+{index + 1 if index < 9 else 0}")
            item.clicked.connect(lambda idx=index: self.navigate.emit(idx))
            layout.addWidget(item)
            self._buttons.append(item)
            self._keys.append(key)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        footer = QLabel("Configuracoes")
        footer.setObjectName("sidebar-section")
        layout.addWidget(footer)

        if self._buttons:
            self.set_active(0)

    def set_active(self, index: int) -> None:
        for button_index, button in enumerate(self._buttons):
            button.set_active(button_index == index)

    def module_key(self, index: int) -> str:
        return self._keys[index]
