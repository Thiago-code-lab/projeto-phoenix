from __future__ import annotations

from typing import Iterable

import qtawesome as qta
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QSpacerItem, QSizePolicy, QVBoxLayout, QWidget


class Sidebar(QWidget):
    navigate = pyqtSignal(int)

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
            button = QPushButton(qta.icon("fa6s.square"), label)
            button.setObjectName("nav-item")
            button.setProperty("active", False)
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
