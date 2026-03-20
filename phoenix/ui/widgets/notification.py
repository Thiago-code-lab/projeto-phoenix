from __future__ import annotations

"""Widget de notificacao visual nao bloqueante."""

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QLabel, QWidget

from phoenix.utils.constants import UiLimits


class ToastNotification(QLabel):
    """Exibe mensagens transitórias sobre a interface principal."""

    def __init__(self, message: str, kind: str = "info", parent: QWidget | None = None, timeout_ms: int = UiLimits.TOAST_TIMEOUT_MS) -> None:
        super().__init__(message, parent)
        self.setObjectName("toast")
        self.setProperty("kind", kind)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMargin(10)
        self.setMinimumWidth(260)
        self.adjustSize()
        QTimer.singleShot(timeout_ms, self.hide)

    def show_bottom_right(self) -> None:
        """Mostra o toast no canto inferior direito sobre o widget pai."""

        parent = self.parentWidget()
        if parent is not None:
            self.adjustSize()
            x_pos = max(parent.width() - self.width() - 24, 24)
            y_pos = max(parent.height() - self.height() - 24, 24)
            self.move(x_pos, y_pos)
        self.show()
