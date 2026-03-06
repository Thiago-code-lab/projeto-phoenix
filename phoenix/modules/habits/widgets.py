from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QMouseEvent, QPainter
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QToolTip, QWidget


HEATMAP_COLORS = [
    (0.0, QColor("#26262b")),
    (0.25, QColor("#1e3a5f")),
    (0.50, QColor("#1d4ed8")),
    (0.75, QColor("#2563eb")),
    (1.00, QColor("#6366f1")),
]


class HeatmapWidget(QWidget):
    def __init__(self, completion_map: dict[date, float] | None = None) -> None:
        super().__init__()
        self._completion_map = completion_map or {}
        self._cells: dict[QRect, date] = {}
        self.setMinimumHeight(170)
        self.setMouseTracking(True)

    def set_completion_map(self, completion_map: dict[date, float]) -> None:
        self._completion_map = completion_map
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._cells.clear()
        size = 12
        gap = 4
        end_date = date.today()
        start_date = end_date - timedelta(days=363)
        current = start_date - timedelta(days=start_date.weekday())
        for week in range(52):
            for weekday in range(7):
                day = current + timedelta(days=week * 7 + weekday)
                rect = QRect(week * (size + gap), weekday * (size + gap), size, size)
                painter.fillRect(rect, self._color_for_ratio(self._completion_map.get(day, 0.0)))
                self._cells[rect] = day

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        cell_date = self._cell_date(event.position().toPoint())
        if cell_date is None:
            return
        ratio = self._completion_map.get(cell_date, 0.0)
        QToolTip.showText(
            event.globalPosition().toPoint(),
            f"{cell_date.strftime('%d/%m/%Y')} | {int(ratio * 100)}% concluido",
            self,
        )

    def _cell_date(self, point: QPoint) -> date | None:
        for rect, cell_date in self._cells.items():
            if rect.contains(point):
                return cell_date
        return None

    def _color_for_ratio(self, ratio: float) -> QColor:
        if ratio <= 0:
            return HEATMAP_COLORS[0][1]
        for threshold, color in HEATMAP_COLORS[1:]:
            if ratio <= threshold:
                return color
        return HEATMAP_COLORS[-1][1]


class HabitRow(QWidget):
    def __init__(
        self,
        habit_id: int,
        name: str,
        streak: int,
        completion_week: int,
        checked: bool,
        on_toggle,
    ) -> None:
        super().__init__()
        self.habit_id = habit_id
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        self.setLayout(row)
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(checked)
        self.checkbox.stateChanged.connect(lambda state: on_toggle(self.habit_id, state == Qt.CheckState.Checked.value))
        row.addWidget(self.checkbox)
        row.addWidget(QLabel(name))
        row.addWidget(StreakBadge(streak))
        row.addWidget(QLabel(f"{completion_week}/7 semana"))
        row.addStretch(1)


class StreakBadge(QLabel):
    def __init__(self, days: int = 0) -> None:
        super().__init__(f"{days} dias consecutivos")
        if days >= 30:
            color = "#10b981"
        elif days >= 7:
            color = "#6366f1"
        elif days >= 1:
            color = "#f59e0b"
        else:
            color = "#64748b"
        self.setStyleSheet(f"padding: 2px 8px; border-radius: 8px; background: {color}; color: #f8fafc;")
