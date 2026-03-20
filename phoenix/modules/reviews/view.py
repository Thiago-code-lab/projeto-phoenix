from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QWidget

from phoenix.modules.reviews.controller import ReviewsController
from phoenix.modules.reviews.widgets import LifeRadarChart, ReviewForm, ReviewHistory


class ReviewsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.controller = ReviewsController()
        layout = QHBoxLayout(self)
        areas, _, _ = self.controller.latest_scores()
        self.form = ReviewForm(areas)
        self.radar = LifeRadarChart()
        self.history = ReviewHistory()
        layout.addWidget(self.form)
        layout.addWidget(self.radar, 1)
        layout.addWidget(self.history)
        self.form.save_button.clicked.connect(self._save_review)
        self.refresh()

    def refresh(self) -> None:
        labels, current, previous = self.controller.latest_scores()
        self.radar.update_scores(labels, current, previous)
        self.history.set_reviews(self.controller.list_reviews())

    def _save_review(self) -> None:
        if not self.form.validator.is_valid():
            return
        self.controller.create_review(self.form.payload())
        self.refresh()
