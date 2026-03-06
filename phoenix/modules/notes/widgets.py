from __future__ import annotations

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QListWidget, QPlainTextEdit, QPushButton, QTextBrowser, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.rich_editor import RichEditor


class NoteTree(CardWidget):
    def __init__(self) -> None:
        super().__init__("Estrutura")
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Notas"])
        self.layout.addWidget(self.tree)

    def set_notes(self, notes: list) -> None:
        self.tree.clear()
        roots: dict[int | None, list] = {}
        for note in notes:
            roots.setdefault(note.parent_id, []).append(note)

        def add_children(parent_item: QTreeWidgetItem | QTreeWidget, parent_id: int | None) -> None:
            for note in roots.get(parent_id, []):
                item = QTreeWidgetItem([note.title])
                item.setData(0, 256, note.id)
                parent_item.addTopLevelItem(item) if isinstance(parent_item, QTreeWidget) else parent_item.addChild(item)
                add_children(item, note.id)

        add_children(self.tree, None)


class NoteEditor(QWidget):
    saveRequested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.editor = RichEditor()
        self.preview = QTextBrowser()
        self.preview.hide()
        self.toggle_preview = QPushButton("Preview")
        self.toggle_preview.setObjectName("btn-secondary")
        layout.addWidget(self.toggle_preview)
        layout.addWidget(self.editor, 1)
        layout.addWidget(self.preview, 1)
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(2000)
        self._autosave_timer.timeout.connect(self.saveRequested.emit)
        self.editor.editor.textChanged.connect(self._queue_autosave)
        self.toggle_preview.clicked.connect(self._toggle_preview)

    def set_content(self, title: str, content: str) -> None:
        self.editor.editor.blockSignals(True)
        self.editor.editor.setMarkdown(content or "")
        self.editor.editor.blockSignals(False)
        self.preview.setMarkdown(content or "")

    def title_guess(self) -> str:
        first_line = self.editor.editor.toPlainText().splitlines()
        return first_line[0][:80] if first_line else "Nova nota"

    def markdown(self) -> str:
        return self.editor.to_markdown()

    def _queue_autosave(self) -> None:
        self.preview.setMarkdown(self.editor.editor.toMarkdown())
        self._autosave_timer.start()

    def _toggle_preview(self) -> None:
        visible = not self.preview.isVisible()
        self.preview.setVisible(visible)


class BacklinkPanel(CardWidget):
    def __init__(self) -> None:
        super().__init__("Backlinks")
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

    def set_backlinks(self, notes: list) -> None:
        self.list_widget.clear()
        for note in notes:
            self.list_widget.addItem(note.title)


class TagFilter(CardWidget):
    def __init__(self) -> None:
        super().__init__("Filtro")
        self.layout.addWidget(QLabel("Busca em tempo real por titulo e conteudo"))


class NoteList(CardWidget):
    def __init__(self) -> None:
        super().__init__("Notas")
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

    def set_notes(self, notes: list) -> None:
        self.list_widget.clear()
        for note in notes:
            self.list_widget.addItem(f"{note.title}")
