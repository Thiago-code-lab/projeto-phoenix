from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QWidget

from phoenix.ui.widgets.card import CardWidget


class SummaryCard(CardWidget):
    def __init__(self, title: str, value: str = "R$ 0,00", subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("summary-card-value")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("summary-card-subtitle")
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.subtitle_label)

    def update_data(self, value: str, subtitle: str) -> None:
        self.value_label.setText(value)
        self.subtitle_label.setText(subtitle)
