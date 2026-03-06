from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.modules.projects.controller import ProjectsController
from phoenix.modules.projects.widgets import KanbanBoard
from phoenix.utils.constants import Events


class ProjectsView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = ProjectsController()
        self.event_bus = event_bus
        self._current_project_id: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        controls = QHBoxLayout()
        self.project_selector = QComboBox()
        self.new_project_btn = QPushButton("+ Novo Projeto")
        self.new_project_btn.setObjectName("btn-secondary")
        self.new_task_btn = QPushButton("+ Nova Tarefa")
        self.new_task_btn.setObjectName("btn-primary")
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Kanban", "Lista"])
        controls.addWidget(QLabel("Projeto"))
        controls.addWidget(self.project_selector)
        controls.addWidget(self.new_project_btn)
        controls.addWidget(self.new_task_btn)
        controls.addStretch(1)
        controls.addWidget(self.mode_selector)
        layout.addLayout(controls)

        self.mode_stack = QStackedWidget()
        self.board = KanbanBoard()
        self.board.taskMoved.connect(self._move_task)
        self.list_table = QTableWidget(0, 6)
        self.list_table.setHorizontalHeaderLabels(["ID", "Titulo", "Status", "Prioridade", "Prazo", "Projeto"])
        self.mode_stack.addWidget(self.board)
        self.mode_stack.addWidget(self.list_table)
        layout.addWidget(self.mode_stack, 1)

        self.project_selector.currentIndexChanged.connect(self._on_project_changed)
        self.new_project_btn.clicked.connect(self._create_project)
        self.new_task_btn.clicked.connect(self._create_task)
        self.mode_selector.currentIndexChanged.connect(self._toggle_mode)
        self.refresh()

    def refresh(self) -> None:
        projects = self.controller.get_all_projects()
        self.project_selector.blockSignals(True)
        current_data = self.project_selector.currentData()
        self.project_selector.clear()
        for project in projects:
            self.project_selector.addItem(project.name, project.id)
        if current_data is not None:
            index = self.project_selector.findData(current_data)
            if index >= 0:
                self.project_selector.setCurrentIndex(index)
        self.project_selector.blockSignals(False)

        if self.project_selector.count() > 0 and self._current_project_id is None:
            self._current_project_id = int(self.project_selector.currentData())
        self._reload_tasks()

    def _reload_tasks(self) -> None:
        if self._current_project_id is None:
            self.board.populate([])
            self.list_table.setRowCount(0)
            return
        tasks = self.controller.get_tasks(self._current_project_id)
        self.board.populate(tasks)

        self.list_table.setRowCount(0)
        project_name = self.project_selector.currentText()
        for task in tasks:
            row = self.list_table.rowCount()
            self.list_table.insertRow(row)
            self.list_table.setItem(row, 0, QTableWidgetItem(str(task.id)))
            self.list_table.setItem(row, 1, QTableWidgetItem(task.title))
            self.list_table.setItem(row, 2, QTableWidgetItem(task.status))
            self.list_table.setItem(row, 3, QTableWidgetItem(task.priority))
            self.list_table.setItem(row, 4, QTableWidgetItem(task.due_date.strftime("%d/%m/%Y") if task.due_date else "-"))
            self.list_table.setItem(row, 5, QTableWidgetItem(project_name))

    def _on_project_changed(self) -> None:
        if self.project_selector.count() == 0:
            self._current_project_id = None
        else:
            self._current_project_id = int(self.project_selector.currentData())
        self._reload_tasks()

    def _toggle_mode(self) -> None:
        self.mode_stack.setCurrentIndex(0 if self.mode_selector.currentText() == "Kanban" else 1)

    def _create_project(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Novo projeto")
        form = QFormLayout(dialog)
        name = QLineEdit()
        color = QLineEdit("#8b5cf6")
        form.addRow("Nome", name)
        form.addRow("Cor", color)
        save = QPushButton("Salvar")
        save.clicked.connect(dialog.accept)
        form.addRow(save)
        if dialog.exec() == 0:
            return
        if not name.text().strip():
            return
        project = self.controller.create_project({"name": name.text().strip(), "color": color.text().strip() or "#8b5cf6"})
        self._current_project_id = project.id
        self.show_toast("Projeto criado.", kind="success")
        self._publish_data_changed()
        self.refresh()

    def _create_task(self) -> None:
        if self._current_project_id is None:
            self.show_toast("Crie ou selecione um projeto primeiro.", kind="warning")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Nova tarefa")
        form = QFormLayout(dialog)
        title = QLineEdit()
        status = QComboBox()
        status.addItems(["backlog", "todo", "in_progress", "review", "done"])
        priority = QComboBox()
        priority.addItems(["low", "medium", "high"])
        due_date = QDateEdit()
        due_date.setCalendarPopup(True)
        due_date.setDate(QDate.currentDate())
        form.addRow("Titulo", title)
        form.addRow("Status", status)
        form.addRow("Prioridade", priority)
        form.addRow("Prazo", due_date)
        save = QPushButton("Salvar")
        save.clicked.connect(dialog.accept)
        form.addRow(save)
        if dialog.exec() == 0:
            return
        if not title.text().strip():
            return
        self.controller.create_task(
            {
                "project_id": self._current_project_id,
                "title": title.text().strip(),
                "status": status.currentText(),
                "priority": priority.currentText(),
                "due_date": due_date.date().toPyDate(),
            }
        )
        self.show_toast("Tarefa criada.", kind="success")
        self._publish_data_changed()
        self._reload_tasks()

    def _move_task(self, task_id: int, status: str, position: int) -> None:
        self.controller.move_task(task_id, status, position)
        self._publish_data_changed()
        self._reload_tasks()

    def show_toast(self, message: str, kind: str = "info") -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[{kind}] {message}"})

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "projects"})
