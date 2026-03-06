from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QMimeData, QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QDrag, QMouseEvent
from PyQt6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from phoenix.core.models import Task
from phoenix.ui.widgets.chart_widget import ChartWidget
from phoenix.ui.widgets.card import CardWidget


class TaskCard(QFrame):
    def __init__(self, task: Task, project_name: str | None = None) -> None:
        super().__init__()
        self.task = task
        self.setObjectName("task-card")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._drag_start: QPoint | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel(task.title)
        title.setWordWrap(True)
        title.setMaximumHeight(38)
        layout.addWidget(title)

        meta = QHBoxLayout()
        badge = QLabel(task.priority.capitalize())
        badge.setObjectName("tag")
        if task.priority == "high":
            badge.setStyleSheet("color: #ef4444;")
        elif task.priority == "medium":
            badge.setStyleSheet("color: #f59e0b;")
        meta.addWidget(badge)

        due_text = task.due_date.strftime("%d/%m") if task.due_date else "Sem prazo"
        due_label = QLabel(due_text)
        if task.due_date and task.due_date < date.today():
            due_label.setStyleSheet("color: #ef4444;")
        meta.addWidget(due_label)
        meta.addStretch(1)
        layout.addLayout(meta)

        tags = QHBoxLayout()
        for tag in (task.tags or [])[:3]:
            tag_label = QLabel(tag)
            tag_label.setObjectName("tag")
            tags.addWidget(tag_label)
        tags.addStretch(1)
        layout.addLayout(tags)

        project_indicator = QLabel(project_name or "Projeto local")
        project_indicator.setStyleSheet(f"border-left: 4px solid {getattr(task.project, 'color', '#6366f1')}; padding-left: 8px;")
        layout.addWidget(project_indicator)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_start is None:
            return
        if (event.pos() - self._drag_start).manhattanLength() <= 10:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(str(self.task.id))
        drag.setMimeData(mime)
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        drag.exec(Qt.DropAction.MoveAction)


class TaskForm(CardWidget):
    def __init__(self) -> None:
        super().__init__("Nova task")
        from PyQt6.QtWidgets import QComboBox, QLineEdit, QPushButton

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Titulo da tarefa")
        self.priority_input = QComboBox()
        self.priority_input.addItems(["low", "medium", "high"])
        self.save_button = QPushButton("Adicionar")
        self.save_button.setObjectName("btn-primary")
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(self.priority_input)
        self.layout.addWidget(self.save_button)


class GanttChart(ChartWidget):
    pass


class ProjectSelector(QComboBox):
    def __init__(self) -> None:
        super().__init__()
        self.addItems(["Todos", "Pessoal", "Estudos", "Trabalho"])


class KanbanColumn(QFrame):
    taskDropped = pyqtSignal(int, str, int)

    def __init__(self, title: str, status: str) -> None:
        super().__init__()
        self.status = status
        self.setObjectName("kanban-column")
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(8)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("kanban-column-title")
        self.layout.addWidget(self.title_label)
        self.placeholder = QLabel("Solte aqui")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.hide()
        self.layout.addWidget(self.placeholder)
        self._drop_position = 0

    def clear_cards(self) -> None:
        while self.layout.count() > 1:
            item = self.layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_card(self, card: TaskCard) -> None:
        self.layout.addWidget(card)

    def dragEnterEvent(self, event) -> None:  # type: ignore[override]
        if event.mimeData().hasText():
            self.placeholder.show()
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:  # type: ignore[override]
        card_index = self._index_from_position(int(event.position().y()))
        self._drop_position = card_index
        event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:  # type: ignore[override]
        self.placeholder.hide()
        super().dragLeaveEvent(event)

    def dropEvent(self, event) -> None:  # type: ignore[override]
        self.placeholder.hide()
        task_id = int(event.mimeData().text())
        position = max(self._drop_position, 0)
        self.taskDropped.emit(task_id, self.status, position)
        event.acceptProposedAction()

    def _index_from_position(self, y_pos: int) -> int:
        index = 0
        for idx in range(1, self.layout.count()):
            item = self.layout.itemAt(idx)
            widget = item.widget()
            if widget is None or widget is self.placeholder:
                continue
            if y_pos < widget.y() + (widget.height() // 2):
                return index
            index += 1
        return index


class KanbanBoard(QWidget):
    taskMoved = pyqtSignal(int, str, int)

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.columns: list[KanbanColumn] = []
        self._mapping = [
            ("Backlog", "backlog"),
            ("A fazer", "todo"),
            ("Em andamento", "in_progress"),
            ("Revisao", "review"),
            ("Concluido", "done"),
        ]
        for title, status in self._mapping:
            column = KanbanColumn(title, status)
            column.taskDropped.connect(self.taskMoved.emit)
            layout.addWidget(column)
            self.columns.append(column)

    def populate(self, tasks: list[Task]) -> None:
        grouped: dict[str, list[Task]] = {status: [] for _, status in self._mapping}
        for task in tasks:
            grouped.setdefault(task.status, []).append(task)
        for column in self.columns:
            column.clear_cards()
            for task in sorted(grouped.get(column.status, []), key=lambda item: item.position):
                column.add_card(TaskCard(task, getattr(task.project, "name", None)))
