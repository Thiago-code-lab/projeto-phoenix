from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class GanttWidget(QWidget):
    """Renderiza uma visao simples de Gantt para tarefas com datas."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tasks: list[object] = []
        self._view_start = date.today() - timedelta(days=7)
        self._day_width = 12
        self._row_height = 26

    def set_tasks(self, tasks: list[object]) -> None:
        """Atualiza lista de tarefas e repinta o widget."""

        self._tasks = tasks
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        del event
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor("#141414"))

            today_x = (date.today() - self._view_start).days * self._day_width
            painter.setPen(QPen(QColor("#c0392b"), 1))
            painter.drawLine(today_x, 0, today_x, self.height())

            for idx, task in enumerate(self._tasks):
                start = getattr(task, "start_date", None) or getattr(task, "created_at", None)
                due = getattr(task, "due_date", None)
                if start is None or due is None:
                    continue
                start_date = start.date() if hasattr(start, "date") else start
                due_date = due.date() if hasattr(due, "date") else due
                x_start = (start_date - self._view_start).days * self._day_width
                x_end = (due_date - self._view_start).days * self._day_width
                width = max(x_end - x_start, self._day_width)
                y = idx * self._row_height + 20

                priority = getattr(task, "priority", "medium")
                color = {"high": "#c0392b", "medium": "#e67e22", "low": "#3498db"}.get(priority, "#e67e22")
                painter.fillRect(x_start, y, width, 18, QColor(color))

                progress = max(0, min(int(getattr(task, "progress", 0)), 100))
                if progress > 0:
                    painter.fillRect(x_start, y, int(width * (progress / 100.0)), 18, QColor(255, 255, 255, 80))

                painter.setPen(QColor("#f0f0f0"))
                painter.drawText(x_start + 4, y + 14, str(getattr(task, "title", "Task")))
        finally:
            painter.end()

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = 1 if event.angleDelta().y() > 0 else -1
            self._day_width = max(7, min(30, self._day_width + delta))
            self.update()
            event.accept()
            return
        super().wheelEvent(event)
