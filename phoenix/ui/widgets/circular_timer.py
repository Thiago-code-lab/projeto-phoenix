from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty
from PyQt6.QtGui import QBrush, QConicalGradient, QColor, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CircularTimerWidget(QWidget):
    """Timer circular com arco gradiente e propriedade progress animável.

    Attributes:
        progress: Progresso restante da sessão entre 0.0 e 1.0.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._progress = 1.0
        self.setFixedSize(220, 220)

        self.time_label = QLabel("25:00", self)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 42px; font-weight: 700; color: #F0F0F0;")

        self.state_label = QLabel("⚡ EM FOCO", self)
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setStyleSheet("font-size: 11px; color: #E67E22; font-weight: 600;")

        overlay = QVBoxLayout(self)
        overlay.setContentsMargins(0, 70, 0, 70)
        overlay.setSpacing(4)
        overlay.addWidget(self.time_label)
        overlay.addWidget(self.state_label)

        self._progress_anim = QPropertyAnimation(self, b"progress", self)
        self._progress_anim.setEasingCurve(QEasingCurve.Type.Linear)

    def set_time_text(self, value: str) -> None:
        """Atualiza o texto central de tempo.

        Args:
            value: Texto no formato mm:ss.
        """

        self.time_label.setText(value)

    def set_state_text(self, value: str) -> None:
        """Atualiza o subtítulo de estado do timer.

        Args:
            value: Estado legível da sessão.
        """

        self.state_label.setText(value)

    def animate_progress(self, duration_ms: int, start: float = 1.0, end: float = 0.0) -> None:
        """Inicia animação linear da propriedade progress.

        Args:
            duration_ms: Duração em milissegundos.
            start: Valor inicial do progresso.
            end: Valor final do progresso.
        """

        self._progress_anim.stop()
        self._progress_anim.setDuration(max(1, duration_ms))
        self._progress_anim.setStartValue(max(0.0, min(1.0, start)))
        self._progress_anim.setEndValue(max(0.0, min(1.0, end)))
        self._progress_anim.start()

    def stop_animation(self) -> None:
        """Interrompe a animação de progresso ativa."""

        self._progress_anim.stop()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(self.width(), self.height()) / 2 - 16

        pen_bg = QPen(QColor("#1E1E1E"), 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2), int(radius * 2))

        gradient = QConicalGradient(center_x, center_y, 90)
        gradient.setColorAt(0.0, QColor("#F39C12"))
        gradient.setColorAt(0.5, QColor("#E67E22"))
        gradient.setColorAt(1.0, QColor("#C0392B"))
        pen_fg = QPen(QBrush(gradient), 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_fg)

        span = -int(360 * self._progress * 16)
        arc_rect = self.rect().adjusted(16, 16, -16, -16)
        painter.drawArc(arc_rect, 90 * 16, span)

        angle_rad = math.radians(90 - 360 * self._progress)
        tip_x = center_x + radius * math.cos(angle_rad)
        tip_y = center_y - radius * math.sin(angle_rad)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(243, 156, 18, 60))
        painter.drawEllipse(int(tip_x - 12), int(tip_y - 12), 24, 24)
        painter.setBrush(QColor("#F39C12"))
        painter.drawEllipse(int(tip_x - 6), int(tip_y - 6), 12, 12)

    def _set_progress(self, value: float) -> None:
        self._progress = max(0.0, min(1.0, float(value)))
        self.update()

    def _get_progress(self) -> float:
        return self._progress

    progress = pyqtProperty(float, fget=_get_progress, fset=_set_progress)
