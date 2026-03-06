from __future__ import annotations

from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout, QWidget, QInputDialog


class RichEditor(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.bold_button = QPushButton("B")
        self.italic_button = QPushButton("I")
        self.code_button = QPushButton("</>")
        self.h1_button = QPushButton("H1")
        self.h2_button = QPushButton("H2")
        self.h3_button = QPushButton("H3")
        self.list_button = QPushButton("Lista")
        self.link_button = QPushButton("Link")
        toolbar.addWidget(self.bold_button)
        toolbar.addWidget(self.italic_button)
        toolbar.addWidget(self.code_button)
        toolbar.addWidget(self.h1_button)
        toolbar.addWidget(self.h2_button)
        toolbar.addWidget(self.h3_button)
        toolbar.addWidget(self.list_button)
        toolbar.addWidget(self.link_button)
        toolbar.addStretch(1)
        self.editor = QTextEdit()
        layout.addLayout(toolbar)
        layout.addWidget(self.editor)
        self.bold_button.clicked.connect(lambda: self._wrap_selection("**", "**"))
        self.italic_button.clicked.connect(lambda: self._wrap_selection("*", "*"))
        self.code_button.clicked.connect(lambda: self._wrap_selection("`", "`"))
        self.h1_button.clicked.connect(lambda: self._prefix_line("# "))
        self.h2_button.clicked.connect(lambda: self._prefix_line("## "))
        self.h3_button.clicked.connect(lambda: self._prefix_line("### "))
        self.list_button.clicked.connect(lambda: self._prefix_line("- "))
        self.link_button.clicked.connect(self._insert_link)

    def to_markdown(self) -> str:
        return self.editor.toMarkdown()

    def _wrap_selection(self, prefix: str, suffix: str) -> None:
        cursor = self.editor.textCursor()
        selected = cursor.selectedText() or "texto"
        cursor.insertText(f"{prefix}{selected}{suffix}")

    def _prefix_line(self, prefix: str) -> None:
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.insertText(prefix)

    def _insert_link(self) -> None:
        url, ok = QInputDialog.getText(self, "Inserir link", "URL:")
        if not ok or not url.strip():
            return
        self._wrap_selection("[", f"]({url.strip()})")
