from __future__ import annotations

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from phoenix.ui.widgets.chart_widget import ChartWidget


class PomodoroTimer(QWidget):
    """Timer circular de pomodoro com emissao de sinal ao concluir sessao."""

    session_completed = pyqtSignal(int, str)

    def __init__(self) -> None:
        super().__init__()
        self.mode = "Foco"
        self.task_name = ""
        self._total_seconds = 25 * 60
        self._remaining_seconds = self._total_seconds
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self.setMinimumSize(280, 280)

    def set_task_name(self, task_name: str) -> None:
        self.task_name = task_name.strip()

    def set_duration_minutes(self, minutes: int, mode: str) -> None:
        self.mode = mode
        self._total_seconds = max(minutes, 1) * 60
        self._remaining_seconds = self._total_seconds
        self.update()

    def start(self) -> None:
        self._timer.start()

    def pause(self) -> None:
        self._timer.stop()

    def reset(self) -> None:
        self._timer.stop()
        self._remaining_seconds = self._total_seconds
        self.update()

    def remaining_text(self) -> str:
        minutes, seconds = divmod(self._remaining_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _tick(self) -> None:
        self._remaining_seconds = max(0, self._remaining_seconds - 1)
        self.update()
        if self._remaining_seconds == 0:
            self.pause()
            self.session_completed.emit(self._total_seconds // 60, self.task_name)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(24, 24, -24, -24)

        painter.setPen(QPen(QColor("#2e2e33"), 10))
        painter.drawEllipse(rect)

        elapsed = self._total_seconds - self._remaining_seconds
        angle = int((elapsed / max(self._total_seconds, 1)) * 360)
        painter.setPen(QPen(QColor("#6366f1"), 10))
        painter.drawArc(rect, 90 * 16, -angle * 16)

        painter.setPen(QColor("#f8fafc"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.remaining_text())
        painter.drawText(self.rect().adjusted(0, 70, 0, 0), Qt.AlignmentFlag.AlignCenter, self.mode)


class SessionsBarChart(ChartWidget):
    def plot_sessions(self, sessions_per_day: dict[str, int]) -> None:
        labels = list(sessions_per_day.keys())
        values = [float(value) for value in sessions_per_day.values()]
        self.plot_bar(labels, values)
