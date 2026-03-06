from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QPushButton, QSlider, QWidget

from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.chart_widget import ChartWidget


class MetricSlider(QWidget):
    changed = pyqtSignal(int)

    def __init__(self, minimum: int, maximum: int, value: int) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(value)
        self.value_label = QLabel(str(value))
        self.slider.valueChanged.connect(self._on_changed)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.value_label)

    def value(self) -> int:
        return self.slider.value()

    def _on_changed(self, value: int) -> None:
        self.value_label.setText(str(value))
        self.changed.emit(value)


class WaterProgress(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._current_ml = 0
        self._target_ml = 2000
        self.setMinimumHeight(110)

    def set_progress(self, current_ml: int, target_ml: int = 2000) -> None:
        self._current_ml = max(current_ml, 0)
        self._target_ml = max(target_ml, 1)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cups = 8
        filled = int((self._current_ml / self._target_ml) * cups)
        cup_width = max((self.width() - 20) // cups, 18)
        for idx in range(cups):
            x_pos = 10 + idx * cup_width
            color = QColor("#38bdf8") if idx < filled else QColor("#334155")
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x_pos, 20, cup_width - 6, 60, 6, 6)
        painter.setPen(QColor("#e2e8f0"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, f"{self._current_ml} ml")


class MoodSelector(QWidget):
    changed = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        labels = ["1", "2", "3", "4", "5"]
        colors = ["#ef4444", "#f97316", "#f59e0b", "#84cc16", "#22c55e"]
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        for idx, (label, color) in enumerate(zip(labels, colors), start=1):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setStyleSheet(f"background-color: {color}; color: #f8fafc; border-radius: 10px; min-width: 28px;")
            self.group.addButton(button, idx)
            layout.addWidget(button)
        self.group.idClicked.connect(self.changed.emit)

    def value(self) -> int:
        checked = self.group.checkedId()
        return checked if checked > 0 else 3


class MetricLogger(CardWidget):
    def __init__(self) -> None:
        super().__init__("Registro")
        self.layout.addWidget(QLabel("Lancamento rapido de peso, sono e agua."))


class BodyMetricChart(ChartWidget):
    pass


class SleepChart(ChartWidget):
    pass


class WaterTracker(CardWidget):
    def __init__(self) -> None:
        super().__init__("Agua")
        self.progress = WaterProgress()
        self.layout.addWidget(self.progress)


class WorkoutLog(CardWidget):
    def __init__(self) -> None:
        super().__init__("Workout")
        self.layout.addWidget(QLabel("Historico de treinos"))
