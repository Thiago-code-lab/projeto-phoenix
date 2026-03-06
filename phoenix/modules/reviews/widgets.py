from __future__ import annotations

from PyQt6.QtWidgets import QLabel

from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.chart_widget import ChartWidget


class ReviewForm(CardWidget):
    def __init__(self) -> None:
        super().__init__("Review")
        self.layout.addWidget(QLabel("Reflexao semanal, mensal e anual"))


class LifeRadarChart(ChartWidget):
    def update_scores(self, labels: list[str], current: list[float], previous: list[float] | None = None) -> None:
        self.plot_radar(labels, current, previous)


class ReviewHistory(CardWidget):
    def __init__(self) -> None:
        super().__init__("Historico")
        self.layout.addWidget(QLabel("Registros anteriores"))
