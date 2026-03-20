from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QProgressBar, QVBoxLayout

from phoenix import __version__
from phoenix.core.backup import auto_backup_if_due
from phoenix.core.database import init_database, run_integrity_check
from phoenix.utils.logging_config import configure_logging


class StartupSplash(QDialog):
    """Splash screen de inicializacao com progresso por etapa."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setModal(False)
        self.setFixedSize(520, 220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        self.title = QLabel(f"Phoenix {__version__}")
        self.title.setStyleSheet("font-size: 24px; font-weight: 700;")
        self.subtitle = QLabel("Inicializando ambiente...")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addStretch(1)
        layout.addWidget(self.progress)

    def update_step(self, value: int, text: str) -> None:
        """Atualiza etapa visivel de bootstrap.

        Args:
            value: Progresso percentual atual.
            text: Descricao curta da etapa executada.
        """

        self.progress.setValue(value)
        self.subtitle.setText(text)
        QApplication.processEvents()


def main() -> int:
    configure_logging()
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Phoenix")
    app.setOrganizationName("phoenix-personal")
    app.setApplicationVersion(__version__)

    splash = StartupSplash()
    splash.show()
    splash.update_step(10, "Carregando configuracoes...")

    assets_dir = Path(__file__).resolve().parent / "assets"
    font_path = assets_dir / "Inter-Variable.ttf"
    if font_path.exists():
        QFontDatabase.addApplicationFont(str(font_path))
        app.setFont(QFont("Inter", 13))
    else:
        app.setFont(QFont("Segoe UI", 13))

    splash.update_step(35, "Inicializando banco...")
    init_database()
    splash.update_step(55, "Executando health check do banco...")
    run_integrity_check()
    splash.update_step(70, "Verificando backup automatico...")
    auto_backup_if_due(interval_hours=24, keep_last=7)
    splash.update_step(85, "Carregando interface...")

    from phoenix.ui.main_window import MainWindow

    window = MainWindow()
    window.show()
    splash.update_step(100, "Pronto")
    splash.close()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
