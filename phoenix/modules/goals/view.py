from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QDate
from PyQt6.QtGui import QKeySequence, QShortcut, QUndoCommand, QUndoStack
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.core.models import Goal, GoalMilestone
from phoenix.modules.goals.controller import GoalsController
from phoenix.modules.goals.widgets import CircularProgress, GoalCard, MilestoneRow, describe_timeline
from phoenix.ui.widgets.confirm_dialog import ConfirmDialog
from phoenix.ui.widgets.empty_state import EmptyState
from phoenix.utils.constants import Events


class DeleteGoalCommand(QUndoCommand):
    def __init__(self, controller: GoalsController, goal_snapshot: Goal, view: "GoalsView") -> None:
        super().__init__(f"Excluir meta {goal_snapshot.title}")
        self.controller = controller
        self.goal_snapshot = goal_snapshot
        self.view = view

    def redo(self) -> None:
        self.controller.delete(self.goal_snapshot.id)
        self.view.refresh()

    def undo(self) -> None:
        self.controller.restore(self.goal_snapshot)
        self.view.refresh()


class GoalsView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = GoalsController()
        self.event_bus = event_bus
        self._undo_stack = QUndoStack(self)
        self._selected_goal_id: int | None = None

        self._build_ui()
        self._connect_signals()
        self._setup_shortcuts()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        filters = QHBoxLayout()
        self.status_filter = QComboBox()
        self.status_filter.addItems(["all", "active", "completed", "paused"])
        self.category_filter = QComboBox()
        self.category_filter.addItem("all")
        self.new_button = QPushButton("Nova Meta")
        self.new_button.setObjectName("btn-primary")
        filters.addWidget(QLabel("Status"))
        filters.addWidget(self.status_filter)
        filters.addWidget(QLabel("Categoria"))
        filters.addWidget(self.category_filter)
        filters.addStretch(1)
        filters.addWidget(self.new_button)
        layout.addLayout(filters)

        content = QHBoxLayout()
        content.setSpacing(14)
        layout.addLayout(content, 1)

        self.cards_wrapper = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_wrapper)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch(1)
        cards_scroll = QScrollArea()
        cards_scroll.setWidgetResizable(True)
        cards_scroll.setWidget(self.cards_wrapper)

        self.list_stack = QStackedWidget()
        self.list_stack.addWidget(cards_scroll)
        self.list_empty = EmptyState("Sem metas", "Crie sua primeira meta para comecar.", "Nova Meta")
        self.list_stack.addWidget(self.list_empty)
        content.addWidget(self.list_stack, 1)

        self.detail_card = QWidget()
        detail_layout = QVBoxLayout(self.detail_card)
        detail_layout.setSpacing(12)

        form_grid = QGridLayout()
        self.title_input = QLineEdit()
        self.category_input = QLineEdit()
        self.status_input = QComboBox()
        self.status_input.addItems(["active", "paused", "completed"])
        self.start_input = QDateEdit()
        self.start_input.setCalendarPopup(True)
        self.start_input.setDate(QDate.currentDate())
        self.target_input = QDateEdit()
        self.target_input.setCalendarPopup(True)
        self.target_input.setDate(QDate.currentDate().addMonths(1))
        self.current_value_input = QLineEdit("0")
        self.target_value_input = QLineEdit("100")
        self.unit_input = QLineEdit()
        self.color_input = QLineEdit("#6366f1")

        form_grid.addWidget(QLabel("Titulo"), 0, 0)
        form_grid.addWidget(self.title_input, 0, 1)
        form_grid.addWidget(QLabel("Categoria"), 1, 0)
        form_grid.addWidget(self.category_input, 1, 1)
        form_grid.addWidget(QLabel("Status"), 2, 0)
        form_grid.addWidget(self.status_input, 2, 1)
        form_grid.addWidget(QLabel("Inicio"), 3, 0)
        form_grid.addWidget(self.start_input, 3, 1)
        form_grid.addWidget(QLabel("Prazo"), 4, 0)
        form_grid.addWidget(self.target_input, 4, 1)
        form_grid.addWidget(QLabel("Atual"), 5, 0)
        form_grid.addWidget(self.current_value_input, 5, 1)
        form_grid.addWidget(QLabel("Meta"), 6, 0)
        form_grid.addWidget(self.target_value_input, 6, 1)
        form_grid.addWidget(QLabel("Unidade"), 7, 0)
        form_grid.addWidget(self.unit_input, 7, 1)
        form_grid.addWidget(QLabel("Cor"), 8, 0)
        form_grid.addWidget(self.color_input, 8, 1)
        detail_layout.addLayout(form_grid)

        self.progress_ring = CircularProgress()
        detail_layout.addWidget(self.progress_ring)

        detail_layout.addWidget(QLabel("Milestones"))
        milestone_form = QHBoxLayout()
        self.milestone_title = QLineEdit()
        self.milestone_title.setPlaceholderText("Novo milestone")
        self.milestone_date = QDateEdit()
        self.milestone_date.setCalendarPopup(True)
        self.milestone_date.setDate(QDate.currentDate())
        self.milestone_add = QPushButton("Adicionar")
        self.milestone_add.setObjectName("btn-secondary")
        milestone_form.addWidget(self.milestone_title, 1)
        milestone_form.addWidget(self.milestone_date)
        milestone_form.addWidget(self.milestone_add)
        detail_layout.addLayout(milestone_form)

        self.milestones_wrapper = QWidget()
        self.milestones_layout = QVBoxLayout(self.milestones_wrapper)
        self.milestones_layout.setContentsMargins(0, 0, 0, 0)
        self.milestones_layout.setSpacing(6)
        milestones_scroll = QScrollArea()
        milestones_scroll.setWidgetResizable(True)
        milestones_scroll.setMinimumHeight(160)
        milestones_scroll.setWidget(self.milestones_wrapper)
        detail_layout.addWidget(milestones_scroll)

        actions = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.setObjectName("btn-primary")
        self.delete_button = QPushButton("Excluir")
        self.delete_button.setObjectName("btn-secondary")
        actions.addWidget(self.save_button)
        actions.addWidget(self.delete_button)
        detail_layout.addLayout(actions)
        content.addWidget(self.detail_card, 1)

    def _connect_signals(self) -> None:
        self.status_filter.currentTextChanged.connect(lambda _: self._load_data())
        self.category_filter.currentTextChanged.connect(lambda _: self._load_data())
        self.new_button.clicked.connect(self._new_goal)
        self.list_empty.action_button.clicked.connect(self._new_goal)
        self.save_button.clicked.connect(self._save_goal)
        self.delete_button.clicked.connect(self._delete_goal)
        self.milestone_add.clicked.connect(self._add_milestone)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self._undo_stack.undo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, activated=self._undo_stack.redo)

    def refresh(self) -> None:
        self._load_data()

    def _load_data(self) -> None:
        self._clear_layout(self.cards_layout)
        goals = self.controller.get_all(self.status_filter.currentText(), self.category_filter.currentText())
        categories = sorted({goal.category for goal in self.controller.get_all() if goal.category})
        current_category = self.category_filter.currentText()
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("all")
        self.category_filter.addItems(categories)
        if current_category in categories or current_category == "all":
            self.category_filter.setCurrentText(current_category)
        self.category_filter.blockSignals(False)

        if not goals:
            self.list_stack.setCurrentWidget(self.list_empty)
            self._new_goal()
            return
        self.list_stack.setCurrentIndex(0)

        for goal in goals:
            target = goal.target_value or 0.0
            ratio = (goal.current_value / target) if target > 0 else 0.0
            card = GoalCard(
                goal.id,
                goal.title,
                goal.category or "Sem categoria",
                goal.status,
                ratio,
                describe_timeline(goal.status, goal.target_date, goal.start_date),
            )
            card.clicked.connect(self._select_goal)
            self.cards_layout.addWidget(card)
        self.cards_layout.addStretch(1)

        if self._selected_goal_id is None or not any(goal.id == self._selected_goal_id for goal in goals):
            self._selected_goal_id = goals[0].id
        self._fill_form(self.controller.get_by_id(self._selected_goal_id))

    def _select_goal(self, goal_id: int) -> None:
        self._selected_goal_id = goal_id
        self._fill_form(self.controller.get_by_id(goal_id))

    def _fill_form(self, goal: Goal | None) -> None:
        if goal is None:
            return
        self.title_input.setText(goal.title)
        self.category_input.setText(goal.category or "")
        self.status_input.setCurrentText(goal.status)
        self.start_input.setDate(QDate(goal.start_date.year, goal.start_date.month, goal.start_date.day) if goal.start_date else QDate.currentDate())
        self.target_input.setDate(QDate(goal.target_date.year, goal.target_date.month, goal.target_date.day) if goal.target_date else QDate.currentDate())
        self.current_value_input.setText(str(goal.current_value))
        self.target_value_input.setText(str(goal.target_value or 0.0))
        self.unit_input.setText(goal.unit or "")
        self.color_input.setText(goal.color or "#6366f1")
        ratio = (goal.current_value / goal.target_value) if goal.target_value and goal.target_value > 0 else 0.0
        self.progress_ring.set_ratio(ratio)
        self._reload_milestones(goal)

    def _reload_milestones(self, goal: Goal) -> None:
        self._clear_layout(self.milestones_layout)
        if not goal.milestones:
            self.milestones_layout.addWidget(QLabel("Sem milestones."))
            self.milestones_layout.addStretch(1)
            return
        for milestone in sorted(goal.milestones, key=lambda item: item.id):
            row = MilestoneRow(milestone)
            row.toggled.connect(self._toggle_milestone)
            row.deleted.connect(self._delete_milestone)
            self.milestones_layout.addWidget(row)
        self.milestones_layout.addStretch(1)

    def _save_goal(self) -> None:
        valid = True
        valid &= self._validate_field(self.title_input, bool(self.title_input.text().strip()))
        valid &= self._validate_field(self.current_value_input, self._is_number(self.current_value_input.text().strip()))
        valid &= self._validate_field(self.target_value_input, self._is_number(self.target_value_input.text().strip()))
        if not valid:
            self.show_toast("Corrija os campos destacados.", kind="error")
            return

        payload = {
            "title": self.title_input.text().strip(),
            "category": self.category_input.text().strip() or "geral",
            "status": self.status_input.currentText(),
            "start_date": self.start_input.date().toPyDate(),
            "target_date": self.target_input.date().toPyDate(),
            "current_value": self.current_value_input.text().strip(),
            "target_value": self.target_value_input.text().strip(),
            "unit": self.unit_input.text().strip(),
            "color": self.color_input.text().strip() or "#6366f1",
        }

        if self._selected_goal_id is None:
            goal = self.controller.create(payload)
            self._selected_goal_id = goal.id
        else:
            self.controller.update(self._selected_goal_id, payload)

        self.show_toast("Meta salva com sucesso.", kind="success")
        self._publish_data_changed()
        self.refresh()

    def _delete_goal(self) -> None:
        if self._selected_goal_id is None:
            return
        goal = self.controller.get_by_id(self._selected_goal_id)
        if goal is None:
            return
        confirm = ConfirmDialog("Excluir meta", f"Deseja excluir '{goal.title}'?")
        if confirm.exec() == 0:
            return
        snapshot = Goal(
            id=goal.id,
            title=goal.title,
            description=goal.description,
            category=goal.category,
            status=goal.status,
            target_value=goal.target_value,
            current_value=goal.current_value,
            unit=goal.unit,
            start_date=goal.start_date,
            target_date=goal.target_date,
            color=goal.color,
            milestones=[
                GoalMilestone(
                    id=m.id,
                    goal_id=goal.id,
                    title=m.title,
                    completed=m.completed,
                    due_date=m.due_date,
                )
                for m in goal.milestones
            ],
        )
        command = DeleteGoalCommand(self.controller, snapshot, self)
        self._undo_stack.push(command)
        self.show_toast("Meta excluida. Use Ctrl+Z para desfazer.", kind="warning")
        self._publish_data_changed()

    def _add_milestone(self) -> None:
        if self._selected_goal_id is None:
            self.show_toast("Selecione uma meta para adicionar milestone.", kind="warning")
            return
        title = self.milestone_title.text().strip()
        if not self._validate_field(self.milestone_title, bool(title)):
            self.show_toast("Informe um titulo para o milestone.", kind="error")
            return
        self.controller.add_milestone(
            self._selected_goal_id,
            {"title": title, "due_date": self.milestone_date.date().toPyDate()},
        )
        self.milestone_title.clear()
        self.show_toast("Milestone adicionado.", kind="success")
        self._publish_data_changed()
        self.refresh()

    def _toggle_milestone(self, milestone_id: int) -> None:
        self.controller.toggle_milestone(milestone_id)
        self._publish_data_changed()
        self.refresh()

    def _delete_milestone(self, milestone_id: int) -> None:
        confirm = ConfirmDialog("Excluir milestone", "Deseja excluir este milestone?")
        if confirm.exec() == 0:
            return
        self.controller.delete_milestone(milestone_id)
        self.show_toast("Milestone excluido.", kind="warning")
        self._publish_data_changed()
        self.refresh()

    def _new_goal(self) -> None:
        self._selected_goal_id = None
        self.title_input.clear()
        self.category_input.clear()
        self.status_input.setCurrentText("active")
        self.start_input.setDate(QDate.currentDate())
        self.target_input.setDate(QDate.currentDate().addMonths(1))
        self.current_value_input.setText("0")
        self.target_value_input.setText("100")
        self.unit_input.clear()
        self.color_input.setText("#6366f1")
        self.progress_ring.set_ratio(0)
        self._clear_layout(self.milestones_layout)
        self.milestones_layout.addWidget(QLabel("Sem milestones."))
        self.milestones_layout.addStretch(1)

    def show_toast(self, message: str, kind: str = "info") -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[{kind}] {message}"})

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "goals"})

    def _validate_field(self, field: QLineEdit, is_valid: bool) -> bool:
        field.setProperty("invalid", not is_valid)
        field.style().unpolish(field)
        field.style().polish(field)
        return is_valid

    def _is_number(self, value: str) -> bool:
        try:
            float(value.replace(",", "."))
            return True
        except ValueError:
            return False

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.cards_wrapper = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_wrapper)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.cards_wrapper)
        content.addWidget(scroll, 1)
        content.addWidget(MilestoneList(), 0)
        layout.addLayout(content)

        self.form.save_button.clicked.connect(self._save_goal)
        self._reload()

    def _reload(self) -> None:
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        goals = self.controller.list_goals()
        if not goals:
            self.cards_layout.addWidget(EmptyState("Sem goals", "Crie a primeira meta para comecar."))
            return
        for goal in goals:
            self.cards_layout.addWidget(GoalCard(goal.title, goal.category or "Sem categoria", f"{goal.current_value}/{goal.target_value or 0}"))

    def _save_goal(self) -> None:
        title = self.form.title_input.text().strip()
        category = self.form.category_input.text().strip() or "geral"
        target = float(self.form.target_input.text().strip() or "0")
        if title:
            self.controller.create_goal(title, category, target)
            self.form.title_input.clear()
            self.form.category_input.clear()
            self.form.target_input.clear()
            self._reload()
