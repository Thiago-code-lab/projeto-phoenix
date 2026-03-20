from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
)

from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.donut_chart import DonutChart
from phoenix.ui.widgets.finance_bar_chart import FinanceBarChart


class TransactionFilters(CardWidget):
    def __init__(self) -> None:
        super().__init__("Filtros")
        row = QHBoxLayout()
        row.setSpacing(8)

        self.period = QComboBox()
        self.period.addItems(["semana", "mes", "trimestre", "ano", "personalizado"])

        self.tx_type = QComboBox()
        self.tx_type.addItems(["Todos", "income", "expense", "transfer"])

        self.category = QComboBox()
        self.category.addItem("Todas")

        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar descricao, categoria ou nota")

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        self.apply_button = QPushButton("Aplicar")
        self.apply_button.setObjectName("btn-secondary")

        row.addWidget(self.period)
        row.addWidget(self.tx_type)
        row.addWidget(self.category)
        row.addWidget(self.search, 1)
        row.addWidget(self.start_date)
        row.addWidget(self.end_date)
        row.addWidget(self.apply_button)
        self.layout.addLayout(row)


class TransactionTable(QTableWidget):
    headers = ["ID", "Data", "Descricao", "Categoria", "Tipo", "Conta", "Valor"]

    def __init__(self) -> None:
        super().__init__(0, len(self.headers))
        self.setObjectName("finance-table")
        self.setHorizontalHeaderLabels(self.headers)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSortingEnabled(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnHidden(0, True)

    def set_rows(self, rows: list[dict[str, Any]], currency_fn) -> None:
        self.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                str(row["id"]),
                str(row["date"]),
                str(row["title"]),
                str(row["category"]),
                str(row["type"]),
                str(row["account"]),
                currency_fn(float(row["amount"])),
            ]
            for col_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col_index == 6:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.setItem(row_index, col_index, item)

    def selected_transaction_id(self) -> int | None:
        indexes = self.selectionModel().selectedRows()
        if not indexes:
            return None
        raw = self.item(indexes[0].row(), 0)
        if raw is None:
            return None
        try:
            return int(raw.text())
        except ValueError:
            return None


class BudgetProgressCard(CardWidget):
    def __init__(self, category: str, spent: float, limit: float, ratio: float, status: str) -> None:
        super().__init__(category)
        self.meta = QLabel(f"Gasto: R$ {spent:.2f} | Limite: R$ {limit:.2f}")
        self.meta.setObjectName("label-muted")
        self.progress = QProgressBar()
        self.progress.setValue(min(100, int(ratio * 100)))
        self.status_label = QLabel(status.upper())
        self.status_label.setObjectName("finance-status")

        if status == "exceeded":
            self.progress.setStyleSheet("QProgressBar::chunk { background: #ef4444; }")
        elif status == "warning":
            self.progress.setStyleSheet("QProgressBar::chunk { background: #f59e0b; }")

        self.layout.addWidget(self.meta)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.status_label)


class ImportReviewTable(QTableWidget):
    headers = ["Data", "Descricao", "Tipo", "Categoria", "Valor", "Duplicada"]

    def __init__(self) -> None:
        super().__init__(0, len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)

    def set_review_rows(self, rows: list[dict[str, Any]]) -> None:
        self.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                str(row["date"]),
                str(row["title"]),
                str(row["type"]),
                str(row["category"]),
                f"R$ {float(row['amount']):.2f}",
                "SIM" if bool(row.get("duplicate")) else "NAO",
            ]
            for col_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col_index == 5 and value == "SIM":
                    item.setForeground(Qt.GlobalColor.red)
                self.setItem(row_index, col_index, item)


# Compatibilidade com o modulo antigo
CategoryPie = DonutChart
CashFlowChart = FinanceBarChart
