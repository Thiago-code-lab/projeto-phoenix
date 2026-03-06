from __future__ import annotations

"""Tabela paginada reutilizavel para listas grandes."""

from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from phoenix.utils.constants import UiLimits


class DataTableWidget(QWidget):
    """Encapsula uma QTableWidget com paginação local."""

    def __init__(self, page_size: int = UiLimits.DEFAULT_PAGE_SIZE) -> None:
        super().__init__()
        self._headers: list[str] = []
        self._rows: list[list[str]] = []
        self._page_size = page_size
        self._page_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget()
        layout.addWidget(self.table)

        pagination = QHBoxLayout()
        self.previous_button = QPushButton("Anterior")
        self.previous_button.setObjectName("btn-secondary")
        self.next_button = QPushButton("Proxima")
        self.next_button.setObjectName("btn-secondary")
        pagination.addStretch(1)
        pagination.addWidget(self.previous_button)
        pagination.addWidget(self.next_button)
        layout.addLayout(pagination)

        self.previous_button.clicked.connect(self._go_previous)
        self.next_button.clicked.connect(self._go_next)

    def set_data(self, headers: list[str], rows: list[list[str]]) -> None:
        """Define os dados da tabela e reinicia a paginacao."""

        self._headers = headers
        self._rows = rows
        self._page_index = 0
        self._render_page()

    def _render_page(self) -> None:
        start = self._page_index * self._page_size
        end = start + self._page_size
        visible_rows = self._rows[start:end]
        self.table.setColumnCount(len(self._headers))
        self.table.setHorizontalHeaderLabels(self._headers)
        self.table.setRowCount(len(visible_rows))
        for row_index, row in enumerate(visible_rows):
            for column_index, value in enumerate(row):
                self.table.setItem(row_index, column_index, QTableWidgetItem(value))
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()
        self.previous_button.setEnabled(self._page_index > 0)
        self.next_button.setEnabled(end < len(self._rows))

    def _go_previous(self) -> None:
        if self._page_index > 0:
            self._page_index -= 1
            self._render_page()

    def _go_next(self) -> None:
        if (self._page_index + 1) * self._page_size < len(self._rows):
            self._page_index += 1
            self._render_page()
