from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.modules.health.controller import HealthController
from phoenix.modules.health.widgets import BodyMetricChart, MetricSlider, MoodSelector, SleepChart, WaterProgress
from phoenix.utils.constants import Events


class HealthView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = HealthController()
        self.event_bus = event_bus

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.register_tab = QWidget()
        self.charts_tab = QWidget()
        self.workouts_tab = QWidget()
        self.tabs.addTab(self.register_tab, "Registrar Hoje")
        self.tabs.addTab(self.charts_tab, "Graficos")
        self.tabs.addTab(self.workouts_tab, "Treinos")
        layout.addWidget(self.tabs)

        self._build_register_tab()
        self._build_charts_tab()
        self._build_workouts_tab()
        self.refresh()

    def _build_register_tab(self) -> None:
        layout = QFormLayout(self.register_tab)
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0, 300)
        self.weight_input.setDecimals(1)
        self.sleep_slider = MetricSlider(0, 14, 7)
        self.water_slider = MetricSlider(0, 5000, 2000)
        self.energy_slider = MetricSlider(1, 5, 3)
        self.steps_slider = MetricSlider(0, 30000, 8000)
        self.mood_selector = MoodSelector()
        self.save_day_button = QPushButton("Salvar Registro do Dia")
        self.save_day_button.setObjectName("btn-primary")
        self.save_day_button.clicked.connect(self._save_today)
        self.water_progress = WaterProgress()

        self.water_slider.changed.connect(lambda value: self.water_progress.set_progress(value, 2000))
        self.water_progress.set_progress(self.water_slider.value(), 2000)

        layout.addRow("Peso (kg)", self.weight_input)
        layout.addRow("Sono (h)", self.sleep_slider)
        layout.addRow("Agua (ml)", self.water_slider)
        layout.addRow("Humor (1-5)", self.mood_selector)
        layout.addRow("Energia (1-5)", self.energy_slider)
        layout.addRow("Passos", self.steps_slider)
        layout.addRow("Hidratacao", self.water_progress)
        layout.addRow(self.save_day_button)

    def _build_charts_tab(self) -> None:
        layout = QVBoxLayout(self.charts_tab)
        top = QHBoxLayout()
        self.period_filter = QComboBox()
        self.period_filter.addItems(["7d", "30d", "90d", "1a"])
        self.period_filter.currentTextChanged.connect(lambda _: self._reload_charts())
        top.addWidget(self.period_filter)
        top.addStretch(1)
        layout.addLayout(top)

        grid = QHBoxLayout()
        self.weight_chart = BodyMetricChart()
        self.sleep_chart = SleepChart()
        self.mood_chart = BodyMetricChart()
        self.water_chart = SleepChart()
        grid.addWidget(self.weight_chart, 1)
        grid.addWidget(self.sleep_chart, 1)
        grid.addWidget(self.mood_chart, 1)
        grid.addWidget(self.water_chart, 1)
        layout.addLayout(grid)

    def _build_workouts_tab(self) -> None:
        layout = QVBoxLayout(self.workouts_tab)
        form = QHBoxLayout()
        self.workout_type = QLineEdit()
        self.workout_type.setPlaceholderText("Tipo")
        self.workout_duration = MetricSlider(0, 240, 45)
        self.workout_calories = MetricSlider(0, 2000, 300)
        self.workout_date = QDateEdit()
        self.workout_date.setCalendarPopup(True)
        self.workout_date.setDate(QDate.currentDate())
        self.add_workout_button = QPushButton("+ Registrar Treino")
        self.add_workout_button.setObjectName("btn-primary")
        self.add_workout_button.clicked.connect(self._save_workout)
        form.addWidget(self.workout_type)
        form.addWidget(self.workout_duration)
        form.addWidget(self.workout_calories)
        form.addWidget(self.workout_date)
        form.addWidget(self.add_workout_button)
        layout.addLayout(form)

        self.workout_table = QTableWidget(0, 4)
        self.workout_table.setHorizontalHeaderLabels(["ID", "Tipo", "Duracao", "Calorias"])
        layout.addWidget(self.workout_table)

        self.weekly_workout_chart = SleepChart()
        layout.addWidget(self.weekly_workout_chart)

    def refresh(self) -> None:
        today_log = self.controller.get_log(date.today())
        if today_log:
            self.weight_input.setValue(today_log.weight_kg or 0)
            self.sleep_slider.slider.setValue(int(today_log.sleep_hours or 0))
            self.water_slider.slider.setValue(int(today_log.water_ml or 0))
            self.energy_slider.slider.setValue(int(today_log.energy or 3))
            self.steps_slider.slider.setValue(int(today_log.steps or 0))
        self._reload_charts()
        self._reload_workouts()

    def _reload_charts(self) -> None:
        mapping = {"7d": 7, "30d": 30, "90d": 90, "1a": 365}
        days = mapping.get(self.period_filter.currentText(), 30)

        weight_series = self.controller.get_weight_series(days)
        sleep_series = self.controller.get_sleep_series(days)
        mood_series = self.controller.get_mood_series(days)
        water_series = self.controller.get_water_series(days)

        self.weight_chart.plot_line([item[0].strftime("%d/%m") for item in weight_series], [item[1] for item in weight_series], color="#6366f1")
        self.sleep_chart.plot_bar([item[0].strftime("%d/%m") for item in sleep_series], [item[1] for item in sleep_series])
        self.mood_chart.plot_line([item[0].strftime("%d/%m") for item in mood_series], [item[1] for item in mood_series], color="#10b981")
        self.water_chart.plot_bar([item[0].strftime("%d/%m") for item in water_series], [item[1] for item in water_series])

    def _reload_workouts(self) -> None:
        workouts = self.controller.get_workouts(date.today() - timedelta(days=90), date.today())
        self.workout_table.setRowCount(0)
        for workout in workouts:
            row = self.workout_table.rowCount()
            self.workout_table.insertRow(row)
            self.workout_table.setItem(row, 0, QTableWidgetItem(str(workout.id)))
            self.workout_table.setItem(row, 1, QTableWidgetItem(workout.type or "-"))
            self.workout_table.setItem(row, 2, QTableWidgetItem(str(workout.duration or 0)))
            self.workout_table.setItem(row, 3, QTableWidgetItem(str(workout.calories or 0)))

        weekly = self.controller.get_weekly_workouts(12)
        self.weekly_workout_chart.plot_bar([item[0] for item in weekly], [item[1] for item in weekly])

    def _save_today(self) -> None:
        self.controller.upsert_log(
            date.today(),
            {
                "weight_kg": self.weight_input.value(),
                "sleep_hours": self.sleep_slider.value(),
                "water_ml": self.water_slider.value(),
                "mood": self.mood_selector.value(),
                "energy": self.energy_slider.value(),
                "steps": self.steps_slider.value(),
            },
        )
        self.show_toast("Registro diario salvo.", kind="success")
        self._publish_data_changed()
        self.refresh()

    def _save_workout(self) -> None:
        self.controller.add_workout(
            {
                "date": self.workout_date.date().toPyDate(),
                "type": self.workout_type.text().strip(),
                "duration": self.workout_duration.value(),
                "calories": self.workout_calories.value(),
            }
        )
        self.workout_type.clear()
        self.show_toast("Treino registrado.", kind="success")
        self._publish_data_changed()
        self._reload_workouts()

    def show_toast(self, message: str, kind: str = "info") -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[{kind}] {message}"})

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "health"})
