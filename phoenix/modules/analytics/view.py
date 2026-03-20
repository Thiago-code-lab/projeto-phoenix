from __future__ import annotations

from datetime import date
from pathlib import Path

from PyQt6.QtWidgets import QComboBox, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from phoenix.core.database import get_session
from phoenix.modules.analytics.controller import AnalyticsController
from phoenix.ui.widgets.metric_card import MetricCard
from phoenix.ui.widgets.radar_chart import RadarChartWidget


class AnalyticsView(QWidget):
    """Tela de analytics com radar e exportacao de relatorio."""

    def __init__(self) -> None:
        super().__init__()
        self.controller = AnalyticsController()

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        self.month = QComboBox()
        self.month.addItems([f"{m:02d}" for m in range(1, 13)])
        self.month.setCurrentText(f"{date.today().month:02d}")
        self.year = QComboBox()
        self.year.addItems([str(y) for y in range(date.today().year - 3, date.today().year + 2)])
        self.year.setCurrentText(str(date.today().year))
        self.refresh_btn = QPushButton("Atualizar")
        self.refresh_btn.setObjectName("btn-secondary")
        self.pdf_btn = QPushButton("Gerar Relatorio de Vida PDF")
        self.pdf_btn.setObjectName("btn-primary")
        header.addWidget(QLabel("Periodo"))
        header.addWidget(self.month)
        header.addWidget(self.year)
        header.addWidget(self.refresh_btn)
        header.addStretch(1)
        header.addWidget(self.pdf_btn)
        root.addLayout(header)

        self.radar = RadarChartWidget()
        self.radar.setMinimumSize(300, 300)
        root.addWidget(self.radar)

        self.score_label = QLabel("Pontuacao de vida: 0/100")
        root.addWidget(self.score_label)

        self.grid = QGridLayout()
        root.addLayout(self.grid)

        self.refresh_btn.clicked.connect(self.refresh)
        self.pdf_btn.clicked.connect(self.export_pdf)
        self.refresh()

    def refresh(self) -> None:
        with get_session() as session:
            scores = self.controller.get_life_score(session)
        values = [scores[k] for k in ["habits", "finances", "focus", "goals", "health", "diary"]]
        self.radar.set_values(values)
        avg = sum(values) / len(values)
        self.score_label.setText(f"Pontuacao de vida: {avg:.0f}/100")

        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        labels = ["habits", "finances", "focus", "goals", "health", "diary"]
        for idx, key in enumerate(labels):
            card = MetricCard(key.capitalize(), f"{scores[key]:.1f}")
            self.grid.addWidget(card, idx // 3, idx % 3)

    def export_pdf(self) -> None:
        month = int(self.month.currentText())
        year = int(self.year.currentText())
        with get_session() as session:
            data = self.controller.get_life_report_data(session, month, year)
        default_name = f"relatorio-vida-{year}-{month:02d}.pdf"
        output, _ = QFileDialog.getSaveFileName(self, "Salvar relatorio", str(Path.home() / default_name), "PDF (*.pdf)")
        if not output:
            return
        self.controller.generate_life_report(data, output)
