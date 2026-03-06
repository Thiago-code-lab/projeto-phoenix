from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QComboBox, QDateEdit, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar

from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.chart_widget import ChartWidget


class TransactionForm(CardWidget):
    def __init__(self) -> None:
        super().__init__("Nova transacao")
        form = QFormLayout()
        self.title_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["income", "expense", "transfer"])
        self.category_input = QComboBox()
        self.account_input = QLineEdit("Principal")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.note_input = QLineEdit()
        form.addRow("Titulo", self.title_input)
        form.addRow("Valor", self.amount_input)
        form.addRow("Tipo", self.type_input)
        form.addRow("Categoria", self.category_input)
        form.addRow("Conta", self.account_input)
        form.addRow("Data", self.date_input)
        form.addRow("Nota", self.note_input)
        self.save_button = QPushButton("Salvar")
        self.save_button.setObjectName("btn-primary")
        self.layout.addLayout(form)
        self.layout.addWidget(self.save_button)


class CategoryPie(ChartWidget):
    pass


class BudgetProgressItem(CardWidget):
    def __init__(self, category: str, spent: float, limit: float, ratio: float) -> None:
        super().__init__(category)
        self.progress = QProgressBar()
        self.progress.setValue(int(ratio * 100))
        self.meta = QLabel(f"R$ {spent:.2f} / R$ {limit:.2f}")
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
