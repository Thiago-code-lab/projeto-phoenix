from __future__ import annotations

from PyQt6.QtWidgets import QLabel

from .card import CardWidget


class StatCard(CardWidget):
    def __init__(self, label: str, value: str, delta: str = "") -> None:
        super().__init__()
        self.setObjectName("stat-card")
        self.label_widget = QLabel(label)
        self.value_widget = QLabel(value)
        self.delta_widget = QLabel(delta)
        self.label_widget.setObjectName("stat-label")
        self.value_widget.setObjectName("stat-value")
        self._set_delta_style(delta)
        self.layout.addWidget(self.label_widget)
        self.layout.addWidget(self.value_widget)
        self.layout.addWidget(self.delta_widget)

    def update_values(self, value: str, delta: str = "") -> None:
        self.value_widget.setText(value)
        self.delta_widget.setText(delta)
        self._set_delta_style(delta)

    def _set_delta_style(self, delta: str) -> None:
        if delta.strip().startswith("+"):
            self.delta_widget.setObjectName("stat-delta-positive")
        elif delta.strip().startswith("-"):
            self.delta_widget.setObjectName("stat-delta-negative")
        else:
            self.delta_widget.setObjectName("stat-delta-neutral")
        self.delta_widget.style().unpolish(self.delta_widget)
        self.delta_widget.style().polish(self.delta_widget)
