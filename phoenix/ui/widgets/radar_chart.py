from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget


class RadarChartWidget(QWidget):
    """Radar chart simples para 6 dimensoes de score de vida."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._values = [0.0] * 6
        self._factor = 0.0
        self._anim = QPropertyAnimation(self, b"factor", self)
        self._anim.setDuration(800)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_values(self, values: list[float]) -> None:
        self._values = (values + [0.0] * 6)[:6]
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def _get_factor(self) -> float:
        return self._factor

    def _set_factor(self, value: float) -> None:
        self._factor = float(value)
        self.update()

    factor = pyqtProperty(float, fget=_get_factor, fset=_set_factor)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        del event
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor("#141414"))

            cx = self.width() / 2
            cy = self.height() / 2
            radius = min(self.width(), self.height()) * 0.35
            labels = ["Habitos", "Financas", "Foco", "Metas", "Saude", "Diario"]

            painter.setPen(QPen(QColor("#2a2a2a"), 1))
            for level in [0.2, 0.4, 0.6, 0.8, 1.0]:
                points = []
                for i in range(6):
                    angle = (math.pi * 2 / 6) * i - math.pi / 2
                    points.append((cx + math.cos(angle) * radius * level, cy + math.sin(angle) * radius * level))
                for i in range(6):
                    x1, y1 = points[i]
                    x2, y2 = points[(i + 1) % 6]
                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))

            polygon = QPolygonF()
            for i, value in enumerate(self._values):
                angle = (math.pi * 2 / 6) * i - math.pi / 2
                normalized = max(0.0, min(value / 100.0, 1.0)) * self._factor
                polygon.append(
                    QPointF(cx + math.cos(angle) * radius * normalized, cy + math.sin(angle) * radius * normalized)
                )
            painter.setPen(QPen(QColor("#C0392B"), 2))
            painter.setBrush(QColor(192, 57, 43, 90))
            painter.drawPolygon(polygon)

            painter.setPen(QColor("#f0f0f0"))
            for i, label in enumerate(labels):
                angle = (math.pi * 2 / 6) * i - math.pi / 2
                x = cx + math.cos(angle) * (radius + 18)
                y = cy + math.sin(angle) * (radius + 18)
                painter.drawText(int(x - 30), int(y), 60, 20, 0, f"{label} {int(self._values[i])}")
        finally:
            painter.end()


from PyQt6.QtCore import QPointF  # noqa: E402
