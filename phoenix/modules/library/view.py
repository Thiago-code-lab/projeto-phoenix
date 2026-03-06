from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.core.models import Book
from phoenix.modules.library.controller import LibraryController
from phoenix.modules.library.widgets import BookCard, GenreChart, ReadingProgressBar, StarRating
from phoenix.ui.widgets.empty_state import EmptyState
from phoenix.utils.constants import Events


class LibraryView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = LibraryController()
        self.event_bus = event_bus
        self._selected_book_id: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        top = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Busca...")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["all", "wishlist", "reading", "completed", "abandoned"])
        self.genre_filter = QComboBox()
        self.genre_filter.addItem("all")
        self.sort_filter = QComboBox()
        self.sort_filter.addItems(["recent", "title"])
        self.add_button = QPushButton("+ Adicionar")
        self.add_button.setObjectName("btn-primary")
        top.addWidget(self.search_input, 1)
        top.addWidget(self.status_filter)
        top.addWidget(self.genre_filter)
        top.addWidget(self.sort_filter)
        top.addWidget(self.add_button)
        layout.addLayout(top)

        self.cards_container = QWidget()
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(12)
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setWidget(self.cards_container)

        self.empty_state = EmptyState("Sem livros", "Adicione livros para montar sua biblioteca.", "Adicionar")
        self.stack = QStackedWidget()
        self.stack.addWidget(self.cards_scroll)
        self.stack.addWidget(self.empty_state)
        layout.addWidget(self.stack, 1)

        stats_row = QHBoxLayout()
        self.stats_label = QLabel("Total: 0")
        self.genre_chart = GenreChart()
        stats_row.addWidget(self.stats_label, 0)
        stats_row.addWidget(self.genre_chart, 1)
        layout.addLayout(stats_row)

        self.search_input.textChanged.connect(lambda _: self.refresh())
        self.status_filter.currentTextChanged.connect(lambda _: self.refresh())
        self.genre_filter.currentTextChanged.connect(lambda _: self.refresh())
        self.sort_filter.currentTextChanged.connect(lambda _: self.refresh())
        self.add_button.clicked.connect(self._open_new_dialog)
        self.empty_state.action_button.clicked.connect(self._open_new_dialog)

        self.refresh()

    def refresh(self) -> None:
        books = self.controller.get_all(
            status=self.status_filter.currentText(),
            genre=self.genre_filter.currentText(),
            search=self.search_input.text().strip() or None,
        )
        if self.sort_filter.currentText() == "title":
            books.sort(key=lambda book: book.title.lower())

        self._clear_cards()
        if not books:
            self.stack.setCurrentWidget(self.empty_state)
        else:
            self.stack.setCurrentIndex(0)
            for idx, book in enumerate(books):
                card = BookCard(book)
                card.clicked.connect(self._open_detail_dialog)
                row = idx // 4
                col = idx % 4
                self.cards_grid.addWidget(card, row, col)

        all_books = self.controller.get_all()
        genres = sorted({(book.genre or "Sem genero") for book in all_books})
        current = self.genre_filter.currentText()
        self.genre_filter.blockSignals(True)
        self.genre_filter.clear()
        self.genre_filter.addItem("all")
        self.genre_filter.addItems(genres)
        if current in genres or current == "all":
            self.genre_filter.setCurrentText(current)
        self.genre_filter.blockSignals(False)

        stats = self.controller.get_stats()
        self.stats_label.setText(
            f"Total: {stats['total']} | Lendo: {stats['reading']} | Concluidos no ano: {stats['completed_year']} | Paginas no ano: {stats['pages_read_year']}"
        )
        self.genre_chart.plot_distribution(stats["genre_distribution"])

    def _open_new_dialog(self) -> None:
        self._open_detail_dialog(0)

    def _open_detail_dialog(self, book_id: int) -> None:
        book = None
        if book_id:
            for item in self.controller.get_all():
                if item.id == book_id:
                    book = item
                    break

        dialog = QDialog(self)
        dialog.setWindowTitle("Detalhe do livro")
        dialog.resize(520, 520)
        root = QVBoxLayout(dialog)

        form = QFormLayout()
        title_input = QLineEdit(book.title if book else "")
        author_input = QLineEdit(book.author if book else "")
        genre_input = QLineEdit(book.genre if book else "")
        status_input = QComboBox()
        status_input.addItems(["wishlist", "reading", "completed", "abandoned"])
        if book:
            status_input.setCurrentText(book.status)
        pages_input = QSpinBox()
        pages_input.setRange(0, 100000)
        pages_input.setValue(book.pages or 0 if book else 0)
        pages_read_input = QSpinBox()
        pages_read_input.setRange(0, 100000)
        pages_read_input.setValue(book.pages_read if book else 0)
        progress = ReadingProgressBar()
        progress.update_progress(pages_read_input.value(), pages_input.value())
        pages_read_input.valueChanged.connect(lambda value: progress.update_progress(value, pages_input.value()))
        pages_input.valueChanged.connect(lambda value: progress.update_progress(pages_read_input.value(), value))

        notes_input = QTextEdit(book.notes if book else "")
        rating = StarRating()
        if book and book.rating:
            rating.set_value(int(book.rating))

        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        end_date = QDateEdit()
        end_date.setCalendarPopup(True)
        if book and book.start_date:
            start_date.setDate(QDate(book.start_date.year, book.start_date.month, book.start_date.day))
        else:
            start_date.setDate(QDate.currentDate())
        if book and book.end_date:
            end_date.setDate(QDate(book.end_date.year, book.end_date.month, book.end_date.day))
        else:
            end_date.setDate(QDate.currentDate())

        form.addRow("Titulo", title_input)
        form.addRow("Autor", author_input)
        form.addRow("Genero", genre_input)
        form.addRow("Status", status_input)
        form.addRow("Paginas", pages_input)
        form.addRow("Paginas lidas", pages_read_input)
        form.addRow("Progresso", progress)
        form.addRow("Notas", notes_input)
        form.addRow("Rating", rating)
        form.addRow("Inicio", start_date)
        form.addRow("Fim", end_date)
        root.addLayout(form)

        buttons = QHBoxLayout()
        save = QPushButton("Salvar")
        save.setObjectName("btn-primary")
        delete = QPushButton("Excluir")
        delete.setObjectName("btn-secondary")
        close = QPushButton("Fechar")
        buttons.addWidget(save)
        if book:
            buttons.addWidget(delete)
        buttons.addStretch(1)
        buttons.addWidget(close)
        root.addLayout(buttons)

        save.clicked.connect(
            lambda: self._persist_book(
                dialog,
                book,
                {
                    "title": title_input.text().strip(),
                    "author": author_input.text().strip(),
                    "genre": genre_input.text().strip(),
                    "status": status_input.currentText(),
                    "pages": pages_input.value(),
                    "pages_read": pages_read_input.value(),
                    "rating": rating.value() or None,
                    "notes": notes_input.toPlainText().strip(),
                    "start_date": start_date.date().toPyDate(),
                    "end_date": end_date.date().toPyDate(),
                },
            )
        )
        delete.clicked.connect(lambda: self._delete_book(dialog, book))
        close.clicked.connect(dialog.reject)
        dialog.exec()

    def _persist_book(self, dialog: QDialog, book: Book | None, payload: dict) -> None:
        title = payload["title"]
        if not title:
            self.show_toast("Titulo e obrigatorio.", kind="error")
            return
        if book is None:
            self.controller.create(payload)
            self.show_toast("Livro adicionado.", kind="success")
        else:
            self.controller.update(book.id, payload)
            self.show_toast("Livro atualizado.", kind="success")
        self._publish_data_changed()
        dialog.accept()
        self.refresh()

    def _delete_book(self, dialog: QDialog, book: Book | None) -> None:
        if book is None:
            return
        self.controller.delete(book.id)
        self.show_toast("Livro excluido.", kind="warning")
        self._publish_data_changed()
        dialog.accept()
        self.refresh()

    def show_toast(self, message: str, kind: str = "info") -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[{kind}] {message}"})

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "library"})

    def _clear_cards(self) -> None:
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
