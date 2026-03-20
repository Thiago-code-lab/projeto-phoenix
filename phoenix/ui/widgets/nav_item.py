from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class NavItem(QWidget):
    clicked = pyqtSignal()

    def __init__(self, label: str, icon_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._active = False

        self._indicator = QLabel()
        self._indicator.setFixedWidth(3)
        self._indicator.setMinimumHeight(0)
        self._indicator.setMaximumHeight(0)
        self._indicator.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #C0392B,stop:1 #E67E22); border-radius: 1px;"
        )

        self.button = QPushButton(label)
        self.button.setObjectName("btn-flat")
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setCheckable(True)
        self.button.setIcon(self._load_icon(icon_path))
        self.button.setIconSize(QSize(16, 16))
        self.button.setStyleSheet(
            "QPushButton {"
            "text-align: left;"
            "padding: 10px 12px;"
            "border-radius: 8px;"
            "color: #888888;"
            "background: transparent;"
            "}"
            "QPushButton:hover {"
            "background: rgba(230,126,34,0.07);"
            "color: #F0F0F0;"
            "}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)
        layout.addWidget(self._indicator, 0, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.button, 1)

        self._indicator_anim = QPropertyAnimation(self._indicator, b"maximumHeight", self)
        self._indicator_anim.setDuration(180)
        self._indicator_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.button.clicked.connect(self.clicked.emit)

    def _load_icon(self, icon_path: str) -> QIcon:
        path = Path(icon_path)
        if path.exists():
            return QIcon(str(path))
        return QIcon()

    def set_active(self, active: bool) -> None:
        self._active = active
        self.button.setChecked(active)
        if active:
            self.button.setStyleSheet(
                "QPushButton {"
                "text-align: left;"
                "padding: 10px 12px;"
                "border-radius: 8px;"
                "color: #F39C12;"
                "background: rgba(230,126,34,0.10);"
                "}"
                "QPushButton:hover {"
                "background: rgba(230,126,34,0.14);"
                "color: #F39C12;"
                "}"
            )
        else:
            self.button.setStyleSheet(
                "QPushButton {"
                "text-align: left;"
                "padding: 10px 12px;"
                "border-radius: 8px;"
                "color: #888888;"
                "background: transparent;"
                "}"
                "QPushButton:hover {"
                "background: rgba(230,126,34,0.07);"
                "color: #F0F0F0;"
                "}"
            )

        self._indicator_anim.stop()
        self._indicator_anim.setStartValue(self._indicator.maximumHeight())
        self._indicator_anim.setEndValue(self.height() if active else 0)
        self._indicator_anim.start()
