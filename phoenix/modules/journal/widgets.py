from __future__ import annotations

from calendar import monthrange
from datetime import date

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QLineEdit, QPushButton, QToolBar, QVBoxLayout, QWidget

from phoenix.ui.widgets.rich_editor import RichEditor


MOOD_COLORS = {
    1: "#ef4444",
    2: "#f97316",
    3: "#f59e0b",
    4: "#84cc16",
    5: "#10b981",
}


class CalendarStrip(QWidget):
    day_selected = pyqtSignal(date)

    def __init__(self) -> None:
        super().__init__()
        self._year = date.today().year
        self._month = date.today().month
        self._calendar_data: dict[int, dict[str, bool | int | None]] = {}
        self.setMinimumHeight(180)

    def set_month(self, year: int, month: int) -> None:
        self._year = year
        self._month = month
        self.update()

    def set_calendar_data(self, calendar_data: dict[int, dict[str, bool | int | None]]) -> None:
        self._calendar_data = calendar_data
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        days = monthrange(self._year, self._month)[1]
        cols = 7
        cell_w = max(self.width() // cols, 24)
        cell_h = 28
        for idx in range(days):
            day = idx + 1
            row = idx // cols
            col = idx % cols
            x_pos = col * cell_w
            y_pos = row * cell_h
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(x_pos + 6, y_pos + 17, str(day))
            marker = self._calendar_data.get(day)
            if marker and marker.get("has_entry"):
                mood = int(marker.get("mood") or 3)
                painter.setBrush(QColor(MOOD_COLORS.get(mood, "#6366f1")))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(x_pos + cell_w - 12, y_pos + 8, 6, 6)


class EntryEditor(RichEditor):
    pass


class MoodSelector(QWidget):
    changed = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        self.group = QButtonGroup(self)
        for mood in range(1, 6):
            button = QPushButton(str(mood))
            button.setCheckable(True)
            button.setStyleSheet(f"background: {MOOD_COLORS[mood]}; color: #f8fafc; border-radius: 10px;")
            self.group.addButton(button, mood)
            layout.addWidget(button)
        self.group.idClicked.connect(self.changed.emit)

    def value(self) -> int:
        value = self.group.checkedId()
        return value if value > 0 else 3


class TagChipInput(QWidget):
    changed = pyqtSignal(list)

    def __init__(self) -> None:
        super().__init__()
        self._tags: list[str] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Tags (Enter ou virgula)")
        self.input.returnPressed.connect(self._consume_input)
        self.input.textChanged.connect(self._consume_on_comma)
        row.addWidget(self.input)
        layout.addLayout(row)
        self.chips_row = QHBoxLayout()
        layout.addLayout(self.chips_row)

    def tags(self) -> list[str]:
        return list(self._tags)

    def set_tags(self, tags: list[str] | None) -> None:
        self._tags = list(tags or [])
        self._refresh_chips()

    def _consume_on_comma(self, text: str) -> None:
        if "," in text:
            self._consume_input()

    def _consume_input(self) -> None:
        raw = self.input.text().replace(",", " ").strip()
        if not raw:
            return
        for chunk in raw.split():
            tag = chunk.strip()
            if tag and tag not in self._tags:
                self._tags.append(tag)
        self.input.clear()
        self._refresh_chips()
        self.changed.emit(self.tags())

    def _refresh_chips(self) -> None:
        while self.chips_row.count():
            item = self.chips_row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for tag in self._tags:
            chip = QLabel(tag)
            chip.setObjectName("tag")
            self.chips_row.addWidget(chip)
        self.chips_row.addStretch(1)


class RichToolbar(QToolBar):
    def __init__(self) -> None:
        super().__init__("Formatacao")
        for action_label in ["Negrito", "Italico", "H1", "H2", "Lista", "Codigo", "Linha"]:
            self.addAction(action_label)
