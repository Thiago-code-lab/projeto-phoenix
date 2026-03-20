from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from dynaconf import Dynaconf
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, QUrl, Qt, pyqtSignal
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import QFrame, QGridLayout, QScrollArea
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.modules.focus.controller import FocusController
from phoenix.ui.widgets.bar_chart_widget import BarChartWidget
from phoenix.ui.widgets.circular_timer import CircularTimerWidget
from phoenix.ui.widgets.validated_fields import FormValidator, ValidatedLineEdit
from phoenix.utils.constants import Events

SETTINGS = Dynaconf(settings_files=[str(Path(__file__).resolve().parents[2] / "settings.toml")])


class ModeTabBar(QWidget):
    """Seletor de modo em formato pill com indicador animado."""

    mode_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("mode-tab-container")
        self.setStyleSheet(
            "QWidget#mode-tab-container { background: #161616; border: 1px solid #2A2A2A; border-radius: 10px; }"
            "QPushButton#mode-tab { background: transparent; border: none; color: #555555; border-radius: 7px; padding: 8px 12px; }"
            "QPushButton#mode-tab:hover { color: #AAAAAA; }"
            "QPushButton#mode-tab[active='true'] {"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #C0392B,stop:1 #E67E22);"
            "color: #FFFFFF;"
            "}"
        )

        self._active_key = "focus"
        self._buttons: dict[str, QPushButton] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        for key, label in (("focus", "Foco"), ("short_break", "Pausa curta"), ("long_break", "Pausa longa")):
            btn = QPushButton(label)
            btn.setObjectName("mode-tab")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _=False, k=key: self.set_active(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        self._indicator_anim = QPropertyAnimation(self, b"minimumHeight", self)
        self._indicator_anim.setDuration(150)
        self._indicator_anim.setStartValue(36)
        self._indicator_anim.setEndValue(37)
        self._indicator_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._indicator_anim.finished.connect(lambda: self.setMinimumHeight(36))
        self.set_active("focus")

    def set_active(self, key: str) -> None:
        self._active_key = key
        for button_key, button in self._buttons.items():
            button.setProperty("active", button_key == key)
            button.style().unpolish(button)
            button.style().polish(button)
        self._indicator_anim.stop()
        self._indicator_anim.start()
        self.mode_changed.emit(key)


class SessionHistoryWidget(QWidget):
    """Histórico recente com itens compactos e indicador visual de sessão."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("HISTÓRICO RECENTE")
        title.setObjectName("label-section")
        layout.addWidget(title)

        self.listing = QListWidget()
        self.listing.setMaximumHeight(280)
        self.listing.setSpacing(4)
        layout.addWidget(self.listing)

    def set_sessions(self, sessions: list) -> None:
        self.listing.clear()
        for session in sessions[:8]:
            row = QWidget()
            line = QHBoxLayout(row)
            line.setContentsMargins(8, 6, 8, 6)
            line.setSpacing(8)

            dot = QLabel("●")
            dot.setStyleSheet("color: #E67E22; font-size: 11px;")
            line.addWidget(dot)

            task = QLabel(session.task_name or "Sessão de foco")
            task.setStyleSheet("color: #F0F0F0;")
            line.addWidget(task, 1)

            duration = QLabel(f"{session.duration_min}m")
            duration.setStyleSheet("color: #E67E22; font-weight: 600;")
            line.addWidget(duration)

            stamp = QLabel(session.date.strftime("%d/%m"))
            stamp.setStyleSheet("color: #666666;")
            line.addWidget(stamp)

            item = QListWidgetItem()
            item.setSizeHint(row.sizeHint())
            self.listing.addItem(item)
            self.listing.setItemWidget(item, row)


class FocusView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = FocusController()
        self.event_bus = event_bus
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        self._session_running = False
        self._session_mode = "focus"
        self._session_duration_min = int(SETTINGS.get("focus.default_duration", 25))
        self._remaining_seconds = self._session_duration_min * 60
        self._daily_goal_hours = int(SETTINGS.get("focus.daily_goal_hours", 2))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        left_panel = QFrame()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setSpacing(10)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)

        self.section_label = QLabel("FOCO")
        self.section_label.setObjectName("label-section")
        self.subtitle_label = QLabel("Sessões profundas · Pomodoro")
        self.subtitle_label.setObjectName("label-muted")
        left_panel_layout.addWidget(self.section_label)
        left_panel_layout.addWidget(self.subtitle_label)

        self.mode_tabs = ModeTabBar()
        left_panel_layout.addWidget(self.mode_tabs)

        self.timer = CircularTimerWidget()
        left_panel_layout.addWidget(self.timer, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.duration_row = QHBoxLayout()
        self.duration_buttons: dict[str, QPushButton] = {}
        for key, text, minutes in [
            ("d25", "25m", 25),
            ("d50", "50m", 50),
            ("d90", "90m", 90),
            ("b5", "Pausa 5m", 5),
            ("b15", "Pausa 15m", 15),
        ]:
            button = QPushButton(text)
            button.setObjectName("pill-duration")
            button.setCheckable(True)
            button.setProperty("minutes", minutes)
            button.clicked.connect(lambda checked=False, k=key: self._select_duration(k))
            self.duration_row.addWidget(button)
            self.duration_buttons[key] = button
        left_panel_layout.addLayout(self.duration_row)
        self._select_duration("d25")

        self.task_input = ValidatedLineEdit()
        self.task_input.set_required(True)
        self.task_input.setObjectName("inp-focus-task")
        self.task_input.setPlaceholderText("No que você está focando agora?")
        self.task_selector = QComboBox()
        self.task_selector.setObjectName("cmb-focus-link")
        left_panel_layout.addWidget(self.task_input)
        left_panel_layout.addWidget(self.task_input.error_label)
        left_panel_layout.addWidget(self.task_selector)

        controls = QHBoxLayout()
        self.start_btn = QPushButton("Iniciar")
        self.start_btn.setObjectName("btn-primary")
        self.reset_btn = QPushButton("↺ Reset")
        self.reset_btn.setObjectName("btn-ghost")
        self.cancel_btn = QPushButton("✕ Cancelar")
        self.cancel_btn.setObjectName("btn-ghost")
        self.cancel_btn.setVisible(False)
        controls.addWidget(self.start_btn)
        controls.addWidget(self.reset_btn)
        controls.addWidget(self.cancel_btn)
        left_panel_layout.addLayout(controls)

        layout.addWidget(left_panel, 6)

        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(0, 0, 0, 0)

        cards_grid = QGridLayout()
        cards_grid.setSpacing(8)
        self.week_sessions_value = self._build_metric_card(cards_grid, 0, "Sessões da semana", "0")
        self.week_hours_value = self._build_metric_card(cards_grid, 1, "Horas focadas", "0.0h")
        self.best_day_value = self._build_metric_card(cards_grid, 2, "Melhor dia", "-")
        right_layout.addLayout(cards_grid)

        self.weekly_chart = BarChartWidget()
        right_layout.addWidget(self.weekly_chart)

        self.history_widget = SessionHistoryWidget()
        right_layout.addWidget(self.history_widget)

        self.stats_label = QLabel("Sessões: <b>0</b> · Minutos: <b>0</b> · Melhor dia: <b>-</b>")
        self.stats_label.setStyleSheet("color: #555555;")
        self.weekly_report_label = QLabel("Horas semanais: <b>0.0h</b> · Distribuição: <b>-</b>")
        self.weekly_report_label.setStyleSheet("color: #555555;")
        right_layout.addWidget(self.stats_label)
        right_layout.addWidget(self.weekly_report_label)
        right_layout.addStretch(1)

        layout.addWidget(right_panel, 4)

        self.mode_tabs.mode_changed.connect(self._on_mode_changed)
        self.start_btn.clicked.connect(self._toggle_start_pause)
        self.reset_btn.clicked.connect(self._reset_timer)
        self.cancel_btn.clicked.connect(self._cancel_session)
        self.form_validator = FormValidator([self.task_input], self)
        self.form_validator.bind_submit_button(self.start_btn)
        self.task_input.textChanged.connect(lambda _: self.form_validator.is_valid())

        self._sound = QSoundEffect(self)
        custom_sound = SETTINGS.get("app.focus_sound_path", "")
        sound_path = Path(custom_sound) if custom_sound else Path(__file__).resolve().parents[2] / "assets" / "sounds" / "bell.wav"
        if sound_path.exists():
            self._sound.setSource(QUrl.fromLocalFile(str(sound_path)))
            self._sound.setVolume(0.7)

        self._set_mode("Foco", self._session_duration_min)
        self.refresh()

    def _build_metric_card(self, grid: QGridLayout, column: int, title: str, value: str) -> QLabel:
        card = QFrame()
        card.setStyleSheet("background: #161616; border: 1px solid #2A2A2A; border-radius: 10px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(2)
        caption = QLabel(title)
        caption.setObjectName("label-section")
        amount = QLabel(value)
        amount.setObjectName("label-value")
        amount.setStyleSheet("font-size: 22px;")
        layout.addWidget(caption)
        layout.addWidget(amount)
        grid.addWidget(card, 0, column)
        return amount

    def refresh(self) -> None:
        sessions = self.controller.get_sessions(date.today() - timedelta(days=14), date.today())
        self.history_widget.set_sessions(sessions)

        stats = self.controller.get_weekly_stats()
        self.week_sessions_value.setText(str(stats["sessions_this_week"]))
        self.week_hours_value.setText(f"{round(stats['total_minutes_this_week'] / 60.0, 1)}h")
        self.best_day_value.setText(str(stats["best_day"]))

        self.stats_label.setText(
            f"Sessões: <b style='color:#E67E22'>{stats['sessions_this_week']}</b> · "
            f"Minutos: <b style='color:#E67E22'>{stats['total_minutes_this_week']}</b> · "
            f"Melhor dia: <b style='color:#E67E22'>{stats['best_day']}</b>"
        )

        start_week = date.today() - timedelta(days=date.today().weekday())
        week_sessions = self.controller.get_sessions(start_week, date.today())
        day_minutes: dict[str, int] = {}
        for item in week_sessions:
            day_key = item.date.strftime("%a")
            day_minutes[day_key] = day_minutes.get(day_key, 0) + int(item.duration_min)
        self.weekly_chart.set_data(day_minutes, goal_minutes=max(30, self._daily_goal_hours * 60))

        self._reload_tasks()
        report = self.controller.weekly_report()
        distribution = ", ".join(report["by_project"].keys()) or "-"
        self.weekly_report_label.setText(
            f"Horas semanais: <b style='color:#E67E22'>{report['total_hours']}h</b> · "
            f"Distribuição: <b style='color:#E67E22'>{distribution}</b>"
        )

    def _set_mode(self, mode: str, minutes: int) -> None:
        self._session_duration_min = max(1, minutes)
        self._remaining_seconds = self._session_duration_min * 60
        self.timer.set_state_text(f"⚡ {mode.upper()}")
        self.timer.set_time_text(self._format_seconds(self._remaining_seconds))
        self.timer.progress = 1.0

    def _on_mode_changed(self, mode_key: str) -> None:
        self._session_mode = mode_key
        if mode_key == "focus":
            self._set_mode("Em foco", self._session_duration_min if self._session_duration_min in {25, 50, 90} else 25)
        elif mode_key == "short_break":
            self._set_mode("Pausa curta", 5)
        else:
            self._set_mode("Pausa longa", 15)

    def _select_duration(self, key: str) -> None:
        for current_key, button in self.duration_buttons.items():
            button.setChecked(current_key == key)
        button = self.duration_buttons[key]
        minutes = int(button.property("minutes") or 25)
        if key.startswith("b"):
            self.mode_tabs.set_active("short_break" if minutes == 5 else "long_break")
            self._set_mode("Pausa curta" if minutes == 5 else "Pausa longa", minutes)
        else:
            self.mode_tabs.set_active("focus")
            self._set_mode("Em foco", minutes)

    def _toggle_start_pause(self) -> None:
        if self._session_running:
            self._pause_session()
            return
        self._start()

    def _start(self) -> None:
        if not self.form_validator.is_valid():
            self.show_toast("Informe o nome da tarefa antes de iniciar.", kind="warning")
            return

        self._session_running = True
        self.start_btn.setText("Pausar")
        self.cancel_btn.setVisible(True)
        self._timer.start()

        total_seconds = max(1, self._session_duration_min * 60)
        self.timer.animate_progress(duration_ms=self._remaining_seconds * 1000, start=self._remaining_seconds / total_seconds, end=0.0)

    def _pause_session(self) -> None:
        self._session_running = False
        self._timer.stop()
        self.timer.stop_animation()
        self.start_btn.setText("Iniciar")

    def _reset_timer(self) -> None:
        self._pause_session()
        self._remaining_seconds = self._session_duration_min * 60
        self.timer.set_time_text(self._format_seconds(self._remaining_seconds))
        self.timer.progress = 1.0
        self.cancel_btn.setVisible(False)

    def _cancel_session(self) -> None:
        self._reset_timer()
        self.show_toast("Sessão cancelada.", kind="warning")

    def _tick(self) -> None:
        self._remaining_seconds = max(0, self._remaining_seconds - 1)
        self.timer.set_time_text(self._format_seconds(self._remaining_seconds))
        if self._remaining_seconds == 0:
            self._pause_session()
            self.cancel_btn.setVisible(False)
            self._handle_completed_session(self._session_duration_min, self.task_input.text().strip())

    def _handle_completed_session(self, duration_minutes: int, task_name: str) -> None:
        self.controller.save_session(
            {
                "date": date.today(),
                "duration_min": duration_minutes,
                "task_name": task_name,
                "task_id": self.task_selector.currentData(),
                "completed": True,
            }
        )
        if self._sound.source().isValid():
            self._sound.play()
        self.show_toast("Sessao concluida e salva.", kind="success")
        self._publish_data_changed()
        self._remaining_seconds = self._session_duration_min * 60
        self.timer.set_time_text(self._format_seconds(self._remaining_seconds))
        self.timer.progress = 1.0
        self.start_btn.setText("Iniciar")
        self.refresh()

    def show_toast(self, message: str, kind: str = "info") -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[{kind}] {message}"})

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "focus"})

    def _reload_tasks(self) -> None:
        self.task_selector.clear()
        self.task_selector.addItem("Sem vínculo com projeto", None)
        for task in self.controller.list_active_tasks():
            self.task_selector.addItem(task.title, task.id)

    def _format_seconds(self, total: int) -> str:
        minutes, seconds = divmod(total, 60)
        return f"{minutes:02d}:{seconds:02d}"
