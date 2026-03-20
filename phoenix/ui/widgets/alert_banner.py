from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget


class AlertBanner(QFrame):
    def __init__(self, message: str = "", level: str = "info", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("alert-banner")
        self._level = level
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        self.level_label = QLabel("INFO")
        self.level_label.setObjectName("alert-level")
        self.message_label = QLabel(message)
        self.message_label.setObjectName("alert-message")
        self.message_label.setWordWrap(True)

        self.close_button = QPushButton("Fechar")
        self.close_button.setObjectName("btn-flat")
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.clicked.connect(self.hide)

        layout.addWidget(self.level_label)
        layout.addWidget(self.message_label, 1)
        layout.addWidget(self.close_button)

        self.set_level(level)

    def set_level(self, level: str) -> None:
        normalized = (level or "info").lower()
        if normalized not in {"info", "warning", "error", "success"}:
            normalized = "info"
        self._level = normalized
        self.setProperty("level", normalized)
        self.level_label.setText(normalized.upper())
        self.style().unpolish(self)
        self.style().polish(self)

    def set_message(self, message: str, level: str | None = None) -> None:
        if level is not None:
            self.set_level(level)
        self.message_label.setText(message)
        self.show()
