from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class CircularProgressBar(QWidget):
    def __init__(self, value: int = 0) -> None:
        super().__init__()
        self.value = value
        self.setMinimumSize(120, 120)

    def set_value(self, value: int) -> None:
        self.value = max(0, min(100, value))
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(10, 10, self.width() - 20, self.height() - 20)

        track = QPen(QColor("#334155"), 10)
        painter.setPen(track)
        painter.drawArc(rect, 0, 360 * 16)

        progress = QPen(QColor("#22c55e"), 10)
        painter.setPen(progress)
        painter.drawArc(rect, 90 * 16, int(-self.value / 100 * 360 * 16))

        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.value}%")
