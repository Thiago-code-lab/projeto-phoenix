from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from phoenix.modules.settings.controller import SettingsController


class SettingsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.controller = SettingsController()
        layout = QVBoxLayout(self)
        self.theme_label = QLabel(f"Tema atual: {self.controller.current_theme()}")
        self.backup_button = QPushButton("Exportar backup")
        self.status_label = QLabel("")
        layout.addWidget(self.theme_label)
        layout.addWidget(self.backup_button)
        layout.addWidget(self.status_label)
        self.backup_button.clicked.connect(self._backup)

    def _backup(self) -> None:
        destination = Path(__file__).resolve().parents[2] / "backup-phoenix.db"
        self.controller.export_backup(destination)
        self.status_label.setText(f"Backup salvo em {destination.name}")
