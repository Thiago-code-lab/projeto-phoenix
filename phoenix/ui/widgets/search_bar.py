from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit, QWidget


class SearchBar(QWidget):
    search_changed = pyqtSignal(str, str)

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Buscar")
        self.filter_box = QComboBox()
        self.filter_box.addItems(["Todos", "Ativos", "Concluidos"])
        layout.addWidget(self.input, 1)
        layout.addWidget(self.filter_box)
        self.input.textChanged.connect(self._emit_change)
        self.filter_box.currentTextChanged.connect(self._emit_change)

    def _emit_change(self) -> None:
        self.search_changed.emit(self.input.text(), self.filter_box.currentText())
