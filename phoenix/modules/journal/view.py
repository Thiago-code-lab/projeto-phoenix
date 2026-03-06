from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QDate, QTimer
from PyQt6.QtWidgets import (
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.core.models import JournalEntry
from phoenix.modules.journal.controller import JournalController
from phoenix.modules.journal.widgets import CalendarStrip, EntryEditor, MoodSelector, RichToolbar, TagChipInput
from phoenix.ui.widgets.confirm_dialog import ConfirmDialog
from phoenix.utils.constants import Events, UiLimits


class JournalView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = JournalController()
        self.event_bus = event_bus
        self._current_month = date.today().replace(day=1)
        self._selected_entry: JournalEntry | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        top = QHBoxLayout()
        left_panel = QVBoxLayout()
        self.calendar = CalendarStrip()
        left_panel.addWidget(self.calendar)

        month_controls = QHBoxLayout()
        self.prev_month = QPushButton("<")
        self.next_month = QPushButton(">")
        self.month_label = QLabel("")
        month_controls.addWidget(self.prev_month)
        month_controls.addWidget(self.month_label, 1)
        month_controls.addWidget(self.next_month)
        left_panel.addLayout(month_controls)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Busca")
        left_panel.addWidget(self.search_input)
        top.addLayout(left_panel, 1)

        center_panel = QVBoxLayout()
        self.toolbar = RichToolbar()
        center_panel.addWidget(self.toolbar)
        layout.addLayout(top)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Titulo da entrada")
        center_panel.addWidget(self.title_input)

        meta = QHBoxLayout()
        self.mood_selector = MoodSelector()
        self.tags_input = TagChipInput()
        meta.addWidget(QLabel("Humor"))
        meta.addWidget(self.mood_selector)
        meta.addWidget(QLabel("Tags"))
        meta.addWidget(self.tags_input, 1)
        center_panel.addLayout(meta)

        self.editor = EntryEditor()
        center_panel.addWidget(self.editor, 1)

        actions = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.delete_button = QPushButton("Excluir")
        self.delete_button.setObjectName("btn-secondary")
        actions.addWidget(self.save_button)
        actions.addWidget(self.delete_button)
        actions.addStretch(1)
        center_panel.addLayout(actions)
        top.addLayout(center_panel, 2)

        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Data"))
        self.entry_date = QDateEdit()
        self.entry_date.setCalendarPopup(True)
        self.entry_date.setDate(QDate.currentDate())
        right_panel.addWidget(self.entry_date)
        self.streak_label = QLabel("Streak: 0 dias")
        right_panel.addWidget(self.streak_label)
        right_panel.addStretch(1)
        top.addLayout(right_panel, 0)

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(UiLimits.AUTO_SAVE_INTERVAL_MS)
        self._autosave_timer.timeout.connect(self._autosave)

        self.save_button.clicked.connect(self._save)
        self.delete_button.clicked.connect(self._delete)
        self.search_input.textChanged.connect(lambda _: self._reload())
        self.prev_month.clicked.connect(self._go_prev_month)
        self.next_month.clicked.connect(self._go_next_month)
        self.editor.editor.textChanged.connect(self._schedule_autosave)
        self.title_input.textChanged.connect(self._schedule_autosave)
        self.entry_date.dateChanged.connect(self._load_entry_for_date)
        self._reload()

    def _reload(self) -> None:
        entries = self.controller.get_entries(month=self._current_month, search=self.search_input.text().strip() or None)
        calendar_data = self.controller.get_entries_calendar(self._current_month.year, self._current_month.month)
        self.calendar.set_month(self._current_month.year, self._current_month.month)
        self.calendar.set_calendar_data(calendar_data)
        self.month_label.setText(self._current_month.strftime("%m/%Y"))
        self.streak_label.setText(f"Streak: {self.controller.get_streak()} dias")

        if entries:
            target_date = self.entry_date.date().toPyDate()
            selected = next((entry for entry in entries if entry.date == target_date), entries[0])
            self._populate_form(selected)
        else:
            self._selected_entry = None
            self.title_input.clear()
            self.editor.editor.clear()
            self.tags_input.set_tags([])

    def _save(self) -> None:
        content = self.editor.editor.toPlainText().strip()
        if not content:
            self.show_toast("Conteudo vazio nao pode ser salvo.", kind="warning")
            return
        payload = {
            "date": self.entry_date.date().toPyDate(),
            "title": self.title_input.text().strip() or "Entrada",
            "content": content,
            "mood": self.mood_selector.value(),
            "tags": self.tags_input.tags(),
        }
        if self._selected_entry is None:
            self._selected_entry = self.controller.create(payload)
        else:
            self._selected_entry = self.controller.update(self._selected_entry.id, payload)
        self.show_toast("Entrada salva.", kind="success")
        self._publish_data_changed()
        self._reload()

    def _autosave(self) -> None:
        if not self.editor.editor.toPlainText().strip():
            return
        self._save()

    def _schedule_autosave(self) -> None:
        self._autosave_timer.start()

    def _delete(self) -> None:
        if self._selected_entry is None:
            return
        confirm = ConfirmDialog("Excluir entrada", "Deseja excluir a entrada atual?")
        if confirm.exec() == 0:
            return
        self.controller.delete(self._selected_entry.id)
        self._selected_entry = None
        self.show_toast("Entrada excluida.", kind="warning")
        self._publish_data_changed()
        self._reload()

    def _go_prev_month(self) -> None:
        year = self._current_month.year
        month = self._current_month.month - 1
        if month == 0:
            month = 12
            year -= 1
        self._current_month = date(year, month, 1)
        self._reload()

    def _go_next_month(self) -> None:
        year = self._current_month.year
        month = self._current_month.month + 1
        if month == 13:
            month = 1
            year += 1
        self._current_month = date(year, month, 1)
        self._reload()

    def _load_entry_for_date(self) -> None:
        selected = self.controller.get_by_date(self.entry_date.date().toPyDate())
        if selected is not None:
            self._populate_form(selected)

    def _populate_form(self, entry: JournalEntry) -> None:
        self._selected_entry = entry
        self.entry_date.setDate(QDate(entry.date.year, entry.date.month, entry.date.day))
        self.title_input.setText(entry.title or "")
        self.editor.editor.setPlainText(entry.content)
        self.tags_input.set_tags(entry.tags or [])

    def show_toast(self, message: str, kind: str = "info") -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[{kind}] {message}"})

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "journal"})
