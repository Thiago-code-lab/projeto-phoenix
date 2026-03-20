from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DropZone(QWidget):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("drop-zone")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.title = QLabel("Arraste um arquivo CSV/OFX aqui")
        self.title.setObjectName("drop-zone-title")
        self.subtitle = QLabel("Ou use o botao de selecao")
        self.subtitle.setObjectName("drop-zone-subtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if not file_path:
                continue
            suffix = Path(file_path).suffix.lower()
            if suffix in {".csv", ".ofx"}:
                self.fileDropped.emit(file_path)
                event.acceptProposedAction()
                return
        event.ignore()
