from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QCheckBox, QGraphicsOpacityEffect, QGridLayout, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

import pyqtgraph as pg

from phoenix.modules.dashboard.controller import DashboardController
from phoenix.core.events import EventBus
from phoenix.ui.widgets.chart_widget import ChartWidget
from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.stat_card import StatCard
from phoenix.utils.constants import Events


class DashboardView(QWidget):
    def __init__(self, event_bus: EventBus | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = DashboardController()
        self.event_bus = event_bus
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(16)
        layout.addLayout(self.stats_grid)

        self.goal_card = StatCard("Metas ativas", "0", "+0% concluidas")
        self.balance_card = StatCard("Saldo total", "R$ 0,00", "+0")
        self.streak_card = StatCard("Melhor streak", "0 dias", "rotina ativa")
        self.focus_card = StatCard("Foco na semana", "0", "sessoes concluidas")
        self.stat_cards = [self.goal_card, self.balance_card, self.streak_card, self.focus_card]
        for index, card in enumerate(self.stat_cards):
            self.stats_grid.addWidget(card, 0, index)

        self.finance_chart = CardWidget("Receitas vs despesas")
        self.finance_chart_view = ChartWidget()
        self.finance_chart.layout.addWidget(self.finance_chart_view)

        self.mood_chart = CardWidget("Humor e energia")
        self.mood_plot = pg.PlotWidget()
        self.mood_plot.setBackground("#18181b")
        self.mood_chart.layout.addWidget(self.mood_plot)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(16)
        charts_grid.addWidget(self.finance_chart, 0, 0)
        charts_grid.addWidget(self.mood_chart, 0, 1)
        layout.addLayout(charts_grid)

        self.upcoming_card = CardWidget("Proximas metas")
        self.upcoming_list = QListWidget()
        self.upcoming_card.layout.addWidget(self.upcoming_list)

        self.habits_card = CardWidget("Habitos de hoje")
        self.habits_list = QVBoxLayout()
        self.habits_card.layout.addLayout(self.habits_list)

        self.tasks_card = CardWidget("Tarefas em andamento")
        self.tasks_list = QListWidget()
        self.tasks_card.layout.addWidget(self.tasks_list)

        quick_grid = QGridLayout()
        quick_grid.setSpacing(16)
        quick_grid.addWidget(self.upcoming_card, 0, 0)
        quick_grid.addWidget(self.habits_card, 0, 1)
        quick_grid.addWidget(self.tasks_card, 0, 2)
        layout.addLayout(quick_grid)

        self.upcoming_list.itemClicked.connect(lambda item: self._navigate(1))
        self.tasks_list.itemClicked.connect(lambda item: self._navigate(7))
        self._animations: list[QPropertyAnimation] = []

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.refresh()

    def refresh(self) -> None:
        summary = self.controller.summary()
        self.goal_card.update_values(str(summary["goals_active"]), f"+{summary['goals_completed_pct']}% concluidas")
        balance = float(summary["balance"])
        self.balance_card.update_values(f"R$ {balance:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "+contas e fluxo")
        self.streak_card.update_values(f"{summary['best_streak']} dias", "melhor habito ativo")
        self.focus_card.update_values(str(summary["focus_week"]), "sessoes na semana")

        labels, incomes, expenses = self.controller.monthly_cash_flow_last_six_months()
        self.finance_chart_view.plot_grouped_bar(
            labels,
            [
                ("Receitas", incomes, "#10b981"),
                ("Despesas", expenses, "#ef4444"),
            ],
        )

        mood_labels, mood_values, energy_values = self.controller.mood_energy_last_30_days()
        self.mood_plot.clear()
        self.mood_plot.showGrid(x=True, y=True, alpha=0.2)
        self.mood_plot.getAxis("left").setTextPen("#a1a1aa")
        self.mood_plot.getAxis("bottom").setTextPen("#71717a")
        self.mood_plot.plot(mood_values, pen=pg.mkPen("#6366f1", width=2), name="Humor")
        self.mood_plot.plot(energy_values, pen=pg.mkPen("#10b981", width=2), name="Energia")
        ticks = [(index, label) for index, label in enumerate(mood_labels) if index % 5 == 0]
        self.mood_plot.getAxis("bottom").setTicks([ticks])

        self.upcoming_list.clear()
        for goal in self.controller.upcoming_goals():
            due = goal.target_date.strftime("%d/%m") if goal.target_date else "Sem data"
            self.upcoming_list.addItem(QListWidgetItem(f"{goal.title}  |  {due}"))

        self.tasks_list.clear()
        for task in self.controller.active_tasks():
            due = task.due_date.strftime("%d/%m") if task.due_date else "Sem prazo"
            self.tasks_list.addItem(QListWidgetItem(f"{task.title}  |  {due}"))

        while self.habits_list.count():
            child = self.habits_list.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
        for habit in self.controller.habits_for_today():
            checkbox = QCheckBox(str(habit["name"]))
            checkbox.setChecked(bool(habit["completed"]))
            checkbox.stateChanged.connect(
                lambda state, habit_id=int(habit["id"]): self.controller.toggle_habit(habit_id, state == Qt.CheckState.Checked.value)
            )
            self.habits_list.addWidget(checkbox)
        self.habits_list.addStretch(1)
        self._animate_cards()

    def _navigate(self, index: int) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.NAVIGATE, {"index": index})

    def _animate_cards(self) -> None:
        self._animations.clear()
        for index, widget in enumerate(self.stat_cards + [self.finance_chart, self.mood_chart, self.upcoming_card, self.habits_card, self.tasks_card]):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            animation = QPropertyAnimation(effect, b"opacity", self)
            animation.setDuration(260 + index * 35)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            animation.start()
            self._animations.append(animation)
