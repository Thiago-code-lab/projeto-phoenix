from __future__ import annotations

from datetime import datetime
from difflib import SequenceMatcher
from typing import Callable

from PyQt6.QtCore import QEasingCurve, QSize, QPropertyAnimation, QTimer, Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QUndoStack
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QGraphicsOpacityEffect,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from phoenix import __version__
from phoenix.core.cache import MemoryCache
from phoenix.core.database import database_size_mb
from phoenix.core.events import EventBus
from phoenix.ui.header import Header
from phoenix.ui.sidebar import Sidebar
from phoenix.ui.theme import ThemeManager
from phoenix.ui.widgets.notification import ToastNotification
from phoenix.utils.constants import AppDefaults, Events


class SkeletonPage(QWidget):
    """Placeholder visual simples enquanto o modulo e carregado."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)
        self._bars: list[QLabel] = []
        for width in (260, 420, 360, 520):
            bar = QLabel()
            bar.setFixedHeight(18)
            bar.setMaximumWidth(width)
            bar.setStyleSheet("background: #3f3f46; border-radius: 8px;")
            layout.addWidget(bar)
            self._bars.append(bar)
        layout.addStretch(1)
        self._pulse_state = False
        self._timer = QTimer(self)
        self._timer.setInterval(320)
        self._timer.timeout.connect(self._pulse)
        self._timer.start()

    def _pulse(self) -> None:
        self._pulse_state = not self._pulse_state
        color = "#52525b" if self._pulse_state else "#3f3f46"
        for bar in self._bars:
            bar.setStyleSheet(f"background: {color}; border-radius: 8px;")


class CommandPaletteDialog(QDialog):
    """Paleta de comandos global com busca fuzzy basica."""

    def __init__(self, actions: list[tuple[str, Callable[[], None]]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Command Palette")
        self.setModal(True)
        self.resize(560, 420)
        self._actions = actions

        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Digite para buscar modulos e acoes...")
        self.listing = QListWidget()
        layout.addWidget(self.search)
        layout.addWidget(self.listing, 1)

        self.search.textChanged.connect(self._refresh)
        self.listing.itemActivated.connect(self._activate)
        self._refresh("")

    def _score(self, query: str, text: str) -> float:
        if not query:
            return 1.0
        query_norm = query.lower().strip()
        text_norm = text.lower()
        if query_norm in text_norm:
            return 1.0 + (len(query_norm) / max(len(text_norm), 1))
        return SequenceMatcher(None, query_norm, text_norm).ratio()

    def _refresh(self, query: str) -> None:
        self.listing.clear()
        ranked = sorted(
            ((self._score(query, label), index, label) for index, (label, _) in enumerate(self._actions)),
            reverse=True,
        )
        appended = 0
        for score, index, label in ranked[:20]:
            if query.strip() and score < 0.32:
                continue
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.listing.addItem(item)
            appended += 1
        if appended == 0:
            no_result = QListWidgetItem("Sem resultados para a busca")
            no_result.setFlags(Qt.ItemFlag.NoItemFlags)
            self.listing.addItem(no_result)
            return
        if self.listing.count() > 0:
            self.listing.setCurrentRow(0)

    def _activate(self, item: QListWidgetItem) -> None:
        index = int(item.data(Qt.ItemDataRole.UserRole))
        _, callback = self._actions[index]
        callback()
        self.accept()


class MainWindow(QMainWindow):
    """Janela principal do Phoenix com carregamento sob demanda dos modulos."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{AppDefaults.APP_NAME} {__version__}")
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
        self.module_hints: dict[str, str] = {}
        self._animations: list[QPropertyAnimation] = []
        self._last_saved = "-"
        self._db_usage_label = QLabel("DB: 0.00 MB")
        self._active_module_label = QLabel("Modulo: -")
        self._last_saved_label = QLabel("Ultimo salvamento: -")

        self._build_ui()
        self._bind_events()
        self._setup_shortcuts()
        self._setup_status_bar()
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
        self.header.quick_actions_button.setToolTip("Abrir a paleta de comandos (Ctrl+P)")
        self.header.quick_actions_button.clicked.connect(self._open_command_palette)
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
        self.module_hints = {
            "dashboard": "Comece pelo resumo do dia e identifique prioridades.",
            "goals": "Defina uma meta com prazo e acompanhe milestones.",
            "habits": "Marque o progresso diario para fortalecer seu streak.",
            "finances": "Importe CSV/OFX e acompanhe fluxo mensal.",
            "library": "Atualize paginas lidas e status para manter ritmo.",
            "health": "Registre peso, sono e agua em menos de 1 minuto.",
            "journal": "Escreva uma entrada curta e deixe o autosave trabalhar.",
            "projects": "Organize tarefas no Kanban por prioridade.",
            "focus": "Escolha uma tarefa e inicie um ciclo de foco 25/50/90.",
            "notes": "Capture ideias e relacione notas com tags.",
            "reviews": "Faça uma revisao semanal para ajustar sua rota.",
            "settings": "Personalize tema, som e backup do aplicativo.",
        }
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
            self.stack.addWidget(SkeletonPage())

    def navigate_to(self, index: int) -> None:
        if not 0 <= index < len(self.modules):
            return
        previous_index = self.stack.currentIndex()
        widget = self._ensure_module_loaded(index)
        previous = self.stack.widget(index)
        if previous is not widget:
            self.stack.removeWidget(previous)
            previous.deleteLater()
            self.stack.insertWidget(index, widget)
        self.stack.setCurrentIndex(index)
        if previous_index != index:
            self._animate_current_module(widget)
        title, subtitle = self.contexts[index]
        self.header.set_context(title, subtitle)
        module_key = self.module_keys[index]
        self.header.set_hint(self.module_hints.get(module_key, "Dica: Ctrl+P abre a paleta de comandos"))
        self.sidebar.set_active(index)
        self._active_module_label.setText(f"Modulo: {title}")
        self._refresh_db_usage()
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _setup_shortcuts(self) -> None:
        for index in range(min(9, len(self.module_keys))):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{index + 1}"), self)
            shortcut.activated.connect(lambda idx=index: self.navigate_to(idx))
        QShortcut(QKeySequence("Ctrl+/"), self, activated=lambda: self.event_bus.publish(Events.SHOW_SHORTCUTS, {}))
        QShortcut(QKeySequence("Ctrl+P"), self, activated=self._open_command_palette)
        QShortcut(QKeySequence("F1"), self, activated=lambda: self.event_bus.publish(Events.SHOW_SHORTCUTS, {}))

    def _apply_theme(self) -> None:
        app = QApplication.instance()
        if app is not None:
            self.theme.apply(app)

    def _bind_events(self) -> None:
        self.event_bus.subscribe(Events.NAVIGATE, lambda payload: self.navigate_to(int(payload.get("index", 0))))
        self.event_bus.subscribe(Events.SHOW_TOAST, self._show_toast)
        self.event_bus.subscribe(Events.SHOW_SHORTCUTS, lambda _: self._show_shortcuts())
        self.event_bus.subscribe(Events.DATA_CHANGED, self._on_data_changed)

    def _ensure_module_loaded(self, index: int) -> QWidget:
        current = self.modules[index][1]
        if current is not None:
            return current
        key = self.module_keys[index]
        widget = self.cache.get_or_set(f"module:{key}", self.module_factories[key])
        self.modules[index] = (self.modules[index][0], widget)
        return widget  # type: ignore[return-value]

    def _show_toast(self, payload: dict[str, object]) -> None:
        raw_message = str(payload.get("message", "Operacao concluida"))
        kind = str(payload.get("kind", "info"))
        message = raw_message
        if raw_message.startswith("[") and "]" in raw_message:
            maybe_kind, rest = raw_message.split("]", 1)
            extracted = maybe_kind.strip("[]").lower().strip()
            if extracted in {"info", "success", "warning", "error"}:
                kind = extracted
                message = rest.strip()
        toast = ToastNotification(message, kind=kind, parent=self)
        toast.show_bottom_right()

    def _show_shortcuts(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Atalhos")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Ctrl+1..9: navegar entre modulos"))
        layout.addWidget(QLabel("Ctrl+P: abrir paleta de comandos"))
        layout.addWidget(QLabel("Ctrl+/: abrir painel de atalhos"))
        layout.addWidget(QLabel("F1: ajuda rapida"))
        layout.addWidget(QLabel("Dica: passe o mouse sobre itens laterais para ver contexto"))
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

    def _setup_status_bar(self) -> None:
        bar = self.statusBar()
        bar.addPermanentWidget(self._active_module_label)
        bar.addPermanentWidget(self._last_saved_label)
        bar.addPermanentWidget(self._db_usage_label)
        self._refresh_db_usage()
        self._status_timer = QTimer(self)
        self._status_timer.setInterval(30000)
        self._status_timer.timeout.connect(self._refresh_db_usage)
        self._status_timer.start()

    def _refresh_db_usage(self) -> None:
        self._db_usage_label.setText(f"DB: {database_size_mb():.2f} MB")

    def _on_data_changed(self, _: dict[str, object]) -> None:
        self.cache.invalidate("module:")
        self._last_saved = datetime.now().strftime("%H:%M:%S")
        self._last_saved_label.setText(f"Ultimo salvamento: {self._last_saved}")
        self._refresh_db_usage()

    def _open_command_palette(self) -> None:
        actions: list[tuple[str, Callable[[], None]]] = []
        for index, (title, _) in enumerate(self.modules):
            actions.append((f"Ir para: {title}", lambda idx=index: self.navigate_to(idx)))
        actions.append(("Acao: Ir para Dashboard", lambda: self.navigate_to(0)))
        actions.append(("Acao: Recarregar modulo atual", lambda: self.navigate_to(self.stack.currentIndex())))
        actions.append(("Acao: Alternar tema", self._toggle_theme))
        actions.append(("Acao: Atalhos", lambda: self.event_bus.publish(Events.SHOW_SHORTCUTS, {})))
        actions.append(("Acao: Sobre o Phoenix", self._show_about))
        dialog = CommandPaletteDialog(actions, self)
        dialog.exec()

    def _animate_current_module(self, widget: QWidget) -> None:
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(220)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        def cleanup() -> None:
            widget.setGraphicsEffect(None)
            if animation in self._animations:
                self._animations.remove(animation)

        animation.finished.connect(cleanup)
        self._animations.append(animation)
        animation.start()

    def _show_about(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Sobre")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Phoenix {__version__}"))
        layout.addWidget(QLabel("Aplicacao local-first para gestao pessoal."))
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec()
