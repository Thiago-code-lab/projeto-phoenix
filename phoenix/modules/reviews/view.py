from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QWidget

from phoenix.modules.reviews.controller import ReviewsController
from phoenix.modules.reviews.widgets import LifeRadarChart, ReviewForm, ReviewHistory


class ReviewsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.controller = ReviewsController()
        layout = QHBoxLayout(self)
        self.form = ReviewForm()
        self.radar = LifeRadarChart()
        self.history = ReviewHistory()
        layout.addWidget(self.form)
        layout.addWidget(self.radar, 1)
        layout.addWidget(self.history)
        self.refresh()

    def refresh(self) -> None:
        labels, current, previous = self.controller.latest_scores()
        self.radar.update_scores(labels, current, previous)
