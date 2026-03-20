from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar

from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.chart_widget import ChartWidget
from phoenix.ui.widgets.validated_fields import FormValidator, ValidatedDateEdit, ValidatedLineEdit


class TransactionForm(CardWidget):
    def __init__(self) -> None:
        super().__init__("Nova transacao")
        form = QFormLayout()
        self.title_input = ValidatedLineEdit()
        self.title_input.set_required(True)
        self.title_input.setObjectName("finance_title")
        self.amount_input = ValidatedLineEdit()
        self.amount_input.set_required(True)
        self.amount_input.setObjectName("finance_amount")
        self.amount_input.add_rule(self._positive_number_rule)
        self.type_input = QComboBox()
        self.type_input.addItems(["income", "expense", "transfer"])
        self.category_input = QComboBox()
        self.account_input = ValidatedLineEdit("Principal")
        self.account_input.setObjectName("finance_account")
        self.date_input = ValidatedDateEdit()
        self.date_input.set_allow_future(False)
        self.date_input.setObjectName("finance_date")
        self.date_input.setDate(QDate.currentDate())
        self.note_input = ValidatedLineEdit()
        self.note_input.setObjectName("finance_note")
        form.addRow("Titulo", self.title_input)
        form.addRow("", self.title_input.error_label)
        form.addRow("Valor", self.amount_input)
        form.addRow("", self.amount_input.error_label)
        form.addRow("Tipo", self.type_input)
        form.addRow("Categoria", self.category_input)
        form.addRow("Conta", self.account_input)
        form.addRow("", self.account_input.error_label)
        form.addRow("Data", self.date_input)
        form.addRow("", self.date_input.error_label)
        form.addRow("Nota", self.note_input)
        form.addRow("", self.note_input.error_label)
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: #ef4444; font-size: 12px;")
        self.save_button = QPushButton("Salvar")
        self.save_button.setObjectName("btn-primary")
        self.validator = FormValidator(
            [
                self.title_input,
                self.amount_input,
                self.account_input,
                self.date_input,
                self.note_input,
            ],
            self,
        )
        self.validator.bind_submit_button(self.save_button)
        self.title_input.textChanged.connect(lambda _: self.validator.is_valid())
        self.amount_input.textChanged.connect(lambda _: self.validator.is_valid())
        self.account_input.textChanged.connect(lambda _: self.validator.is_valid())
        self.note_input.textChanged.connect(lambda _: self.validator.is_valid())
        self.layout.addLayout(form)
        self.layout.addWidget(self.validation_label)
        self.layout.addWidget(self.save_button)

    def _positive_number_rule(self, value: object) -> tuple[bool, str]:
        try:
            parsed = float(str(value).replace(",", "."))
        except ValueError:
            return False, "Valor deve ser numerico."
        if parsed <= 0:
            return False, "Valor deve ser maior que zero."
        return True, ""


class CategoryPie(ChartWidget):
    pass


class BudgetProgressItem(CardWidget):
    def __init__(self, category: str, spent: float, limit: float, ratio: float) -> None:
        super().__init__(category)
        self.progress = QProgressBar()
        self.progress.setValue(int(ratio * 100))
        alert = ""
        if ratio >= 1:
            alert = " | Limite estourado"
            self.progress.setStyleSheet("QProgressBar::chunk { background: #ef4444; }")
        elif ratio >= 0.8:
            alert = " | Alerta 80%"
            self.progress.setStyleSheet("QProgressBar::chunk { background: #f59e0b; }")
        self.meta = QLabel(f"R$ {spent:.2f} / R$ {limit:.2f}{alert}")
        self.layout.addWidget(self.meta)
        self.layout.addWidget(self.progress)


class CashFlowChart(ChartWidget):
    pass


class FiltersBar(CardWidget):
    def __init__(self) -> None:
        super().__init__("Filtros")
        row = QHBoxLayout()
        self.period = QComboBox()
        self.period.addItems(["semana", "mes", "ano", "personalizado"])
        self.tx_type = QComboBox()
        self.tx_type.addItems(["Todos", "income", "expense", "transfer"])
        self.category = QComboBox()
        self.category.addItem("Todas")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        row.addWidget(self.period)
        row.addWidget(self.tx_type)
        row.addWidget(self.category)
        row.addWidget(self.start_date)
        row.addWidget(self.end_date)
        self.layout.addLayout(row)
