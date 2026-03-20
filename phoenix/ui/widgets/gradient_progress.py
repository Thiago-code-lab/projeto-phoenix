from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath
from PyQt6.QtWidgets import QWidget


class GradientProgressBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = 0
        self._shimmer = -0.2
        self.setMinimumHeight(10)
        self.setMaximumHeight(10)

        self._shimmer_anim = QPropertyAnimation(self, b"shimmerPosition", self)
        self._shimmer_anim.setDuration(1800)
        self._shimmer_anim.setStartValue(-0.2)
        self._shimmer_anim.setEndValue(1.2)
        self._shimmer_anim.setLoopCount(-1)
        self._shimmer_anim.setEasingCurve(QEasingCurve.Type.Linear)
        self._shimmer_anim.start()

    def setValue(self, value: int) -> None:
        self._value = max(0, min(100, value))
        self.update()

    def value(self) -> int:
        return self._value

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        path = QPainterPath()
        path.addRoundedRect(rect, 5, 5)
        painter.fillPath(path, QColor("#1E1E1E"))

        if self._value <= 0:
            return

        progress_width = int(rect.width() * (self._value / 100.0))
        progress_rect = rect.adjusted(0, 0, -(rect.width() - progress_width), 0)
        progress_path = QPainterPath()
        progress_path.addRoundedRect(progress_rect, 5, 5)

        gradient = QLinearGradient(progress_rect.left(), progress_rect.top(), progress_rect.right(), progress_rect.top())
        gradient.setColorAt(0.0, QColor("#C0392B"))
        gradient.setColorAt(0.5, QColor("#E67E22"))
        gradient.setColorAt(1.0, QColor("#F39C12"))
        painter.fillPath(progress_path, gradient)

        shimmer_x = int(progress_rect.left() + progress_rect.width() * self._shimmer)
        shimmer = QLinearGradient(shimmer_x - 20, rect.top(), shimmer_x + 20, rect.top())
        shimmer.setColorAt(0.0, QColor(255, 255, 255, 0))
        shimmer.setColorAt(0.5, QColor(255, 255, 255, 70))
        shimmer.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(progress_rect, shimmer)

    def _set_shimmer(self, value: float) -> None:
        self._shimmer = value
        self.update()

    def _get_shimmer(self) -> float:
        return self._shimmer

    shimmerPosition = pyqtProperty(float, fget=_get_shimmer, fset=_set_shimmer)
