from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QHBoxLayout, QVBoxLayout, QWidget


class StreakBadge(QWidget):
    def __init__(self, days: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._days = days
        self.setMinimumHeight(72)
        self.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #C0392B,stop:1 #E67E22);"
            "border-radius: 12px;"
        )

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(16)
        self._shadow.setOffset(0, 6)
        self._shadow.setColor(QColor(230, 126, 34, 130))
        self.setGraphicsEffect(self._shadow)

        content = QHBoxLayout(self)
        content.setContentsMargins(14, 10, 14, 10)
        content.setSpacing(10)

        self.flame_label = QLabel("🔥")
        self.flame_label.setStyleSheet("font-size: 20px;")
        content.addWidget(self.flame_label)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        self.value_label = QLabel(str(days))
        self.value_label.setObjectName("label-value")
        self.value_label.setStyleSheet("color: #FFFFFF; font-size: 26px; font-weight: 700;")
        self.caption_label = QLabel("dias seguidos")
        self.caption_label.setStyleSheet("color: rgba(255,255,255,0.88); font-size: 11px; text-transform: uppercase;")
        text_col.addWidget(self.value_label)
        text_col.addWidget(self.caption_label)
        content.addLayout(text_col, 1)

        self._pulse_up = QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._pulse_up.setDuration(1000)
        self._pulse_up.setStartValue(8)
        self._pulse_up.setEndValue(20)
        self._pulse_up.setEasingCurve(QEasingCurve.Type.InOutSine)

        self._pulse_down = QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._pulse_down.setDuration(1000)
        self._pulse_down.setStartValue(20)
        self._pulse_down.setEndValue(8)
        self._pulse_down.setEasingCurve(QEasingCurve.Type.InOutSine)

        self._pulse_group = QSequentialAnimationGroup(self)
        self._pulse_group.addAnimation(self._pulse_up)
        self._pulse_group.addAnimation(self._pulse_down)
        self._pulse_group.setLoopCount(-1)
        self._pulse_group.start()

    def set_days(self, days: int) -> None:
        self._days = days
        self.value_label.setText(str(days))
