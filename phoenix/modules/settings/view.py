from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QApplication, QFileDialog, QComboBox, QLabel, QPushButton, QVBoxLayout, QWidget

from phoenix.modules.settings.controller import SettingsController
from phoenix.ui.theme import ThemeManager


class SettingsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.controller = SettingsController()
        self.theme_manager = ThemeManager()
        layout = QVBoxLayout(self)
        self.theme_label = QLabel(f"Tema atual: {self.controller.current_theme()}")
        self.theme_select = QComboBox()
        self.theme_select.addItems(["dark", "light"])
        self.theme_select.setCurrentText(self.controller.current_theme())
        self.theme_button = QPushButton("Aplicar tema")
        self.sound_button = QPushButton("Selecionar som .wav")
        self.sound_label = QLabel(self.controller.focus_sound_path() or "Som atual: padrao")
        self.backup_button = QPushButton("Exportar backup")
        self.status_label = QLabel("")
        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_select)
        layout.addWidget(self.theme_button)
        layout.addWidget(self.sound_button)
        layout.addWidget(self.sound_label)
        layout.addWidget(self.backup_button)
        layout.addWidget(self.status_label)
        self.theme_button.clicked.connect(self._apply_theme)
        self.sound_button.clicked.connect(self._select_sound)
        self.backup_button.clicked.connect(self._backup)

    def _backup(self) -> None:
        destination = Path(__file__).resolve().parents[2] / "backup-phoenix.db"
        self.controller.export_backup(destination)
        self.status_label.setText(f"Backup salvo em {destination.name}")

    def _apply_theme(self) -> None:
        theme = self.controller.set_theme(self.theme_select.currentText())
        self.theme_label.setText(f"Tema atual: {theme}")
        app = QApplication.instance()
        if app is not None:
            self.theme_manager.current_theme = theme
            self.theme_manager.apply(app)
        self.status_label.setText("Tema atualizado com sucesso.")

    def _select_sound(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Selecionar som WAV", "", "WAV (*.wav)")
        if not selected:
            return
        self.controller.set_focus_sound_path(selected)
        self.sound_label.setText(f"Som atual: {Path(selected).name}")
        self.status_label.setText("Som de foco atualizado.")
