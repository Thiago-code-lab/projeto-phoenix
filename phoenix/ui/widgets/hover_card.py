from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QWidget

from phoenix.ui.styles import palette


class HoverCard(QFrame):
    """Card com destaque de hover, brilho e barra superior animada."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("hover-card")
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self._hover_progress = 0.0
        self._lift = 0.0
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(10)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(self._shadow)

        self._top_bar = QLabel(self)
        self._top_bar.setFixedHeight(2)
        self._top_bar.setMaximumWidth(0)
        self._top_bar.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #C0392B,stop:1 #E67E22); border-radius: 1px;"
        )

        self._container = QWidget(self)
        self.content_layout = QVBoxLayout(self._container)
        self.content_layout.setContentsMargins(14, 14, 14, 14)
        self.content_layout.setSpacing(10)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._top_bar, alignment=Qt.AlignmentFlag.AlignTop)
        root.addWidget(self._container, 1)

        self._lift_anim = QPropertyAnimation(self, b"lift", self)
        self._lift_anim.setDuration(200)
        self._lift_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._bar_anim = QPropertyAnimation(self._top_bar, b"maximumWidth", self)
        self._bar_anim.setDuration(200)
        self._bar_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.installEventFilter(self)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self._hover_progress >= 0.99:
            self._top_bar.setMaximumWidth(self.width())

    def eventFilter(self, obj: object, event: QEvent) -> bool:
        if obj is self:
            if event.type() == QEvent.Type.Enter:
                self._animate_hover(True)
            elif event.type() == QEvent.Type.Leave:
                self._animate_hover(False)
        return super().eventFilter(obj, event)

    def _animate_hover(self, entering: bool) -> None:
        self._set_hover_progress(1.0 if entering else 0.0)

        self._lift_anim.stop()
        self._lift_anim.setStartValue(self._lift)
        self._lift_anim.setEndValue(3.0 if entering else 0.0)
        self._lift_anim.start()

        self._bar_anim.stop()
        self._bar_anim.setStartValue(self._top_bar.maximumWidth())
        self._bar_anim.setEndValue(self.width() if entering else 0)
        self._bar_anim.start()

    def _set_hover_progress(self, value: float) -> None:
        self._hover_progress = value
        mix = max(0.0, min(1.0, value))
        blur = 10 + (14 * mix)
        y_offset = 4 + (4 * mix)
        effect = self.graphicsEffect()
        if isinstance(effect, QGraphicsDropShadowEffect):
            effect.setBlurRadius(blur)
            effect.setOffset(0, y_offset)
            effect.setColor(QColor(192, 57, 43, int(40 + 80 * mix)))

    def _get_hover_progress(self) -> float:
        return self._hover_progress

    hoverProgress = pyqtProperty(float, fget=_get_hover_progress, fset=_set_hover_progress)

    def _set_lift(self, value: float) -> None:
        self._lift = value
        self.setContentsMargins(0, int(-value), 0, int(value))

    def _get_lift(self) -> float:
        return self._lift

    lift = pyqtProperty(float, fget=_get_lift, fset=_set_lift)
