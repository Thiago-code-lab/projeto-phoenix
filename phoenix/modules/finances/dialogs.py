from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QComboBox, QDateEdit, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLineEdit, QTextEdit


class TransactionDialog(QDialog):
    def __init__(
        self,
        categories: list[str],
        accounts: list[str],
        payload: dict[str, object] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Transacao")
        self.setModal(True)

        form = QFormLayout(self)

        self.title_input = QLineEdit()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(999999999.0)
        self.amount_input.setDecimals(2)
        self.type_input = QComboBox()
        self.type_input.addItems(["income", "expense", "transfer"])

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(categories or ["Outros"])

        self.account_input = QComboBox()
        self.account_input.setEditable(True)
        self.account_input.addItems(accounts or ["Principal"])

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(90)

        form.addRow("Titulo", self.title_input)
        form.addRow("Valor", self.amount_input)
        form.addRow("Tipo", self.type_input)
        form.addRow("Categoria", self.category_input)
        form.addRow("Conta", self.account_input)
        form.addRow("Data", self.date_input)
        form.addRow("Nota", self.note_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        form.addRow(self.buttons)

        if payload:
            self._load_payload(payload)

    def _load_payload(self, payload: dict[str, object]) -> None:
        self.title_input.setText(str(payload.get("title", "")))
        self.amount_input.setValue(float(payload.get("amount", 0.0)))
        tx_type = str(payload.get("type", "expense"))
        self.type_input.setCurrentText(tx_type)
        self.category_input.setCurrentText(str(payload.get("category", "Outros")))
        self.account_input.setCurrentText(str(payload.get("account", "Principal")))
        tx_date = payload.get("date")
        if isinstance(tx_date, date):
            self.date_input.setDate(QDate(tx_date.year, tx_date.month, tx_date.day))
        self.note_input.setPlainText(str(payload.get("note", "")))

    def payload(self) -> dict[str, object]:
        return {
            "title": self.title_input.text().strip(),
            "amount": float(self.amount_input.value()),
            "type": self.type_input.currentText(),
            "category": self.category_input.currentText().strip() or "Outros",
            "account": self.account_input.currentText().strip() or "Principal",
            "date": self.date_input.date().toPyDate(),
            "note": self.note_input.toPlainText().strip(),
        }


class BudgetDialog(QDialog):
    def __init__(self, payload: dict[str, object] | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Orcamento")
        self.setModal(True)

        form = QFormLayout(self)

        self.category_input = QLineEdit()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(999999999.0)
        self.amount_input.setDecimals(2)

        self.period_input = QComboBox()
        self.period_input.addItems(["monthly", "yearly"])

        form.addRow("Categoria", self.category_input)
        form.addRow("Limite", self.amount_input)
        form.addRow("Periodo", self.period_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        form.addRow(self.buttons)

        if payload:
            self.category_input.setText(str(payload.get("category", "")))
            self.amount_input.setValue(float(payload.get("limit", 0.0)))

    def payload(self) -> dict[str, object]:
        return {
            "category": self.category_input.text().strip(),
            "amount": float(self.amount_input.value()),
            "period": self.period_input.currentText(),
        }
