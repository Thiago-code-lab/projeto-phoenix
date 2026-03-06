from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QPushButton, QWidget

from phoenix.core.models import Book
from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.chart_widget import ChartWidget


class BookCard(CardWidget):
    clicked = pyqtSignal(int)

    def __init__(self, book: Book) -> None:
        super().__init__()
        self.book = book
        title = QLabel(book.title)
        title.setWordWrap(True)
        title.setMaximumHeight(44)
        author = QLabel(book.author or "Autor indefinido")
        author.setStyleSheet("color: #94a3b8;")
        status = QLabel((book.status or "wishlist").capitalize())
        status.setObjectName("tag")
        self.layout.addWidget(title)
        self.layout.addWidget(author)
        self.layout.addWidget(status)

        total_pages = max(book.pages or 0, 1)
        ratio = min(max((book.pages_read or 0) / total_pages, 0), 1)
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(int(ratio * 100))
        self.layout.addWidget(progress)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.book.id)
        super().mousePressEvent(event)


class StarRating(QWidget):
    changed = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self._value = 0
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._buttons: list[QPushButton] = []
        for index in range(5):
            button = QPushButton("☆")
            button.setFlat(True)
            button.clicked.connect(lambda _, idx=index + 1: self.set_value(idx))
            self._buttons.append(button)
            layout.addWidget(button)
        layout.addStretch(1)

    def value(self) -> int:
        return self._value

    def set_value(self, value: int) -> None:
        self._value = max(0, min(value, 5))
        for idx, button in enumerate(self._buttons, start=1):
            button.setText("★" if idx <= self._value else "☆")
        self.changed.emit(self._value)


class ReadingProgressBar(QProgressBar):
    def update_progress(self, pages_read: int, total_pages: int) -> None:
        total = max(total_pages, 1)
        ratio = int((max(pages_read, 0) / total) * 100)
        self.setValue(min(max(ratio, 0), 100))
        self.setFormat(f"{pages_read} de {total_pages} paginas")


class GenreChart(ChartWidget):
    def plot_distribution(self, distribution: dict[str, int]) -> None:
        labels = list(distribution.keys())
        values = [float(value) for value in distribution.values()]
        self.plot_pie(labels, values, ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#38bdf8"])


class BookForm(CardWidget):
    def __init__(self) -> None:
        super().__init__("Novo livro")
        self.title_input = QLabel("Use o painel de detalhe para salvar.")
        self.layout.addWidget(self.title_input)
