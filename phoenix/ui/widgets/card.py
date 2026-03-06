from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget


class CardWidget(QFrame):
    def __init__(self, title: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)
        if title:
            from PyQt6.QtWidgets import QLabel

            label = QLabel(title)
            label.setObjectName("stat-label")
            self.layout.addWidget(label)
