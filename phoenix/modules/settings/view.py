from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QComboBox,
)

from phoenix.core.theme_engine import ThemeEngine
from phoenix.modules.settings.controller import SettingsController


class SettingsView(QWidget):
    COLOR_KEYS = [
        "PRIMARY",
        "SECONDARY",
        "ACCENT",
        "BG_ROOT",
        "BG_SURFACE",
        "BG_ELEVATED",
        "BORDER",
        "BORDER_HOVER",
        "TEXT_PRIMARY",
        "TEXT_SECONDARY",
        "TEXT_HINT",
    ]

    SIZE_KEYS = [
        "RADIUS_SM",
        "RADIUS_MD",
        "RADIUS_LG",
        "SPACING_SM",
        "SPACING_MD",
        "SPACING_LG",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.controller = SettingsController()
        app = QApplication.instance()
        if app is not None:
            ThemeEngine.instance().set_app(app)

        self._color_inputs: dict[str, QLineEdit] = {}
        self._size_inputs: dict[str, QLineEdit] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        title = QLabel("Personalizacao visual")
        title.setObjectName("label-title")
        root.addWidget(title)

        self.status_label = QLabel("")
        self.status_label.setObjectName("label-muted")

        root.addWidget(self._build_preset_group())
        root.addWidget(self._build_colors_group())
        root.addWidget(self._build_layout_group())
        root.addWidget(self._build_font_group())
        root.addWidget(self._build_misc_group())

        root.addWidget(self.status_label)
        root.addStretch(1)

        self._load_from_current_theme()

    def _build_preset_group(self) -> QGroupBox:
        group = QGroupBox("Presets")
        row = QHBoxLayout(group)

        self.preset_select = QComboBox()
        self.preset_select.addItems(self.controller.available_presets())

        self.apply_preset_btn = QPushButton("Aplicar preset")
        self.apply_preset_btn.setObjectName("btn-secondary")
        self.apply_preset_btn.clicked.connect(self._apply_preset)

        self.apply_custom_btn = QPushButton("Aplicar customizacao")
        self.apply_custom_btn.setObjectName("btn-primary")
        self.apply_custom_btn.clicked.connect(self._apply_custom)

        row.addWidget(QLabel("Preset:"))
        row.addWidget(self.preset_select)
        row.addWidget(self.apply_preset_btn)
        row.addStretch(1)
        row.addWidget(self.apply_custom_btn)
        return group

    def _build_colors_group(self) -> QGroupBox:
        group = QGroupBox("Cores")
        grid = QGridLayout(group)

        for index, key in enumerate(self.COLOR_KEYS):
            label = QLabel(key)
            field = QLineEdit()
            field.setPlaceholderText("#RRGGBB")
            field.setObjectName("theme-color-input")
            self._color_inputs[key] = field
            grid.addWidget(label, index // 2, (index % 2) * 2)
            grid.addWidget(field, index // 2, (index % 2) * 2 + 1)

        return group

    def _build_layout_group(self) -> QGroupBox:
        group = QGroupBox("Raios e espacamentos")
        form = QFormLayout(group)

        for key in self.SIZE_KEYS:
            field = QLineEdit()
            self._size_inputs[key] = field
            form.addRow(key, field)

        return group

    def _build_font_group(self) -> QGroupBox:
        group = QGroupBox("Tipografia")
        row = QHBoxLayout(group)

        self.font_family = QLineEdit()
        self.font_family.setPlaceholderText("Segoe UI")

        self.font_size = QSpinBox()
        self.font_size.setRange(9, 28)

        row.addWidget(QLabel("Fonte"))
        row.addWidget(self.font_family, 1)
        row.addWidget(QLabel("Tamanho"))
        row.addWidget(self.font_size)
        return group

    def _build_misc_group(self) -> QGroupBox:
        group = QGroupBox("Outras configuracoes")
        row = QHBoxLayout(group)

        self.theme_label = QLabel(f"Tema atual: {self.controller.current_theme()}")
        self.sound_button = QPushButton("Selecionar som .wav")
        self.sound_button.setObjectName("btn-secondary")
        self.sound_label = QLabel(self.controller.focus_sound_path() or "Som atual: padrao")
        self.backup_button = QPushButton("Exportar backup")
        self.backup_button.setObjectName("btn-secondary")

        self.sound_button.clicked.connect(self._select_sound)
        self.backup_button.clicked.connect(self._backup)

        row.addWidget(self.theme_label)
        row.addStretch(1)
        row.addWidget(self.sound_button)
        row.addWidget(self.sound_label)
        row.addWidget(self.backup_button)
        return group

    def _load_from_current_theme(self) -> None:
        theme = self.controller.get_theme()
        self.theme_label.setText(f"Tema atual: {theme.get('name', 'custom')}")
        if str(theme.get("name", "")) in self.controller.available_presets():
            self.preset_select.setCurrentText(str(theme.get("name")))

        for key, field in self._color_inputs.items():
            field.setText(str(theme.get(key, "")))
        for key, field in self._size_inputs.items():
            field.setText(str(theme.get(key, "")))

        self.font_family.setText(str(theme.get("font_family", "Segoe UI")))
        self.font_size.setValue(int(theme.get("font_size", 13)))

    def _build_theme_payload(self) -> dict[str, str | int]:
        payload: dict[str, str | int] = {
            "name": "custom",
            "font_family": self.font_family.text().strip() or "Segoe UI",
            "font_size": int(self.font_size.value()),
        }

        for key, field in self._color_inputs.items():
            value = field.text().strip().upper()
            if not value:
                continue
            payload[key] = value

        for key, field in self._size_inputs.items():
            value = field.text().strip()
            if not value:
                continue
            payload[key] = value

        return payload

    def _apply_preset(self) -> None:
        theme = self.controller.apply_preset(self.preset_select.currentText())
        self._load_from_current_theme()
        self.status_label.setText(f"Preset aplicado: {theme.get('name', 'custom')}")

    def _apply_custom(self) -> None:
        payload = self._build_theme_payload()
        theme = self.controller.apply_custom_theme(payload)
        self.theme_label.setText(f"Tema atual: {theme.get('name', 'custom')}")
        self.status_label.setText("Tema customizado aplicado e salvo.")

    def _backup(self) -> None:
        destination = Path(__file__).resolve().parents[2] / "backup-phoenix.db"
        self.controller.export_backup(destination)
        self.status_label.setText(f"Backup salvo em {destination.name}")

    def _select_sound(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Selecionar som WAV", "", "WAV (*.wav)")
        if not selected:
            return
        self.controller.set_focus_sound_path(selected)
        self.sound_label.setText(f"Som atual: {Path(selected).name}")
        self.status_label.setText("Som de foco atualizado.")
