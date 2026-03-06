from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

from phoenix.utils.logging_config import configure_logging


def main() -> int:
    configure_logging()
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Phoenix")
    app.setOrganizationName("phoenix-personal")
    app.setApplicationVersion("2.0.0")

    assets_dir = Path(__file__).resolve().parent / "assets"
    font_path = assets_dir / "Inter-Variable.ttf"
    if font_path.exists():
        QFontDatabase.addApplicationFont(str(font_path))
        app.setFont(QFont("Inter", 13))
    else:
        app.setFont(QFont("Segoe UI", 13))

    from phoenix.core.database import init_database
    from phoenix.ui.main_window import MainWindow

    init_database()

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
