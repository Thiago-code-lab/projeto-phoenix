from __future__ import annotations

from datetime import datetime
from typing import Callable

from PyQt6.QtCore import QEasingCurve, QEvent, QPoint, QSize, QPropertyAnimation, QSequentialAnimationGroup, QTimer, Qt
from PyQt6.QtGui import QColor, QKeySequence, QShortcut, QUndoStack
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QLabel,
    QLayout,
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
from phoenix.core.database import SessionLocal
from phoenix.core.database import database_size_mb
from phoenix.core.events import EventBus
from phoenix.core.native_bridge import fuzzy_search
from phoenix.core.notifications.scheduler import ReminderScheduler
from phoenix.core.notifications.system_tray import PhoenixTray
from phoenix.modules.assistant.view import PhoenixAssistantPanel
from phoenix.ui.header import Header
from phoenix.ui.sidebar import Sidebar
from phoenix.ui.theme import ThemeManager, apply_theme
from phoenix.ui.widgets.notification import ToastNotification
from phoenix.utils.constants import AppDefaults, Events


class PrimaryButtonRippleFilter(QWidget):
    """Event filter para ripple simples em botoes primarios."""

    def eventFilter(self, watched: object, event: QEvent) -> bool:
        if isinstance(watched, QPushButton) and watched.objectName() == "btn-primary":
            if event.type() == QEvent.Type.MouseButtonPress:
                self._run_ripple(watched, event.position().toPoint())
        return super().eventFilter(watched, event)

    def _run_ripple(self, button: QPushButton, center: QPoint) -> None:
        ripple = QLabel(button)
        ripple.setStyleSheet("background: rgba(255,255,255,0.3); border-radius: 30px;")
        ripple.setFixedSize(0, 0)
        ripple.move(center.x(), center.y())
        ripple.show()

        grow = QPropertyAnimation(ripple, b"geometry", button)
        grow.setDuration(220)
        grow.setStartValue(ripple.geometry())
        grow.setEndValue(ripple.geometry().adjusted(-30, -30, 30, 30))
        grow.setEasingCurve(QEasingCurve.Type.OutCubic)

        fade = QPropertyAnimation(ripple, b"windowOpacity", button)
        fade.setDuration(220)
        fade.setStartValue(0.3)
        fade.setEndValue(0.0)

        group = QSequentialAnimationGroup(button)
        group.addAnimation(grow)
        group.addAnimation(fade)
        group.finished.connect(ripple.deleteLater)
        group.start()


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

    def _refresh(self, query: str) -> None:
        self.listing.clear()
        labels = [label for label, _ in self._actions]
        if query.strip():
            ranked_native = fuzzy_search(query, labels, 20)
            ranked = [(score, index, labels[index]) for index, score in ranked_native]
        else:
            ranked = [(1.0, index, label) for index, label in enumerate(labels[:20])]
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
        self._transitioning = False
        self._last_saved = "-"
        self._db_usage_label = QLabel("DB: 0.00 MB")
        self._active_module_label = QLabel("Modulo: -")
        self._last_saved_label = QLabel("Ultimo salvamento: -")
        self._sep_one = QLabel("│")
        self._sep_two = QLabel("│")
        self._ripple_filter = PrimaryButtonRippleFilter(self)
        self._assistant_panel: PhoenixAssistantPanel | None = None
        self._session = SessionLocal()
        self._tray: PhoenixTray | None = None
        self._scheduler: ReminderScheduler | None = None

        self._build_ui()
        self._bind_events()
        self._setup_shortcuts()
        self._setup_status_bar()
        self._setup_assistant_panel()
        self._setup_tray_and_scheduler()
        self._apply_theme()
        self._install_ripple_effects()
        self.navigate_to(0)

    def _setup_tray_and_scheduler(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        self._tray = PhoenixTray(self, app)
        self._tray.show()
        self._scheduler = ReminderScheduler(self._session, self)
        self._scheduler.reminder_triggered.connect(self._on_reminder)

    def _on_reminder(self, title: str, message: str) -> None:
        if self._tray is not None:
            self._tray.notify(title, message)
        self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[info] {title}: {message}"})

    def show_settings(self) -> None:
        if "settings" in self.module_keys:
            self.navigate_to(self.module_keys.index("settings"))

    def quick_action(self, action: str) -> None:
        if action == "habit_check":
            self.navigate_to(self.module_keys.index("habits"))
        elif action == "new_transaction":
            self.navigate_to(self.module_keys.index("finances"))
        elif action == "start_focus":
            self.navigate_to(self.module_keys.index("focus"))

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._tray is None:
            super().closeEvent(event)
            return
        event.ignore()
        self.hide()
        self._tray.notify("Phoenix", "Minimizado para a bandeja do sistema.")

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
            ("achievements", "Conquistas"),
            ("analytics", "Analytics"),
            ("settings", "Configuracoes"),
        ]
        self.sidebar = Sidebar(sidebar_modules, self)
        self.sidebar.navigate.connect(self.navigate_to)
        sidebar_shadow = QGraphicsDropShadowEffect(self.sidebar)
        sidebar_shadow.setBlurRadius(32)
        sidebar_shadow.setColor(QColor(0, 0, 0, 180))
        sidebar_shadow.setOffset(4, 0)
        self.sidebar.setGraphicsEffect(sidebar_shadow)
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
            "achievements",
            "analytics",
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
            ("Conquistas", None),
            ("Analytics", None),
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
            ("Conquistas", "Progresso, niveis e badges desbloqueadas"),
            ("Analytics", "Pontuacao de vida e relatorio consolidado"),
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
            "achievements": "Acompanhe seu XP, nivel e conquistas desbloqueadas.",
            "analytics": "Avalie seu score de vida e gere relatorios mensais.",
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
            "achievements": self._load_achievements,
            "analytics": self._load_analytics,
            "settings": self._load_settings,
        }
        for _ in self.modules:
            self.stack.addWidget(SkeletonPage())

    def navigate_to(self, index: int) -> None:
        if not 0 <= index < len(self.modules) or self._transitioning:
            return
        previous_index = self.stack.currentIndex()
        widget = self._ensure_module_loaded(index)
        previous = self.stack.widget(index)
        if previous is not widget:
            self.stack.removeWidget(previous)
            previous.deleteLater()
            self.stack.insertWidget(index, widget)
        if previous_index != index:
            self._cross_dissolve_to(index)
        else:
            self.stack.setCurrentIndex(index)
        title, subtitle = self.contexts[index]
        self.header.set_context(title, subtitle)
        module_key = self.module_keys[index]
        self.header.set_hint(self.module_hints.get(module_key, "Dica: Ctrl+P abre a paleta de comandos"))
        self.sidebar.set_active(index)
        self._active_module_label.setText(f"Modulo: {title}")
        self._refresh_db_usage()
        self._apply_module_defaults(widget)
        self._install_ripple_effects(widget)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _setup_shortcuts(self) -> None:
        for index in range(min(9, len(self.module_keys))):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{index + 1}"), self)
            shortcut.activated.connect(lambda idx=index: self.navigate_to(idx))
        QShortcut(QKeySequence("Ctrl+/"), self, activated=lambda: self.event_bus.publish(Events.SHOW_SHORTCUTS, {}))
        QShortcut(QKeySequence("Ctrl+P"), self, activated=self._open_command_palette)
        QShortcut(QKeySequence("Ctrl+A"), self, activated=self._toggle_assistant_panel)
        QShortcut(QKeySequence("F1"), self, activated=lambda: self.event_bus.publish(Events.SHOW_SHORTCUTS, {}))

    def _setup_assistant_panel(self) -> None:
        self._assistant_panel = PhoenixAssistantPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._assistant_panel)
        self._assistant_panel.hide()

    def _toggle_assistant_panel(self) -> None:
        if self._assistant_panel is None:
            return
        if self._assistant_panel.isVisible():
            self._assistant_panel.hide()
            return
        self._assistant_panel.show()

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
        apply_theme(dialog)
        dialog.setWindowTitle("Atalhos")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Ctrl+1..9: navegar entre modulos"))
        layout.addWidget(QLabel("Ctrl+P: abrir paleta de comandos"))
        layout.addWidget(QLabel("Ctrl+/: abrir painel de atalhos"))
        layout.addWidget(QLabel("F1: ajuda rapida"))
        layout.addWidget(QLabel("Dica: passe o mouse sobre itens laterais para ver contexto"))
        close_button = QPushButton("Fechar")
        close_button.setObjectName("btn-ghost")
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
        from phoenix.modules.diary.view import DiaryView

        return DiaryView(self.event_bus)

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

    def _load_analytics(self) -> QWidget:
        from phoenix.modules.analytics.view import AnalyticsView

        return AnalyticsView()

    def _load_achievements(self) -> QWidget:
        from phoenix.modules.achievements.view import AchievementsView

        return AchievementsView()

    def _toggle_theme(self) -> None:
        app = QApplication.instance()
        if app is not None:
            self.theme.toggle(app)
            self.event_bus.publish(Events.SHOW_TOAST, {"message": "Tema atualizado."})

    def _setup_status_bar(self) -> None:
        bar = self.statusBar()
        self._sep_one.setStyleSheet("color: #2A2A2A;")
        self._sep_two.setStyleSheet("color: #2A2A2A;")
        bar.addPermanentWidget(self._active_module_label)
        bar.addPermanentWidget(self._sep_one)
        bar.addPermanentWidget(self._last_saved_label)
        bar.addPermanentWidget(self._sep_two)
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

    def _cross_dissolve_to(self, next_index: int) -> None:
        current_widget = self.stack.currentWidget()
        if current_widget is None:
            self.stack.setCurrentIndex(next_index)
            return

        self._transitioning = True
        out_effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(out_effect)
        fade_out = QPropertyAnimation(out_effect, b"opacity", self)
        fade_out.setDuration(150)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_out_finished() -> None:
            current_widget.setGraphicsEffect(None)
            self.stack.setCurrentIndex(next_index)
            incoming = self.stack.currentWidget()
            if incoming is None:
                self._transitioning = False
                return
            in_effect = QGraphicsOpacityEffect(incoming)
            incoming.setGraphicsEffect(in_effect)
            fade_in = QPropertyAnimation(in_effect, b"opacity", self)
            fade_in.setDuration(150)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

            def on_in_finished() -> None:
                incoming.setGraphicsEffect(None)
                self._transitioning = False
                if fade_in in self._animations:
                    self._animations.remove(fade_in)

            fade_in.finished.connect(on_in_finished)
            self._animations.append(fade_in)
            fade_in.start()

        fade_out.finished.connect(on_out_finished)
        self._animations.append(fade_out)
        fade_out.start()

    def _show_about(self) -> None:
        dialog = QDialog(self)
        apply_theme(dialog)
        dialog.setWindowTitle("Sobre")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Phoenix {__version__}"))
        layout.addWidget(QLabel("Aplicacao local-first para gestao pessoal."))
        close_button = QPushButton("Fechar")
        close_button.setObjectName("btn-ghost")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec()

    def _apply_module_defaults(self, root: QWidget) -> None:
        for layout in root.findChildren(QLayout):
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(12)

        for label in root.findChildren(QLabel):
            text = label.text().strip()
            if not text:
                continue
            if label.objectName():
                continue
            if len(text) <= 20 and text.isupper():
                label.setObjectName("label-section")
            elif len(text) <= 28 and any(ch.isalpha() for ch in text):
                label.setObjectName("label-title")

        for button in root.findChildren(QPushButton):
            if button.objectName() in {"btn-primary", "btn-ghost", "btn-danger", "btn-flat", "btn-secondary"}:
                continue
            text = button.text().lower()
            if any(word in text for word in ["excluir", "remover", "delet", "apagar"]):
                button.setObjectName("btn-danger")
            elif any(word in text for word in ["salvar", "novo", "criar", "adicionar", "iniciar", "ok"]):
                button.setObjectName("btn-primary")
            else:
                button.setObjectName("btn-ghost")

    def _install_ripple_effects(self, root: QWidget | None = None) -> None:
        scope = root or self
        for button in scope.findChildren(QPushButton):
            if button.objectName() == "btn-primary":
                button.installEventFilter(self._ripple_filter)
