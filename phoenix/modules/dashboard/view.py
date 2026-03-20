from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QCheckBox, QGraphicsOpacityEffect, QGridLayout, QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QLabel

import pyqtgraph as pg

from phoenix.modules.dashboard.controller import DashboardController
from phoenix.core.events import EventBus
from phoenix.ui.widgets.chart_widget import ChartWidget
from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.gradient_progress import GradientProgressBar
from phoenix.ui.widgets.metric_card import MetricCard
from phoenix.ui.widgets.section_header import SectionHeader
from phoenix.ui.widgets.streak_badge import StreakBadge
from phoenix.utils.constants import Events


class DashboardView(QWidget):
    def __init__(self, event_bus: EventBus | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = DashboardController()
        self.event_bus = event_bus
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("Hoje"))

        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(12)
        layout.addLayout(self.stats_grid)

        self.goal_card = MetricCard("Metas ativas", "0", "◎")
        self.balance_card = MetricCard("Saldo total", "R$ 0,00", "◈")
        self.streak_card = MetricCard("Melhor streak", "0 dias", "🔥")
        self.focus_card = MetricCard("Foco na semana", "0", "◔")
        self.stat_cards = [self.goal_card, self.balance_card, self.streak_card, self.focus_card]
        for index, card in enumerate(self.stat_cards):
            self.stats_grid.addWidget(card, 0, index)

        self.dashboard_streak = StreakBadge(0)
        self.stats_grid.addWidget(self.dashboard_streak, 1, 0, 1, 2)

        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)
        progress_layout.addWidget(QLabel("Hoje"))
        self.today_progress = GradientProgressBar()
        progress_layout.addWidget(self.today_progress)
        progress_layout.addWidget(QLabel("Esta semana"))
        self.week_progress = GradientProgressBar()
        progress_layout.addWidget(self.week_progress)
        progress_layout.addWidget(QLabel("Metas"))
        self.goals_progress = GradientProgressBar()
        progress_layout.addWidget(self.goals_progress)
        self.stats_grid.addWidget(progress_container, 1, 2, 1, 2)

        layout.addWidget(SectionHeader("Esta semana"))

        self.finance_chart = CardWidget("Receitas vs despesas")
        self.finance_chart_view = ChartWidget()
        self.finance_chart.layout.addWidget(self.finance_chart_view)

        self.mood_chart = CardWidget("Humor e energia")
        self.mood_plot = pg.PlotWidget()
        self.mood_plot.setBackground("#161616")
        self.mood_chart.layout.addWidget(self.mood_plot)

        self.productivity_chart = CardWidget("Produtividade semanal")
        self.productivity_plot = pg.PlotWidget()
        self.productivity_plot.setBackground("#161616")
        self.productivity_chart.layout.addWidget(self.productivity_plot)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(16)
        charts_grid.addWidget(self.finance_chart, 0, 0)
        charts_grid.addWidget(self.mood_chart, 0, 1)
        charts_grid.addWidget(self.productivity_chart, 1, 0, 1, 2)
        layout.addLayout(charts_grid)

        layout.addWidget(SectionHeader("Metas"))

        self.upcoming_card = CardWidget("Proximas metas")
        self.upcoming_list = QListWidget()
        self.upcoming_card.layout.addWidget(self.upcoming_list)

        self.habits_card = CardWidget("Habitos de hoje")
        self.habits_list = QVBoxLayout()
        self.habits_card.layout.addLayout(self.habits_list)

        self.tasks_card = CardWidget("Tarefas em andamento")
        self.tasks_list = QListWidget()
        self.tasks_card.layout.addWidget(self.tasks_list)

        self.daily_summary_card = CardWidget("Resumo do dia")
        self.daily_summary_list = QListWidget()
        self.daily_summary_card.layout.addWidget(self.daily_summary_list)

        self.milestones_card = CardWidget("Proximos milestones")
        self.milestones_list = QListWidget()
        self.milestones_card.layout.addWidget(self.milestones_list)

        quick_grid = QGridLayout()
        quick_grid.setSpacing(16)
        quick_grid.addWidget(self.upcoming_card, 0, 0)
        quick_grid.addWidget(self.habits_card, 0, 1)
        quick_grid.addWidget(self.tasks_card, 0, 2)
        quick_grid.addWidget(self.daily_summary_card, 1, 0, 1, 2)
        quick_grid.addWidget(self.milestones_card, 1, 2)
        layout.addLayout(quick_grid)

        self.upcoming_list.itemClicked.connect(lambda item: self._navigate(1))
        self.tasks_list.itemClicked.connect(lambda item: self._navigate(7))
        self._animations: list[QPropertyAnimation] = []

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.refresh()

    def refresh(self) -> None:
        summary = self.controller.summary()
        self.goal_card.set_value(str(summary["goals_active"]))
        self.goal_card.set_sparkline([max(0, summary["goals_active"] - 2), summary["goals_active"] - 1, summary["goals_active"], summary["goals_active"] + 1, summary["goals_active"] + 2])
        balance = float(summary["balance"])
        self.balance_card.set_value(f"R$ {balance:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.balance_card.set_sparkline([balance * 0.95, balance * 0.98, balance, balance * 1.02, balance * 1.04])
        self.streak_card.set_value(f"{summary['global_streak']} dias")
        self.streak_card.set_sparkline([0, summary["best_streak"] * 0.4, summary["best_streak"] * 0.7, summary["best_streak"] * 0.9, summary["best_streak"]])
        self.focus_card.set_value(str(summary["focus_week"]))
        self.focus_card.set_sparkline([max(0, summary["focus_week"] - 3), max(0, summary["focus_week"] - 2), max(0, summary["focus_week"] - 1), summary["focus_week"], summary["focus_week"] + 1])
        self.dashboard_streak.set_days(int(summary["global_streak"]))
        self.today_progress.setValue(min(100, int((summary["global_streak"] / max(summary["best_streak"], 1)) * 100)))
        self.week_progress.setValue(min(100, int(summary["focus_week"] * 10)))
        self.goals_progress.setValue(int(summary["goals_completed_pct"]))

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
        self.mood_plot.getAxis("left").setTextPen("#AAAAAA")
        self.mood_plot.getAxis("bottom").setTextPen("#AAAAAA")
        self.mood_plot.plot(mood_values, pen=pg.mkPen(color="#E67E22", width=2), name="Humor")
        self.mood_plot.plot(energy_values, pen=pg.mkPen(color="#E67E22", width=2), name="Energia")
        ticks = [(index, label) for index, label in enumerate(mood_labels) if index % 5 == 0]
        self.mood_plot.getAxis("bottom").setTicks([ticks])

        productivity_labels, productivity_values = self.controller.weekly_productivity()
        self.productivity_plot.clear()
        self.productivity_plot.showGrid(x=True, y=True, alpha=0.2)
        self.productivity_plot.getAxis("left").setTextPen("#AAAAAA")
        self.productivity_plot.getAxis("bottom").setTextPen("#AAAAAA")
        self.productivity_plot.plot(productivity_values, pen=pg.mkPen(color="#E67E22", width=2), symbol="o", symbolSize=6)
        p_ticks = [(index, label) for index, label in enumerate(productivity_labels)]
        self.productivity_plot.getAxis("bottom").setTicks([p_ticks])

        self.upcoming_list.clear()
        for goal in self.controller.upcoming_goals():
            due = goal.target_date.strftime("%d/%m") if goal.target_date else "Sem data"
            self.upcoming_list.addItem(QListWidgetItem(f"{goal.title}  |  {due}"))

        self.tasks_list.clear()
        for task in self.controller.active_tasks():
            due = task.due_date.strftime("%d/%m") if task.due_date else "Sem prazo"
            self.tasks_list.addItem(QListWidgetItem(f"{task.title}  |  {due}"))

        self.daily_summary_list.clear()
        daily = self.controller.daily_overview()
        self.daily_summary_list.addItem(f"Habitos pendentes: {len(daily['pending_habits'])}")
        for name in list(daily["pending_habits"])[:4]:
            self.daily_summary_list.addItem(f"- {name}")
        self.daily_summary_list.addItem(f"Meta de foco hoje: {daily['focus_hours']}h")
        self.daily_summary_list.addItem(f"Tarefas Kanban do dia: {len(daily['tasks_today'])}")

        self.milestones_list.clear()
        for milestone in self.controller.upcoming_milestones():
            self.milestones_list.addItem(
                QListWidgetItem(f"{milestone['goal']} / {milestone['title']} - D-{milestone['days_left']}")
            )

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
        for index, widget in enumerate(
            self.stat_cards
            + [
                self.finance_chart,
                self.mood_chart,
                self.productivity_chart,
                self.upcoming_card,
                self.habits_card,
                self.tasks_card,
                self.daily_summary_card,
                self.milestones_card,
            ]
        ):
            existing_effect = widget.graphicsEffect()
            if existing_effect is not None:
                continue
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            animation = QPropertyAnimation(effect, b"opacity", self)
            animation.setDuration(260 + index * 35)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            animation.start()
            self._animations.append(animation)
