from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QDate
from PyQt6.QtGui import QKeySequence, QShortcut, QUndoCommand, QUndoStack
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
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
from phoenix.ui.widgets.validated_fields import FormValidator, ValidatedDateEdit, ValidatedLineEdit, ValidatedSpinBox
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
        self.title_input = ValidatedLineEdit()
        self.title_input.set_required(True)
        self.title_input.setObjectName("goal_title")
        self.category_input = ValidatedLineEdit()
        self.category_input.setObjectName("goal_category")
        self.status_input = QComboBox()
        self.status_input.addItems(["active", "paused", "completed"])
        self.start_input = ValidatedDateEdit()
        self.start_input.setDate(QDate.currentDate())
        self.target_input = ValidatedDateEdit()
        self.target_input.setDate(QDate.currentDate().addMonths(1))
        self.current_value_input = ValidatedSpinBox()
        self.current_value_input.setDecimals(2)
        self.current_value_input.set_min_max(0, 1_000_000)
        self.current_value_input.setObjectName("goal_current")
        self.target_value_input = ValidatedSpinBox()
        self.target_value_input.setDecimals(2)
        self.target_value_input.set_min_max(0.01, 1_000_000)
        self.target_value_input.set_required(True)
        self.target_value_input.setValue(100)
        self.target_value_input.setObjectName("goal_target")
        self.unit_input = ValidatedLineEdit()
        self.unit_input.setObjectName("goal_unit")
        self.color_input = ValidatedLineEdit("#6366f1")
        self.color_input.setObjectName("goal_color")

        def add_validated_row(base_row: int, label_text: str, widget: object) -> int:
            form_grid.addWidget(QLabel(label_text), base_row, 0)
            form_grid.addWidget(widget, base_row, 1)
            if hasattr(widget, "error_label"):
                form_grid.addWidget(widget.error_label, base_row + 1, 1)
                return base_row + 2
            return base_row + 1

        row = 0
        row = add_validated_row(row, "Titulo", self.title_input)
        row = add_validated_row(row, "Categoria", self.category_input)
        form_grid.addWidget(QLabel("Status"), row, 0)
        form_grid.addWidget(self.status_input, row, 1)
        row += 1
        row = add_validated_row(row, "Inicio", self.start_input)
        row = add_validated_row(row, "Prazo", self.target_input)
        row = add_validated_row(row, "Atual", self.current_value_input)
        row = add_validated_row(row, "Meta", self.target_value_input)
        row = add_validated_row(row, "Unidade", self.unit_input)
        add_validated_row(row, "Cor", self.color_input)
        detail_layout.addLayout(form_grid)

        self.progress_ring = CircularProgress()
        detail_layout.addWidget(self.progress_ring)

        detail_layout.addWidget(QLabel("Milestones"))
        milestone_form = QHBoxLayout()
        self.milestone_title = ValidatedLineEdit()
        self.milestone_title.set_required(True)
        self.milestone_title.setObjectName("goal_milestone")
        self.milestone_title.setPlaceholderText("Novo milestone")
        self.milestone_date = ValidatedDateEdit()
        self.milestone_date.setDate(QDate.currentDate())
        self.milestone_add = QPushButton("Adicionar")
        self.milestone_add.setObjectName("btn-secondary")
        milestone_form.addWidget(self.milestone_title, 1)
        milestone_form.addWidget(self.milestone_date)
        milestone_form.addWidget(self.milestone_add)
        detail_layout.addLayout(milestone_form)
        detail_layout.addWidget(self.milestone_title.error_label)

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

        self.form_validator = FormValidator(
            [
                self.title_input,
                self.start_input,
                self.target_input,
                self.current_value_input,
                self.target_value_input,
                self.color_input,
            ],
            self,
        )
        self.form_validator.bind_submit_button(self.save_button)
        self.milestone_validator = FormValidator([self.milestone_title, self.milestone_date], self)
        self.milestone_validator.bind_submit_button(self.milestone_add)

    def _connect_signals(self) -> None:
        self.status_filter.currentTextChanged.connect(lambda _: self._load_data())
        self.category_filter.currentTextChanged.connect(lambda _: self._load_data())
        self.new_button.clicked.connect(self._new_goal)
        self.list_empty.action_button.clicked.connect(self._new_goal)
        self.save_button.clicked.connect(self._save_goal)
        self.delete_button.clicked.connect(self._delete_goal)
        self.milestone_add.clicked.connect(self._add_milestone)
        self.title_input.textChanged.connect(lambda _: self.form_validator.is_valid())
        self.current_value_input.valueChanged.connect(lambda _: self.form_validator.is_valid())
        self.target_value_input.valueChanged.connect(lambda _: self.form_validator.is_valid())
        self.color_input.textChanged.connect(lambda _: self.form_validator.is_valid())
        self.milestone_title.textChanged.connect(lambda _: self.milestone_validator.is_valid())

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
        self.target_value_input.setValue(goal.target_value or 0.0)
        self.current_value_input.setValue(goal.current_value or 0.0)
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
        if not self.form_validator.is_valid():
            self.show_toast("Corrija os campos destacados.", kind="error")
            return

        if self.target_input.date().toPyDate() < self.start_input.date().toPyDate():
            self.target_input._set_invalid("Prazo deve ser maior ou igual a data de inicio.")
            self.show_toast("Corrija os campos destacados.", kind="error")
            self.form_validator.is_valid()
            return

        payload = {
            "title": self.title_input.text().strip(),
            "category": self.category_input.text().strip() or "geral",
            "status": self.status_input.currentText(),
            "start_date": self.start_input.date().toPyDate(),
            "target_date": self.target_input.date().toPyDate(),
            "current_value": self.current_value_input.value(),
            "target_value": self.target_value_input.value(),
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
        if not self.milestone_validator.is_valid():
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
        self.current_value_input.setValue(0)
        self.target_value_input.setValue(100)
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

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
