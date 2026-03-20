from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.profiles.manager import ProfileManager


class ProfileSelectDialog(QDialog):
    """Dialogo de selecao de perfil com suporte opcional a PIN."""

    def __init__(self, profiles: list[dict], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Selecionar perfil")
        self.resize(520, 360)
        self._profiles = profiles
        self._selected: dict | None = None
        self._manager = ProfileManager()

        root = QVBoxLayout(self)
        grid = QGridLayout()
        for idx, profile in enumerate(self._profiles):
            button = QPushButton(profile.get("name", "Perfil"))
            button.clicked.connect(lambda _, p=profile: self._choose(p))
            grid.addWidget(button, idx // 2, idx % 2)
        root.addLayout(grid)

        footer = QHBoxLayout()
        create_btn = QPushButton("+ Novo perfil")
        create_btn.clicked.connect(self._create_profile)
        footer.addStretch(1)
        footer.addWidget(create_btn)
        root.addLayout(footer)

    def _choose(self, profile: dict) -> None:
        if profile.get("pin_hash"):
            pin, ok = PINDialog.request(self)
            if not ok or not self._manager.verify_pin(profile, pin):
                QMessageBox.warning(self, "PIN", "PIN incorreto")
                return
        self._selected = profile
        self.accept()

    def _create_profile(self) -> None:
        name, ok = TextPrompt.request(self, "Nome do perfil")
        if not ok or not name.strip():
            return
        profile = self._manager.create_profile(name.strip())
        self._selected = profile
        self.accept()

    def selected_profile(self) -> dict | None:
        return self._selected


class TextPrompt(QDialog):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        self.input = QLineEdit()
        layout.addWidget(self.input)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

    @staticmethod
    def request(parent: QWidget, title: str) -> tuple[str, bool]:
        dialog = TextPrompt(title, parent)
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        return dialog.input.text(), accepted


class PINDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PIN")
        layout = QVBoxLayout(self)
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Digite o PIN"))
        layout.addWidget(self.input)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

    @staticmethod
    def request(parent: QWidget) -> tuple[str, bool]:
        dialog = PINDialog(parent)
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        return dialog.input.text(), accepted
