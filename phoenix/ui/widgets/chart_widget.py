from __future__ import annotations

import math

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class ChartWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.figure = Figure(figsize=(4, 3), facecolor="#18181b")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def plot_bar(self, labels: list[str], values: list[float]) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        self._style_axis(axis)
        axis.bar(labels, values, color="#6366f1")
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_grouped_bar(self, labels: list[str], series: list[tuple[str, list[float], str]]) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        self._style_axis(axis)
        width = 0.8 / max(len(series), 1)
        positions = list(range(len(labels)))
        for series_index, (_, values, color) in enumerate(series):
            shifted = [position + (series_index - (len(series) - 1) / 2) * width for position in positions]
            axis.bar(shifted, values, width=width, color=color)
        axis.set_xticks(positions)
        axis.set_xticklabels(labels)
        axis.legend([name for name, _, _ in series], frameon=False, labelcolor="#a1a1aa")
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_line(self, labels: list[str], values: list[float], color: str = "#6366f1", fill: bool = False) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        self._style_axis(axis)
        axis.plot(labels, values, color=color, linewidth=2)
        if fill:
            axis.fill_between(labels, values, [0 for _ in values], color=color, alpha=0.18)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_pie(self, labels: list[str], values: list[float], colors: list[str] | None = None) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.set_facecolor("#18181b")
        if sum(values) == 0:
            values = [1]
            labels = ["Sem dados"]
            colors = ["#2e2e33"]
        axis.pie(
            values,
            labels=labels,
            colors=colors,
            textprops={"color": "#fafafa", "fontsize": 9},
            wedgeprops={"edgecolor": "#18181b"},
        )
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_radar(
        self,
        labels: list[str],
        primary: list[float],
        secondary: list[float] | None = None,
    ) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111, polar=True)
        axis.set_facecolor("#18181b")
        self.figure.patch.set_facecolor("#18181b")
        angles = [index / float(len(labels)) * 2 * math.pi for index in range(len(labels))]
        angles += angles[:1]
        primary_values = primary + primary[:1]
        axis.set_theta_offset(math.pi / 2)
        axis.set_theta_direction(-1)
        axis.set_thetagrids([math.degrees(angle) for angle in angles[:-1]], labels, color="#a1a1aa", fontsize=9)
        axis.set_rlabel_position(0)
        axis.set_ylim(0, 10)
        axis.tick_params(colors="#71717a")
        axis.grid(color="#3f3f46")
        axis.plot(angles, primary_values, color="#6366f1", linewidth=2)
        axis.fill(angles, primary_values, color="#6366f1", alpha=0.2)
        if secondary is not None:
            secondary_values = secondary + secondary[:1]
            axis.plot(angles, secondary_values, color="#10b981", linewidth=2)
            axis.fill(angles, secondary_values, color="#10b981", alpha=0.12)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _style_axis(self, axis) -> None:
        self.figure.patch.set_facecolor("#18181b")
        axis.set_facecolor("#18181b")
        axis.tick_params(colors="#a1a1aa")
        for spine in axis.spines.values():
            spine.set_color("#2e2e33")
        axis.yaxis.label.set_color("#a1a1aa")
        axis.xaxis.label.set_color("#a1a1aa")
        axis.title.set_color("#fafafa")
        axis.grid(color="#2e2e33", alpha=0.6)
