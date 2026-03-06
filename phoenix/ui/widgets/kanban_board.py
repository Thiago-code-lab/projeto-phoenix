from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from .card import CardWidget


class KanbanColumn(CardWidget):
    def __init__(self, title: str) -> None:
        super().__init__(title)
        self.list_widget = QListWidget()
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDefaultDropAction(self.list_widget.defaultDropAction())
        self.layout.addWidget(self.list_widget)

    def add_card(self, title: str) -> None:
        self.list_widget.addItem(QListWidgetItem(title))


class KanbanBoard(QWidget):
    def __init__(self, columns: list[str] | None = None) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        self.columns: list[KanbanColumn] = []
        for title in columns or ["Backlog", "Todo", "Doing", "Done"]:
            column = KanbanColumn(title)
            layout.addWidget(column)
            self.columns.append(column)

    def seed(self, items: dict[str, list[str]]) -> None:
        for column in self.columns:
            for item in items.get(column.layout.itemAt(0).widget().text(), []):
                column.add_card(item)
