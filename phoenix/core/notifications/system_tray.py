from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


class PhoenixTray(QSystemTrayIcon):
    """System tray do Phoenix com atalhos rapidos.

    Args:
        main_window: Janela principal da aplicacao.
        app: Instancia QApplication ativa.
    """

    def __init__(self, main_window, app: QApplication):
        icon = self._create_icon()
        super().__init__(icon, app)
        self._mw = main_window
        self._streak_action = None
        self._balance_action = None
        self._build_menu()
        self.activated.connect(self._on_activated)

    def _create_icon(self) -> QIcon:
        pm = QPixmap(16, 16)
        pm.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pm)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor("#E67E22"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, 16, 16)
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            painter.drawText(pm.rect(), int(Qt.AlignmentFlag.AlignCenter), "P")
        finally:
            painter.end()
        return QIcon(pm)

    def _build_menu(self) -> None:
        menu = QMenu()
        menu.addAction("Abrir Phoenix", self._mw.show)
        menu.addSeparator()
        menu.addAction("Check de habito", self._quick_habit_check)
        menu.addAction("Nova transacao", self._quick_transaction)
        menu.addAction("Iniciar foco", self._quick_focus)
        menu.addSeparator()
        self._streak_action = menu.addAction("Streak: -")
        self._streak_action.setEnabled(False)
        self._balance_action = menu.addAction("Saldo: -")
        self._balance_action.setEnabled(False)
        menu.addSeparator()
        menu.addAction("Configuracoes", lambda: self._mw.show_settings())
        menu.addAction("Sair", QApplication.instance().quit)
        self.setContextMenu(menu)

    def update_stats(self, streak: int, balance: float) -> None:
        """Atualiza dados de streak e saldo mostrados no menu."""

        if self._streak_action is not None:
            self._streak_action.setText(f"Streak: {streak} dias")
        if self._balance_action is not None:
            self._balance_action.setText(f"Saldo: R$ {balance:,.2f}")

    def notify(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information) -> None:
        """Mostra notificacao nativa do sistema."""

        self.showMessage(title, message, icon, 4000)

    def _on_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._mw.show()
            self._mw.raise_()

    def _quick_habit_check(self) -> None:
        self._mw.quick_action("habit_check")

    def _quick_transaction(self) -> None:
        self._mw.quick_action("new_transaction")

    def _quick_focus(self) -> None:
        self._mw.quick_action("start_focus")
