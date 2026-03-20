from __future__ import annotations

import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class SparklineWidget(QWidget):
    def __init__(self, values: list[float] | None = None) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.plot = pg.PlotWidget()
        self.plot.hideAxis("left")
        self.plot.hideAxis("bottom")
        self.plot.setBackground("#161616")
        self.plot.setMenuEnabled(False)
        layout.addWidget(self.plot)
        self.set_values(values or [1, 3, 2, 5, 4])

    def set_values(self, values: list[float]) -> None:
        self.plot.clear()
        self.plot.plot(values, pen=pg.mkPen(color="#E67E22", width=2))
