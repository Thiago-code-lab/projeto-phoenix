from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from phoenix.modules.assistant.controller import AssistantController


class MessageBubble(QFrame):
    """Componente visual de mensagem de chat.

    Args:
        text: Conteudo textual da mensagem.
        user: Define se a mensagem e do usuario.
    """

    def __init__(self, text: str, user: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("assistant-message")
        self.setFrameShape(QFrame.Shape.NoFrame)

        style_user = "background: rgba(230,126,34,0.15); border-radius: 10px 10px 2px 10px;"
        style_assistant = "background: #1e1e1e; border-radius: 10px 10px 10px 2px;"
        self.setStyleSheet(style_user if user else style_assistant)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 12px;")
        layout.addWidget(label)


class PhoenixAssistantPanel(QDockWidget):
    """Painel lateral do assistant com chat em tempo real."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Phoenix Assistant")
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.setFixedWidth(320)

        self.controller = AssistantController(self)

        shell = QWidget(self)
        shell.setStyleSheet("background: #111111; border-left: 1px solid #1e1e1e;")
        self.setWidget(shell)

        root = QVBoxLayout(shell)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("PHOENIX ASSISTANT")
        title.setObjectName("label-section")
        close_btn = QPushButton("x")
        close_btn.setObjectName("btn-ghost")
        close_btn.setFixedWidth(28)
        close_btn.clicked.connect(self.hide)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(close_btn)
        root.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.feed = QWidget()
        self.feed_layout = QVBoxLayout(self.feed)
        self.feed_layout.setContentsMargins(0, 0, 0, 0)
        self.feed_layout.setSpacing(8)
        self.feed_layout.addStretch(1)
        self.scroll.setWidget(self.feed)
        root.addWidget(self.scroll, 1)

        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Pergunte algo...")
        self.send = QPushButton("->")
        self.send.setObjectName("btn-primary")
        self.send.setFixedWidth(40)
        input_row.addWidget(self.input, 1)
        input_row.addWidget(self.send)
        root.addLayout(input_row)

        self.status = QLabel(f"Usando: {self.controller.backend_name()}")
        self.status.setStyleSheet("font-size: 10px; color: #555555;")
        root.addWidget(self.status)

        self.send.clicked.connect(self._submit)
        self.input.returnPressed.connect(self._submit)
        self.controller.response_ready.connect(self._append_assistant)

    def _append_bubble(self, text: str, user: bool) -> None:
        bubble = MessageBubble(text, user=user)
        self.feed_layout.insertWidget(max(self.feed_layout.count() - 1, 0), bubble)
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def _submit(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self._append_bubble(text, user=True)
        self.input.clear()
        self.controller.chat(text, context={})

    def _append_assistant(self, text: str) -> None:
        self._append_bubble(text, user=False)
