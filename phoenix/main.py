from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QDialog, QGraphicsOpacityEffect, QLabel, QVBoxLayout

from phoenix import __version__
from phoenix.core.backup import auto_backup_if_due
from phoenix.core.database import get_session, init_database, run_integrity_check
from phoenix.core.profiles.manager import ProfileManager
from phoenix.core.theme_engine import ThemeEngine
from phoenix.ui.onboarding.onboarding_seed import run_seed
from phoenix.ui.onboarding.onboarding_wizard import OnboardingWizard, is_first_run
from phoenix.ui.profile_select_dialog import ProfileSelectDialog
from phoenix.ui.widgets.gradient_progress import GradientProgressBar
from phoenix.utils.logging_config import configure_logging


class GradientTitleLabel(QLabel):
    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor("#C0392B"))
        gradient.setColorAt(1.0, QColor("#F39C12"))
        pen = QPen(gradient, 1)
        painter.setPen(pen)
        painter.setFont(self.font())
        painter.drawText(self.rect(), int(Qt.AlignmentFlag.AlignCenter), self.text())


class StartupSplash(QDialog):
    """Splash screen de inicializacao com progresso por etapa."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setModal(False)
        self.setFixedSize(620, 280)
        self.setStyleSheet("background: #0D0D0D; border: 1px solid #1E1E1E; border-radius: 16px;")

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 24)
        layout.setSpacing(8)

        self.title = GradientTitleLabel("PHOENIX")
        self.title.setStyleSheet("font-size: 48px; font-weight: 700;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version = QLabel("2.0")
        self.version.setStyleSheet("font-size: 14px; color: #666666;")
        self.version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle = QLabel("Inicializando ambiente...")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("color: #AAAAAA;")
        self.progress = GradientProgressBar()
        self.progress.setValue(0)

        layout.addWidget(self.title)
        layout.addWidget(self.version)
        layout.addWidget(self.subtitle)
        layout.addStretch(1)
        layout.addWidget(self.progress)

        self._fade_in = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_in.setDuration(400)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._fade_out = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_out.setDuration(300)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self._fade_in.start()

    def update_step(self, value: int, text: str) -> None:
        """Atualiza etapa visivel de bootstrap.

        Args:
            value: Progresso percentual atual.
            text: Descricao curta da etapa executada.
        """

        self.progress.setValue(value)
        self.subtitle.setText(text)
        QApplication.processEvents()

    def close_with_fade(self) -> None:
        def _close() -> None:
            self.close()

        self._fade_out.finished.connect(_close)
        self._fade_out.start()


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

    theme_engine = ThemeEngine.instance()
    theme_engine.set_app(app)
    theme_engine.apply(theme_engine.load_saved())

    splash.update_step(35, "Inicializando banco...")
    init_database()
    splash.update_step(55, "Executando health check do banco...")
    run_integrity_check()
    splash.update_step(70, "Verificando backup automatico...")
    auto_backup_if_due(interval_hours=24, keep_last=7)
    splash.update_step(85, "Preparando interface...")

    manager = ProfileManager()
    profiles = manager.list_profiles()
    if len(profiles) == 0:
        manager.create_profile("Padrao", "#E67E22")
        profile = manager.list_profiles()[0]
    elif len(profiles) == 1 and not profiles[0].get("pin_hash"):
        profile = profiles[0]
    else:
        selector = ProfileSelectDialog(profiles)
        if selector.exec() != QDialog.DialogCode.Accepted:
            return 0
        selected = selector.selected_profile()
        if selected is None:
            return 0
        profile = selected
    manager.switch_profile(profile)

    should_onboard = False
    with get_session() as session:
        should_onboard = is_first_run(session)

    if should_onboard:
        splash.close_with_fade()
        app.processEvents()
        wizard = OnboardingWizard()
        if wizard.exec() == QDialog.DialogCode.Accepted:
            with get_session() as session:
                run_seed(wizard.get_data(), session)

    splash.update_step(92, "Carregando interface...")

    from phoenix.ui.main_window import MainWindow

    window = MainWindow()
    window.show()
    splash.update_step(100, "Pronto")
    splash.close_with_fade()
    app.processEvents()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
