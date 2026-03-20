from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QTimer, Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AchievementToast(QWidget):
    """Toast para conquistas desbloqueadas com destaque visual.

    Args:
        title: Nome da conquista.
        description: Descricao curta.
        xp: Experiencia concedida.
        rarity: Nivel de raridade.
        parent: Widget pai.
    """

    def __init__(
        self,
        title: str,
        description: str,
        xp: int,
        rarity: str = "common",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(320, 90)

        gradients = {
            "common": "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1e1e1e, stop:1 #252525)",
            "rare": "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0d1f3c, stop:1 #132b4f)",
            "epic": "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1a0d2e, stop:1 #2a1642)",
            "legendary": "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1f1000, stop:1 #402300)",
        }
        borders = {
            "common": "#555555",
            "rare": "#3498db",
            "epic": "#8e44ad",
            "legendary": "#f39c12",
        }

        self.setStyleSheet(
            "background: "
            + gradients.get(rarity, gradients["common"])
            + "; border: 1px solid "
            + borders.get(rarity, borders["common"])
            + "; border-radius: 10px;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 700;")
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 11px;")
        desc_label.setWordWrap(True)
        xp_label = QLabel(f"+{xp} XP")
        xp_label.setStyleSheet("font-size: 12px; color: #E67E22; font-weight: 700;")
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(xp_label)

    def show_bottom_right(self) -> None:
        """Exibe toast no canto inferior direito com animacao."""

        parent = self.parentWidget()
        if parent is not None:
            end = QPoint(parent.width() - self.width() - 24, parent.height() - self.height() - 72)
            start = QPoint(end.x(), end.y() + 24)
            self.move(start)
        self.show()

        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.Type.OutBack)
        anim.setStartValue(self.pos())
        anim.setEndValue(QPoint(self.x(), self.y() - 24))
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

        QTimer.singleShot(5000, self.close)
