from __future__ import annotations

from typing import Iterable

import qtawesome as qta
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QSpacerItem, QSizePolicy, QVBoxLayout, QWidget


class Sidebar(QWidget):
    navigate = pyqtSignal(int)

    _ICON_BY_KEY = {
        "dashboard": "fa6s.gauge-high",
        "goals": "fa6s.bullseye",
        "habits": "fa6s.calendar-check",
        "finances": "fa6s.wallet",
        "library": "fa6s.book-open",
        "health": "fa6s.heart-pulse",
        "journal": "fa6s.pen-to-square",
        "projects": "fa6s.kanban",
        "focus": "fa6s.hourglass-half",
        "notes": "fa6s.note-sticky",
        "reviews": "fa6s.chart-line",
        "settings": "fa6s.gear",
    }

    def __init__(self, modules: Iterable[tuple[str, str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._buttons: list[QPushButton] = []
        self._keys: list[str] = []

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
            icon_name = self._ICON_BY_KEY.get(key, "fa6s.square")
            button = QPushButton(self._icon_or_default(icon_name), label)
            button.setObjectName("nav-item")
            button.setProperty("active", False)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(f"{label}  |  Ctrl+{index + 1 if index < 9 else 0}")
            button.clicked.connect(lambda checked=False, idx=index: self.navigate.emit(idx))
            layout.addWidget(button)
            self._buttons.append(button)
            self._keys.append(key)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        footer = QLabel("Configuracoes")
        footer.setObjectName("sidebar-section")
        layout.addWidget(footer)

        if self._buttons:
            self.set_active(0)

    def set_active(self, index: int) -> None:
        for button_index, button in enumerate(self._buttons):
            button.setProperty("active", button_index == index)
            button.style().unpolish(button)
            button.style().polish(button)

    def module_key(self, index: int) -> str:
        return self._keys[index]

    def _icon_or_default(self, name: str):
        try:
            return qta.icon(name)
        except Exception:  # noqa: BLE001
            return qta.icon("fa6s.square")
