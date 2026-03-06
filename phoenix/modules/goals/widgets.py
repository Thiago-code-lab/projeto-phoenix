from __future__ import annotations

from datetime import date

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget

from phoenix.core.models import GoalMilestone


STATUS_COLORS = {
    "active": "#6366f1",
    "completed": "#10b981",
    "paused": "#f59e0b",
}


class GoalCard(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, goal_id: int, title: str, category: str, status: str, progress_ratio: float, timeline_text: str) -> None:
        super().__init__()
        self.goal_id = goal_id
        self.setObjectName("goal-card")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        header.addWidget(title_label, 1)
        badge = QLabel(status.capitalize())
        badge.setStyleSheet(
            "padding: 2px 8px; border-radius: 8px;"
            f" background-color: {STATUS_COLORS.get(status, '#334155')}; color: #f8fafc;"
        )
        header.addWidget(badge, 0)
        layout.addLayout(header)

        category_label = QLabel(category or "Sem categoria")
        category_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(category_label)

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(int(max(min(progress_ratio, 1.0), 0.0) * 100))
        layout.addWidget(progress)

        timeline = QLabel(timeline_text)
        timeline.setStyleSheet("color: #cbd5e1;")
        layout.addWidget(timeline)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.goal_id)
        super().mousePressEvent(event)


class CircularProgress(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._ratio = 0.0
        self.setMinimumSize(120, 120)

    def set_ratio(self, ratio: float) -> None:
        self._ratio = max(min(ratio, 1.0), 0.0)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 12
        rect = self.rect().adjusted(
            center.x() - radius - self.rect().x(),
            center.y() - radius - self.rect().y(),
            -((self.rect().right() - center.x()) - radius),
            -((self.rect().bottom() - center.y()) - radius),
        )

        painter.setPen(QPen(QColor("#2e2e33"), 10))
        painter.drawEllipse(rect)

        painter.setPen(QPen(QColor("#6366f1"), 10))
        painter.drawArc(rect, 90 * 16, int(-360 * self._ratio * 16))

        painter.setPen(QColor("#f8fafc"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self._ratio * 100)}%")


class MilestoneRow(QFrame):
    toggled = pyqtSignal(int)
    deleted = pyqtSignal(int)

    def __init__(self, milestone: GoalMilestone) -> None:
        super().__init__()
        self.milestone = milestone
        self.setObjectName("milestone-row")

        row = QHBoxLayout(self)
        row.setContentsMargins(8, 4, 8, 4)
        row.setSpacing(8)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(milestone.completed)
        self.checkbox.stateChanged.connect(self._emit_toggle)
        row.addWidget(self.checkbox)

        title = QLabel(milestone.title)
        row.addWidget(title, 1)

        due = milestone.due_date.strftime("%d/%m/%Y") if milestone.due_date else "Sem data"
        row.addWidget(QLabel(due))

        delete_button = QPushButton("Excluir")
        delete_button.setObjectName("btn-secondary")
        delete_button.clicked.connect(lambda: self.deleted.emit(self.milestone.id))
        row.addWidget(delete_button)

    def _emit_toggle(self) -> None:
        self.toggled.emit(self.milestone.id)


def describe_timeline(status: str, target_date: date | None, start_date: date | None) -> str:
    today = date.today()
    if status == "completed" and start_date and target_date:
        delta = (target_date - start_date).days
        return f"Concluida em {max(delta, 0)} dias"
    if target_date is None:
        return "Sem prazo definido"
    remaining = (target_date - today).days
    if remaining < 0:
        return f"Atrasada ha {abs(remaining)} dias"
    return f"Faltam {remaining} dias"
