from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget


class SectionHeader(QWidget):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.label = QLabel(title.upper())
        self.label.setObjectName("label-section")
        layout.addWidget(self.label)

        self.line = QFrame()
        self.line.setFixedHeight(2)
        self.line.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #C0392B,stop:1 #E67E22); border: none;"
        )
        layout.addWidget(self.line, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
