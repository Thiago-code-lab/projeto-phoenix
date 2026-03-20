from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget

from phoenix.ui.widgets.hover_card import HoverCard
from phoenix.ui.widgets.sparkline import SparklineWidget


class GradientValueLabel(QLabel):
    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, self.palette().color(self.foregroundRole()))
        gradient.setColorAt(0.5, self.palette().color(self.foregroundRole()).lighter(120))
        gradient.setColorAt(1.0, self.palette().color(self.foregroundRole()))
        pen = QPen(gradient, 1)
        painter.setPen(pen)
        painter.setFont(self.font())
        path = QPainterPath()
        path.addText(0, self.fontMetrics().ascent() + 4, self.font(), self.text())
        painter.drawPath(path)


class MetricCard(HoverCard):
    def __init__(self, title: str, value: str, icon: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.setStyleSheet(
            "QFrame#hover-card {"
            "background: #161616;"
            "border: 1px solid #2A2A2A;"
            "border-radius: 12px;"
            "}"
        )

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        self.icon_label = QLabel(icon or "◉")
        self.icon_label.setStyleSheet("color: #E67E22; font-size: 18px;")
        top.addWidget(self.icon_label, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        top.addStretch(1)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("label-section")

        self.value_label = GradientValueLabel(value)
        self.value_label.setObjectName("label-value")

        self.sparkline = SparklineWidget([2, 3, 2, 4, 5])
        self.sparkline.setFixedSize(80, 40)

        self.content_layout.addLayout(top)
        self.content_layout.addWidget(self.title_label)
        self.content_layout.addWidget(self.value_label)
        self.content_layout.addWidget(self.sparkline, 0, alignment=Qt.AlignmentFlag.AlignRight)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)
        self.value_label.update()

    def set_sparkline(self, values: list[float]) -> None:
        self.sparkline.set_values(values)
