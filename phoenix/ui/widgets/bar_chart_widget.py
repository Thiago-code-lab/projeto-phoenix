from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class BarChartWidget(QWidget):
    """Gráfico semanal de barras com desenho manual em QPainter.

    Args:
        parent: Widget pai opcional.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(150)
        self._days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        self._minutes = [0, 0, 0, 0, 0, 0, 0]
        self._goal_minutes = 120
        self._bar_rects: list[QRect] = []

    def set_data(self, day_minutes: dict[str, int], goal_minutes: int = 120) -> None:
        """Atualiza dados de minutos por dia e meta diária.

        Args:
            day_minutes: Mapa de dia abreviado para minutos focados.
            goal_minutes: Linha de meta em minutos.
        """

        aliases = {
            "mon": 0,
            "seg": 0,
            "tue": 1,
            "ter": 1,
            "wed": 2,
            "qua": 2,
            "thu": 3,
            "qui": 3,
            "fri": 4,
            "sex": 4,
            "sat": 5,
            "sáb": 5,
            "sab": 5,
            "sun": 6,
            "dom": 6,
        }
        self._minutes = [0, 0, 0, 0, 0, 0, 0]
        for key, value in day_minutes.items():
            idx = aliases.get(str(key).strip().lower()[:3])
            if idx is not None:
                self._minutes[idx] += int(value)
        self._goal_minutes = max(1, int(goal_minutes))
        self.update()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        pos = event.position().toPoint()
        for idx, rect in enumerate(self._bar_rects):
            if rect.contains(pos):
                value = self._minutes[idx]
                hours = value // 60
                minutes = value % 60
                self.setToolTip(f"{self._days[idx]}: {hours}h{minutes:02d}m")
                return
        self.setToolTip("")

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        margin_x = 14
        chart_top = 16
        chart_bottom = 110
        chart_h = 80
        total_w = max(1, self.width() - (margin_x * 2))
        slot_w = total_w / 7
        bar_w = int(slot_w * 0.58)

        max_value = max(max(self._minutes), self._goal_minutes, 1)
        self._bar_rects.clear()

        goal_ratio = self._goal_minutes / max_value
        goal_y = int(chart_bottom - chart_h * goal_ratio)
        dashed = QPen(QColor("#333333"), 1, Qt.PenStyle.DashLine)
        painter.setPen(dashed)
        painter.drawLine(margin_x, goal_y, self.width() - margin_x, goal_y)
        painter.setPen(QColor("#555555"))
        painter.drawText(margin_x + 4, goal_y - 4, "meta")

        for idx, day in enumerate(self._days):
            value = self._minutes[idx]
            ratio = value / max_value
            height = max(8 if value > 0 else 4, int(chart_h * ratio))
            x = int(margin_x + idx * slot_w + (slot_w - bar_w) / 2)
            y = chart_bottom - height
            rect = QRect(x, y, bar_w, height)
            self._bar_rects.append(rect)

            if value > 0:
                grad = QLinearGradient(x, y + height, x, y)
                grad.setColorAt(0.0, QColor("#C0392B"))
                grad.setColorAt(1.0, QColor("#E67E22"))
                painter.setBrush(grad)
            else:
                painter.setBrush(QColor("#1E1E1E"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 4, 4)

            painter.setPen(QColor("#555555"))
            painter.drawText(QRect(int(margin_x + idx * slot_w), chart_bottom + 10, int(slot_w), 16), int(Qt.AlignmentFlag.AlignCenter), day)

        painter.end()
