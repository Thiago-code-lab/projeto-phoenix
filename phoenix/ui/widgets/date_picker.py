from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QDateEdit


class DatePicker(QDateEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setCalendarPopup(True)
        self.setDate(QDate.currentDate())
        self.setDisplayFormat("dd/MM/yyyy")
