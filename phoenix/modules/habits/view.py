from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.core.models import Habit
from phoenix.modules.habits.controller import HabitsController
from phoenix.modules.habits.widgets import HabitRow, HeatmapWidget, StreakBadge
from phoenix.ui.widgets.confirm_dialog import ConfirmDialog
from phoenix.ui.widgets.empty_state import EmptyState
from phoenix.utils.constants import Events


class HabitsView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = HabitsController()
        self.event_bus = event_bus
        self._selected_habit_id: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.today_tab = QWidget()
        self.heatmap_tab = QWidget()
        self.manage_tab = QWidget()
        self.tabs.addTab(self.today_tab, "Hoje")
        self.tabs.addTab(self.heatmap_tab, "Heatmap")
        self.tabs.addTab(self.manage_tab, "Gerenciar")
        layout.addWidget(self.tabs)

        self._build_today_tab()
        self._build_heatmap_tab()
        self._build_manage_tab()
        self.refresh()

    def _build_today_tab(self) -> None:
        layout = QVBoxLayout(self.today_tab)
        self.today_stack = QStackedWidget()
        today_list_widget = QWidget()
        self.today_list_layout = QVBoxLayout(today_list_widget)
        self.today_empty = EmptyState("Sem habitos", "Crie habitos na aba Gerenciar.", "Ir para gerenciar")
        self.today_empty.action_button.clicked.connect(lambda: self.tabs.setCurrentWidget(self.manage_tab))
        self.today_stack.addWidget(today_list_widget)
        self.today_stack.addWidget(self.today_empty)
        layout.addWidget(self.today_stack)

        summary = self.controller.get_today_summary()
        self.today_summary = QLabel(f"Concluidos hoje: {summary['completed']}/{summary['total']}")
        layout.addWidget(self.today_summary)

    def _build_heatmap_tab(self) -> None:
        layout = QVBoxLayout(self.heatmap_tab)
        selector_row = QHBoxLayout()
        self.habit_selector = QComboBox()
        selector_row.addWidget(QLabel("Habito"))
        selector_row.addWidget(self.habit_selector)
        selector_row.addStretch(1)
        layout.addLayout(selector_row)

        self.heatmap = HeatmapWidget()
        layout.addWidget(self.heatmap)

        stats = QHBoxLayout()
        self.current_streak_label = StreakBadge(0)
        self.longest_streak_label = QLabel("Maior streak: 0")
        self.rate_label = QLabel("Taxa (30d): 0%")
        stats.addWidget(self.current_streak_label)
        stats.addWidget(self.longest_streak_label)
        stats.addWidget(self.rate_label)
        stats.addStretch(1)
        layout.addLayout(stats)
        self.habit_selector.currentIndexChanged.connect(self._refresh_heatmap_stats)

    def _build_manage_tab(self) -> None:
        layout = QVBoxLayout(self.manage_tab)
        form = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome do habito")
        self.frequency_input = QComboBox()
        self.frequency_input.addItems(["daily", "weekly", "custom"])
        self.active_input = QCheckBox("Ativo")
        self.active_input.setChecked(True)
        self.save_button = QPushButton("Novo")
        self.save_button.setObjectName("btn-primary")
        form.addWidget(self.name_input, 1)
        form.addWidget(self.frequency_input)
        form.addWidget(self.active_input)
        form.addWidget(self.save_button)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.edit_button = QPushButton("Editar")
        self.archive_button = QPushButton("Arquivar")
        self.delete_button = QPushButton("Excluir")
        for button in [self.edit_button, self.archive_button, self.delete_button]:
            button.setObjectName("btn-secondary")
            actions.addWidget(button)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.manage_table = QTableWidget(0, 4)
        self.manage_table.setHorizontalHeaderLabels(["ID", "Nome", "Frequencia", "Ativo"])
        self.manage_table.itemSelectionChanged.connect(self._sync_selection_from_table)
        layout.addWidget(self.manage_table)

        self.save_button.clicked.connect(self._save)
        self.edit_button.clicked.connect(self._edit_selected)
        self.archive_button.clicked.connect(self._archive_selected)
        self.delete_button.clicked.connect(self._delete_selected)

    def _reload_today(self, habits: list[Habit]) -> None:
        while self.today_list_layout.count():
            item = self.today_list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not habits:
            self.today_stack.setCurrentWidget(self.today_empty)
            return

        self.today_stack.setCurrentIndex(0)
        today = date.today()
        start_week = today - timedelta(days=6)
        for habit in habits:
            log = self.controller.get_log(habit.id, today)
            completions_week = sum(1 for item in self.controller.get_logs_range(habit.id, start_week, today) if item.completed)
            row = HabitRow(
                habit.id,
                habit.name,
                self.controller.get_streak(habit.id),
                completions_week,
                bool(log and log.completed),
                self._toggle_today,
            )
            self.today_list_layout.addWidget(row)
        self.today_list_layout.addStretch(1)

    def _reload_manage(self, habits: list[Habit]) -> None:
        self.manage_table.setRowCount(0)
        for habit in habits:
            row = self.manage_table.rowCount()
            self.manage_table.insertRow(row)
            self.manage_table.setItem(row, 0, QTableWidgetItem(str(habit.id)))
            self.manage_table.setItem(row, 1, QTableWidgetItem(habit.name))
            self.manage_table.setItem(row, 2, QTableWidgetItem(habit.frequency))
            self.manage_table.setItem(row, 3, QTableWidgetItem("Sim" if habit.active else "Nao"))

    def refresh(self) -> None:
        habits = self.controller.get_all(active_only=False)
        active_habits = [habit for habit in habits if habit.active]
        self._reload_today(active_habits)
        self._reload_manage(habits)

        self.habit_selector.blockSignals(True)
        self.habit_selector.clear()
        for habit in active_habits:
            self.habit_selector.addItem(habit.name, habit.id)
        self.habit_selector.blockSignals(False)

        self.heatmap.set_completion_map(self.controller.get_heatmap_data())
        self._refresh_heatmap_stats()
        summary = self.controller.get_today_summary()
        self.today_summary.setText(f"Concluidos hoje: {summary['completed']}/{summary['total']}")

    def _toggle_today(self, habit_id: int, completed: bool) -> None:
        self.controller.log_today(habit_id, completed)
        self.show_toast("Registro atualizado.", kind="success")
        self._publish_data_changed()
        self.refresh()

    def _save(self) -> None:
        name = self.name_input.text().strip()
        if not self._validate_field(self.name_input, bool(name)):
            self.show_toast("Informe um nome valido.", kind="error")
            return
        self.controller.create(
            {
                "name": name,
                "frequency": self.frequency_input.currentText(),
                "active": self.active_input.isChecked(),
            }
        )
        self.name_input.clear()
        self.show_toast("Habito criado.", kind="success")
        self._publish_data_changed()
        self.refresh()

    def _sync_selection_from_table(self) -> None:
        row = self.manage_table.currentRow()
        if row < 0:
            self._selected_habit_id = None
            return
        self._selected_habit_id = int(self.manage_table.item(row, 0).text())

    def _edit_selected(self) -> None:
        if self._selected_habit_id is None:
            return
        selected = self._get_selected_habit()
        if selected is None:
            return
        self.controller.update(
            selected.id,
            {
                "name": self.name_input.text().strip() or selected.name,
                "frequency": self.frequency_input.currentText(),
                "active": self.active_input.isChecked(),
            },
        )
        self.show_toast("Habito atualizado.", kind="success")
        self._publish_data_changed()
        self.refresh()

    def _archive_selected(self) -> None:
        selected = self._get_selected_habit()
        if selected is None:
            return
        self.controller.update(selected.id, {"active": False})
        self.show_toast("Habito arquivado.", kind="warning")
        self._publish_data_changed()
        self.refresh()

    def _delete_selected(self) -> None:
        selected = self._get_selected_habit()
        if selected is None:
            return
        confirm = ConfirmDialog("Excluir habito", f"Deseja excluir '{selected.name}'?")
        if confirm.exec() == 0:
            return
        self.controller.delete(selected.id)
        self.show_toast("Habito excluido.", kind="warning")
        self._publish_data_changed()
        self.refresh()

    def _get_selected_habit(self) -> Habit | None:
        if self._selected_habit_id is None:
            return None
        for habit in self.controller.get_all(active_only=False):
            if habit.id == self._selected_habit_id:
                return habit
        return None

    def _refresh_heatmap_stats(self) -> None:
        if self.habit_selector.count() == 0:
            self.current_streak_label.setText("0 dias consecutivos")
            self.longest_streak_label.setText("Maior streak: 0")
            self.rate_label.setText("Taxa (30d): 0%")
            return
        habit_id = int(self.habit_selector.currentData())
        streak = self.controller.get_streak(habit_id)
        longest = self.controller.get_longest_streak(habit_id)
        rate = self.controller.get_completion_rate(habit_id, 30)
        self.current_streak_label.setText(f"{streak} dias consecutivos")
        self.longest_streak_label.setText(f"Maior streak: {longest}")
        self.rate_label.setText(f"Taxa (30d): {int(rate * 100)}%")

    def show_toast(self, message: str, kind: str = "info") -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[{kind}] {message}"})

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "habits"})

    def _validate_field(self, field: QLineEdit, is_valid: bool) -> bool:
        field.setProperty("invalid", not is_valid)
        field.style().unpolish(field)
        field.style().polish(field)
        return is_valid
