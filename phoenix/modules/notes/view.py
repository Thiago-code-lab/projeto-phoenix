from __future__ import annotations

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from phoenix.modules.notes.controller import NotesController
from phoenix.modules.notes.widgets import BacklinkPanel, NoteEditor, NoteList, NoteTree


class NotesView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.controller = NotesController()
        self.current_note_id: int | None = None
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        left_panel = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por titulo e conteudo")
        self.tree = NoteTree()
        left_panel.addWidget(self.search_input)
        left_panel.addWidget(self.tree)

        center_panel = QVBoxLayout()
        self.note_list = NoteList()
        center_panel.addWidget(self.note_list)

        self.editor = NoteEditor()
        self.backlinks = BacklinkPanel()

        layout.addLayout(left_panel, 1)
        layout.addLayout(center_panel, 1)
        layout.addWidget(self.editor, 2)
        layout.addWidget(self.backlinks, 1)

        self.search_input.textChanged.connect(self._refresh_results)
        self.note_list.list_widget.currentRowChanged.connect(self._select_from_list)
        self.tree.tree.itemClicked.connect(self._select_from_tree)
        self.editor.saveRequested.connect(self._autosave)
        QShortcut(QKeySequence("Ctrl+Shift+F"), self, activated=self.search_input.setFocus)
        self.refresh()

    def refresh(self) -> None:
        notes = self.controller.list_notes()
        self._notes_cache = notes
        self._filtered_notes = notes
        self.tree.set_notes(notes)
        self.note_list.set_notes(notes)
        if notes and self.current_note_id is None:
            self._load_note(notes[0].id)

    def _refresh_results(self) -> None:
        notes = self.controller.search_notes(self.search_input.text().strip())
        self.note_list.set_notes(notes)
        self._filtered_notes = notes

    def _select_from_list(self, index: int) -> None:
        notes = getattr(self, "_filtered_notes", self._notes_cache)
        if 0 <= index < len(notes):
            self._load_note(notes[index].id)

    def _select_from_tree(self, item, column: int) -> None:
        note_id = item.data(0, 256)
        if note_id is not None:
            self._load_note(int(note_id))

    def _load_note(self, note_id: int) -> None:
        note = next((note for note in self._notes_cache if note.id == note_id), None)
        if note is None:
            return
        self.current_note_id = note.id
        self.editor.set_content(note.title, note.content or "")
        self.backlinks.set_backlinks(self.controller.backlinks(note.id))

    def _autosave(self) -> None:
        content = self.editor.markdown()
        title = self.editor.title_guess()
        note = self.controller.save_note(self.current_note_id, title, content)
        self.current_note_id = note.id
        self.refresh()
