from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class Header(QWidget):
    """Cabecalho principal com contexto da pagina e acoes globais."""

    def __init__(self, title: str = "Dashboard", subtitle: str = "Visao geral") -> None:
        super().__init__()
        self.setObjectName("header")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.setSpacing(16)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("page-title")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("header-subtitle")
        self.hint_label = QLabel("Dica: Ctrl+P abre a paleta de comandos")
        self.hint_label.setObjectName("header-hint")

        labels = QWidget()
        labels_layout = QVBoxLayout(labels)
        labels_layout.setContentsMargins(0, 0, 0, 0)
        labels_layout.setSpacing(2)
        labels_layout.addWidget(self.title_label)
        labels_layout.addWidget(self.subtitle_label)
        labels_layout.addWidget(self.hint_label)
        layout.addWidget(labels, 1)

        self.quick_actions_button = QPushButton("Acoes rapidas")
        self.quick_actions_button.setObjectName("btn-secondary")
        layout.addWidget(self.quick_actions_button, 0, Qt.AlignmentFlag.AlignRight)

        self.action_button = QPushButton("Alternar tema")
        self.action_button.setObjectName("btn-secondary")
        layout.addWidget(self.action_button, 0, Qt.AlignmentFlag.AlignRight)

        self.shortcuts_button = QPushButton("Ajuda")
        self.shortcuts_button.setObjectName("btn-ghost")
        layout.addWidget(self.shortcuts_button, 0, Qt.AlignmentFlag.AlignRight)

    def set_context(self, title: str, subtitle: str) -> None:
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)

    def set_hint(self, text: str) -> None:
        self.hint_label.setText(text)
