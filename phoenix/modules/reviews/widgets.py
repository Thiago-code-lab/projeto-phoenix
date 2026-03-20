from __future__ import annotations

from PyQt6.QtWidgets import QComboBox, QLabel, QListWidget, QPlainTextEdit, QPushButton

from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.chart_widget import ChartWidget
from phoenix.ui.widgets.validated_fields import FormValidator, ValidatedLineEdit, ValidatedSpinBox


class ReviewForm(CardWidget):
    def __init__(self, areas: list[str]) -> None:
        super().__init__("Review")
        self.period_type = QComboBox()
        self.period_type.addItems(["weekly", "monthly", "quarterly", "yearly"])
        self.period_label = ValidatedLineEdit()
        self.period_label.set_required(True)
        self.highlights = QPlainTextEdit()
        self.challenges = QPlainTextEdit()
        self.intentions = QPlainTextEdit()
        self.scores: dict[str, ValidatedSpinBox] = {}

        self.layout.addWidget(QLabel("Periodo"))
        self.layout.addWidget(self.period_type)
        self.layout.addWidget(QLabel("Rotulo (ex: 2026-W10)"))
        self.layout.addWidget(self.period_label)
        self.layout.addWidget(self.period_label.error_label)

        for area in areas:
            score = ValidatedSpinBox()
            score.setDecimals(1)
            score.set_min_max(0, 10)
            score.setValue(6)
            score.setObjectName(f"review_{area}")
            self.scores[area] = score
            self.layout.addWidget(QLabel(area))
            self.layout.addWidget(score)
            self.layout.addWidget(score.error_label)

        self.layout.addWidget(QLabel("Destaques"))
        self.layout.addWidget(self.highlights)
        self.layout.addWidget(QLabel("Desafios"))
        self.layout.addWidget(self.challenges)
        self.layout.addWidget(QLabel("Intencoes"))
        self.layout.addWidget(self.intentions)

        self.save_button = QPushButton("Salvar review")
        self.save_button.setObjectName("btn-primary")
        self.layout.addWidget(self.save_button)

        fields = [self.period_label, *self.scores.values()]
        self.validator = FormValidator(fields, self)
        self.validator.bind_submit_button(self.save_button)
        self.period_label.textChanged.connect(lambda _: self.validator.is_valid())

    def payload(self) -> dict:
        return {
            "period_type": self.period_type.currentText(),
            "period_label": self.period_label.text().strip(),
            "scores": {area: score.value() for area, score in self.scores.items()},
            "highlights": self.highlights.toPlainText().strip(),
            "challenges": self.challenges.toPlainText().strip(),
            "intentions": self.intentions.toPlainText().strip(),
        }


class LifeRadarChart(ChartWidget):
    def update_scores(self, labels: list[str], current: list[float], previous: list[float] | None = None) -> None:
        self.plot_radar(labels, current, previous)


class ReviewHistory(CardWidget):
    def __init__(self) -> None:
        super().__init__("Historico")
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

    def set_reviews(self, reviews: list) -> None:
        self.list_widget.clear()
        for review in reviews:
            label = review.period_label or "Sem periodo"
            self.list_widget.addItem(f"{label} ({review.period_type or '-'})")
