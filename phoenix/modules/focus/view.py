from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.modules.focus.controller import FocusController
from phoenix.modules.focus.widgets import PomodoroTimer, SessionsBarChart
from phoenix.utils.constants import Events


class FocusView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = FocusController()
        self.event_bus = event_bus

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        left = QVBoxLayout()
        self.timer = PomodoroTimer()
        left.addWidget(self.timer, 1)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Tarefa")
        left.addWidget(self.task_input)

        mode_buttons = QHBoxLayout()
        self.focus_btn = QPushButton("Foco 25m")
        self.short_btn = QPushButton("Pausa 5m")
        self.long_btn = QPushButton("Pausa 15m")
        for button in [self.focus_btn, self.short_btn, self.long_btn]:
            button.setObjectName("btn-secondary")
            mode_buttons.addWidget(button)
        left.addLayout(mode_buttons)

        controls = QHBoxLayout()
        self.start_btn = QPushButton("Iniciar")
        self.pause_btn = QPushButton("Pausar")
        self.reset_btn = QPushButton("Reset")
        self.start_btn.setObjectName("btn-primary")
        for button in [self.start_btn, self.pause_btn, self.reset_btn]:
            controls.addWidget(button)
        left.addLayout(controls)

        config = QFormLayout()
        self.focus_minutes = QSpinBox()
        self.focus_minutes.setRange(1, 180)
        self.focus_minutes.setValue(25)
        self.break_minutes = QSpinBox()
        self.break_minutes.setRange(1, 60)
        self.break_minutes.setValue(5)
        config.addRow("Foco", self.focus_minutes)
        config.addRow("Pausa", self.break_minutes)
        left.addLayout(config)

        layout.addLayout(left, 1)

        side = QVBoxLayout()
        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Data", "Tarefa", "Duracao"])
        side.addWidget(self.history_table, 1)

        self.stats_label = QLabel("Sessoes: 0 | Minutos: 0 | Melhor dia: -")
        side.addWidget(self.stats_label)
        self.weekly_chart = SessionsBarChart()
        side.addWidget(self.weekly_chart, 1)
        layout.addLayout(side, 1)

        self.focus_btn.clicked.connect(lambda: self._set_mode("Foco", self.focus_minutes.value()))
        self.short_btn.clicked.connect(lambda: self._set_mode("Pausa curta", self.break_minutes.value()))
        self.long_btn.clicked.connect(lambda: self._set_mode("Pausa longa", self.break_minutes.value() * 3))
        self.start_btn.clicked.connect(self._start)
        self.pause_btn.clicked.connect(self.timer.pause)
        self.reset_btn.clicked.connect(self.timer.reset)
        self.timer.session_completed.connect(self._handle_completed_session)

        self._sound = QSoundEffect(self)
        sound_path = Path(__file__).resolve().parents[2] / "assets" / "sounds" / "bell.wav"
        if sound_path.exists():
            self._sound.setSource(QUrl.fromLocalFile(str(sound_path)))
            self._sound.setVolume(0.7)

        self.refresh()

    def refresh(self) -> None:
        sessions = self.controller.get_sessions(date.today() - timedelta(days=14), date.today())
        self.history_table.setRowCount(0)
        for session in sessions:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(session.date.strftime("%d/%m/%Y")))
            self.history_table.setItem(row, 1, QTableWidgetItem(session.task_name or "-"))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{session.duration_min} min"))

        stats = self.controller.get_weekly_stats()
        self.stats_label.setText(
            f"Sessoes: {stats['sessions_this_week']} | Minutos: {stats['total_minutes_this_week']} | Melhor dia: {stats['best_day']}"
        )
        self.weekly_chart.plot_sessions(stats["sessions_per_day"])

    def _set_mode(self, mode: str, minutes: int) -> None:
        self.timer.set_duration_minutes(minutes, mode)

    def _start(self) -> None:
        self.timer.set_task_name(self.task_input.text().strip())
        self.timer.start()

    def _handle_completed_session(self, duration_minutes: int, task_name: str) -> None:
        self.controller.save_session(
            {
                "date": date.today(),
                "duration_min": duration_minutes,
                "task_name": task_name,
                "completed": True,
            }
        )
        if self._sound.source().isValid():
            self._sound.play()
        self.show_toast("Sessao concluida e salva.", kind="success")
        self._publish_data_changed()
        self.refresh()

    def show_toast(self, message: str, kind: str = "info") -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[{kind}] {message}"})

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "focus"})
