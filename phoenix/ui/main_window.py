from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QUndoStack
from PyQt6.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from phoenix.core.cache import MemoryCache
from phoenix.core.events import EventBus
from phoenix.ui.header import Header
from phoenix.ui.sidebar import Sidebar
from phoenix.ui.theme import ThemeManager
from phoenix.ui.widgets.notification import ToastNotification
from phoenix.utils.constants import AppDefaults, Events


class MainWindow(QMainWindow):
    """Janela principal do Phoenix com carregamento sob demanda dos modulos."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(AppDefaults.APP_NAME)
        self.setMinimumSize(QSize(1100, 700))
        self.resize(1280, 800)

        self.theme = ThemeManager()
        self.event_bus = EventBus()
        self.cache = MemoryCache()
        self.undo_stack = QUndoStack(self)
        self.modules: list[tuple[str, QWidget]] = []
        self.contexts: list[tuple[str, str]] = []
        self.module_keys: list[str] = []
        self.module_factories: dict[str, Callable[[], QWidget]] = {}

        self._build_ui()
        self._bind_events()
        self._setup_shortcuts()
        self._apply_theme()
        self.navigate_to(0)

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("main")
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar_modules = [
            ("dashboard", "Dashboard"),
            ("goals", "Metas"),
            ("habits", "Habitos"),
            ("finances", "Financas"),
            ("library", "Biblioteca"),
            ("health", "Saude"),
            ("journal", "Diario"),
            ("projects", "Projetos"),
            ("focus", "Foco"),
            ("notes", "Notas"),
            ("reviews", "Revisoes"),
            ("settings", "Configuracoes"),
        ]
        self.sidebar = Sidebar(sidebar_modules, self)
        self.sidebar.navigate.connect(self.navigate_to)
        root_layout.addWidget(self.sidebar)

        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self.header = Header()
        self.header.action_button.clicked.connect(self._toggle_theme)
        self.header.shortcuts_button.clicked.connect(lambda: self.event_bus.publish(Events.SHOW_SHORTCUTS, {}))
        content_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)
        root_layout.addWidget(content, 1)

        self._configure_modules()

    def _configure_modules(self) -> None:
        self.module_keys = [
            "dashboard",
            "goals",
            "habits",
            "finances",
            "library",
            "health",
            "journal",
            "projects",
            "focus",
            "notes",
            "reviews",
            "settings",
        ]
        self.modules = [
            ("Dashboard", None),
            ("Metas", None),
            ("Habitos", None),
            ("Financas", None),
            ("Biblioteca", None),
            ("Saude", None),
            ("Diario", None),
            ("Projetos", None),
            ("Foco", None),
            ("Notas", None),
            ("Revisoes", None),
            ("Configuracoes", None),
        ]
        self.contexts = [
            ("Dashboard", "Resumo consolidado do sistema pessoal"),
            ("Metas", "Planejamento e acompanhamento por prazo"),
            ("Habitos", "Consistencia diaria e visualizacao anual"),
            ("Financas", "Contas, transacoes, orcamentos e relatorios"),
            ("Biblioteca", "Leituras, progresso e referencias"),
            ("Saude", "Metricas, energia e historico corporal"),
            ("Diario", "Entradas e reflexoes do dia"),
            ("Projetos", "Kanban operacional com prioridades"),
            ("Foco", "Pomodoro e sessoes profundas"),
            ("Notas", "Base de conhecimento local e backlinks"),
            ("Revisoes", "Radar de vida e historico de ciclos"),
            ("Configuracoes", "Preferencias, backup e dados"),
        ]
        self.module_factories = {
            "dashboard": self._load_dashboard,
            "goals": self._load_goals,
            "habits": self._load_habits,
            "finances": self._load_finances,
            "library": self._load_library,
            "health": self._load_health,
            "journal": self._load_journal,
            "projects": self._load_projects,
            "focus": self._load_focus,
            "notes": self._load_notes,
            "reviews": self._load_reviews,
            "settings": self._load_settings,
        }
        for _ in self.modules:
            self.stack.addWidget(QWidget())

    def navigate_to(self, index: int) -> None:
        if not 0 <= index < len(self.modules):
            return
        widget = self._ensure_module_loaded(index)
        previous = self.stack.widget(index)
        if previous is not widget:
            self.stack.removeWidget(previous)
            previous.deleteLater()
            self.stack.insertWidget(index, widget)
        self.stack.setCurrentIndex(index)
        title, subtitle = self.contexts[index]
        self.header.set_context(title, subtitle)
        self.sidebar.set_active(index)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _setup_shortcuts(self) -> None:
        for index in range(min(9, len(self.module_keys))):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{index + 1}"), self)
            shortcut.activated.connect(lambda idx=index: self.navigate_to(idx))
        QShortcut(QKeySequence("Ctrl+/"), self, activated=lambda: self.event_bus.publish(Events.SHOW_SHORTCUTS, {}))

    def _apply_theme(self) -> None:
        app = QApplication.instance()
        if app is not None:
            self.theme.apply(app)

    def _bind_events(self) -> None:
        self.event_bus.subscribe(Events.NAVIGATE, lambda payload: self.navigate_to(int(payload.get("index", 0))))
        self.event_bus.subscribe(Events.SHOW_TOAST, self._show_toast)
        self.event_bus.subscribe(Events.SHOW_SHORTCUTS, lambda _: self._show_shortcuts())
        self.event_bus.subscribe(Events.DATA_CHANGED, lambda _: self.cache.invalidate("module:"))

    def _ensure_module_loaded(self, index: int) -> QWidget:
        current = self.modules[index][1]
        if current is not None:
            return current
        key = self.module_keys[index]
        widget = self.cache.get_or_set(f"module:{key}", self.module_factories[key])
        self.modules[index] = (self.modules[index][0], widget)
        return widget  # type: ignore[return-value]

    def _show_toast(self, payload: dict[str, object]) -> None:
        toast = ToastNotification(str(payload.get("message", "Operacao concluida")), self)
        toast.show_centered()

    def _show_shortcuts(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Atalhos")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Ctrl+1..9: navegar entre modulos"))
        layout.addWidget(QLabel("Ctrl+/: abrir painel de atalhos"))
        layout.addWidget(QLabel("Ctrl+Shift+F: buscar nas notas"))
        layout.addWidget(QLabel("Ctrl+1 carrega Dashboard sem abrir modulos antes do acesso"))
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.resize(420, 220)
        dialog.exec()

    def _load_dashboard(self) -> QWidget:
        from phoenix.modules.dashboard.view import DashboardView

        return DashboardView(event_bus=self.event_bus, parent=self)

    def _load_goals(self) -> QWidget:
        from phoenix.modules.goals.view import GoalsView

        return GoalsView()

    def _load_habits(self) -> QWidget:
        from phoenix.modules.habits.view import HabitsView

        return HabitsView()

    def _load_finances(self) -> QWidget:
        from phoenix.modules.finances.view import FinancesView

        return FinancesView(self.event_bus)

    def _load_library(self) -> QWidget:
        from phoenix.modules.library.view import LibraryView

        return LibraryView()

    def _load_health(self) -> QWidget:
        from phoenix.modules.health.view import HealthView

        return HealthView()

    def _load_journal(self) -> QWidget:
        from phoenix.modules.journal.view import JournalView

        return JournalView()

    def _load_projects(self) -> QWidget:
        from phoenix.modules.projects.view import ProjectsView

        return ProjectsView()

    def _load_focus(self) -> QWidget:
        from phoenix.modules.focus.view import FocusView

        return FocusView()

    def _load_notes(self) -> QWidget:
        from phoenix.modules.notes.view import NotesView

        return NotesView()

    def _load_reviews(self) -> QWidget:
        from phoenix.modules.reviews.view import ReviewsView

        return ReviewsView()

    def _load_settings(self) -> QWidget:
        from phoenix.modules.settings.view import SettingsView

        return SettingsView()

    def _toggle_theme(self) -> None:
        app = QApplication.instance()
        if app is not None:
            self.theme.toggle(app)
            self.event_bus.publish(Events.SHOW_TOAST, {"message": "Tema atualizado."})
