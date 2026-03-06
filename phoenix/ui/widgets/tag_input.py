from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QWidget


class TagInputWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Adicionar tag")
        self.tags = QListWidget()
        self.tags.setMaximumHeight(80)
        layout.addWidget(self.input)
        layout.addWidget(self.tags)
        self.input.returnPressed.connect(self._add_tag)

    def _add_tag(self) -> None:
        text = self.input.text().strip()
        if text:
            self.tags.addItem(QListWidgetItem(text))
            self.input.clear()

    def values(self) -> list[str]:
        return [self.tags.item(index).text() for index in range(self.tags.count())]
