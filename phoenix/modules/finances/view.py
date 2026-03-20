from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.modules.finances.controller import FinancesController
from phoenix.modules.finances.dialogs import BudgetDialog, TransactionDialog
from phoenix.modules.finances.widgets import BudgetProgressCard, ImportReviewTable, TransactionFilters, TransactionTable
from phoenix.ui.widgets.alert_banner import AlertBanner
from phoenix.ui.widgets.donut_chart import DonutChart
from phoenix.ui.widgets.drop_zone import DropZone
from phoenix.ui.widgets.finance_bar_chart import FinanceBarChart
from phoenix.ui.widgets.line_chart import LineChart
from phoenix.ui.widgets.summary_card import SummaryCard
from phoenix.utils.constants import Events


class FinancesView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = FinancesController()
        self.event_bus = event_bus
        self._import_rows: list[dict[str, Any]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.banner = AlertBanner("Modulo financeiro pronto", "success")
        self.banner.hide()
        layout.addWidget(self.banner)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("finance-tabs")
        layout.addWidget(self.tabs)

        self.overview_tab = QWidget()
        self.transactions_tab = QWidget()
        self.budgets_tab = QWidget()
        self.analytics_tab = QWidget()
        self.import_export_tab = QWidget()

        self.tabs.addTab(self.overview_tab, "Visao Geral")
        self.tabs.addTab(self.transactions_tab, "Transacoes")
        self.tabs.addTab(self.budgets_tab, "Orcamentos")
        self.tabs.addTab(self.analytics_tab, "Analises")
        self.tabs.addTab(self.import_export_tab, "Importar/Exportar")

        self._build_overview_tab()
        self._build_transactions_tab()
        self._build_budgets_tab()
        self._build_analytics_tab()
        self._build_import_export_tab()
        self.refresh()

    def _build_overview_tab(self) -> None:
        root = QVBoxLayout(self.overview_tab)
        root.setSpacing(12)

        cards_row = QHBoxLayout()
        self.balance_card = SummaryCard("Saldo", "R$ 0,00", "Consolidado")
        self.income_card = SummaryCard("Receitas", "R$ 0,00", "Mes atual")
        self.expense_card = SummaryCard("Despesas", "R$ 0,00", "Mes atual")
        self.savings_card = SummaryCard("Economia", "R$ 0,00", "Mes atual")

        for card in [self.balance_card, self.income_card, self.expense_card, self.savings_card]:
            cards_row.addWidget(card)
        root.addLayout(cards_row)

        charts_row = QHBoxLayout()
        self.overview_flow_chart = FinanceBarChart()
        self.overview_category_chart = DonutChart()
        charts_row.addWidget(self.overview_flow_chart, 1)
        charts_row.addWidget(self.overview_category_chart, 1)
        root.addLayout(charts_row)

    def _build_transactions_tab(self) -> None:
        root = QVBoxLayout(self.transactions_tab)
        root.setSpacing(10)

        self.filters = TransactionFilters()
        root.addWidget(self.filters)

        controls = QHBoxLayout()
        self.new_transaction_button = QPushButton("Nova transacao")
        self.new_transaction_button.setObjectName("btn-primary")
        self.edit_transaction_button = QPushButton("Editar")
        self.edit_transaction_button.setObjectName("btn-secondary")
        self.delete_transaction_button = QPushButton("Excluir")
        self.delete_transaction_button.setObjectName("btn-danger")

        controls.addWidget(self.new_transaction_button)
        controls.addWidget(self.edit_transaction_button)
        controls.addWidget(self.delete_transaction_button)
        controls.addStretch(1)
        root.addLayout(controls)

        self.transactions_table = TransactionTable()
        root.addWidget(self.transactions_table, 1)

        self.filters.apply_button.clicked.connect(self._reload_transactions)
        self.filters.period.currentTextChanged.connect(lambda _: self._reload_transactions())
        self.filters.tx_type.currentTextChanged.connect(lambda _: self._reload_categories())
        self.filters.search.textChanged.connect(lambda _: self._reload_transactions())

        self.new_transaction_button.clicked.connect(self._create_transaction)
        self.edit_transaction_button.clicked.connect(self._edit_selected_transaction)
        self.delete_transaction_button.clicked.connect(self._delete_selected_transaction)

    def _build_budgets_tab(self) -> None:
        root = QVBoxLayout(self.budgets_tab)
        root.setSpacing(10)

        actions = QHBoxLayout()
        self.new_budget_button = QPushButton("Novo orcamento")
        self.new_budget_button.setObjectName("btn-primary")
        actions.addWidget(self.new_budget_button)
        actions.addStretch(1)
        root.addLayout(actions)

        self.budgets_scroll = QScrollArea()
        self.budgets_scroll.setWidgetResizable(True)
        self.budgets_container = QWidget()
        self.budgets_layout = QVBoxLayout(self.budgets_container)
        self.budgets_layout.setSpacing(10)
        self.budgets_scroll.setWidget(self.budgets_container)
        root.addWidget(self.budgets_scroll)

        self.new_budget_button.clicked.connect(self._create_budget)

    def _build_analytics_tab(self) -> None:
        root = QVBoxLayout(self.analytics_tab)
        root.setSpacing(12)

        top_row = QHBoxLayout()
        self.analytics_cash_flow = FinanceBarChart()
        self.analytics_distribution = DonutChart()
        top_row.addWidget(self.analytics_cash_flow, 1)
        top_row.addWidget(self.analytics_distribution, 1)
        root.addLayout(top_row)

        self.analytics_equity = LineChart()
        root.addWidget(self.analytics_equity)

    def _build_import_export_tab(self) -> None:
        root = QVBoxLayout(self.import_export_tab)
        root.setSpacing(12)

        self.drop_zone = DropZone()
        root.addWidget(self.drop_zone)

        controls = QHBoxLayout()
        self.select_file_button = QPushButton("Selecionar arquivo")
        self.select_file_button.setObjectName("btn-secondary")
        self.import_button = QPushButton("Importar aprovadas")
        self.import_button.setObjectName("btn-primary")
        self.export_pdf_button = QPushButton("Exportar PDF")
        self.export_pdf_button.setObjectName("btn-secondary")
        controls.addWidget(self.select_file_button)
        controls.addWidget(self.import_button)
        controls.addWidget(self.export_pdf_button)
        controls.addStretch(1)
        root.addLayout(controls)

        self.import_summary = QLabel("Nenhum arquivo analisado")
        self.import_summary.setObjectName("label-muted")
        root.addWidget(self.import_summary)

        self.import_review_table = ImportReviewTable()
        root.addWidget(self.import_review_table, 1)

        self.drop_zone.fileDropped.connect(self._review_file)
        self.select_file_button.clicked.connect(self._select_and_review_file)
        self.import_button.clicked.connect(self._import_reviewed_rows)
        self.export_pdf_button.clicked.connect(self._export_pdf)

    def refresh(self) -> None:
        summary = self.controller.get_monthly_summary()
        self.balance_card.update_data(self._currency(summary["balance"]), "Consolidado")
        self.income_card.update_data(self._currency(summary["income"]), self._variation_label(summary["income_variation"]))
        self.expense_card.update_data(self._currency(summary["expense"]), self._variation_label(summary["expense_variation"]))
        self.savings_card.update_data(self._currency(summary["savings"]), self._variation_label(summary["savings_variation"]))

        labels, incomes, expenses, _ = self.controller.monthly_evolution(months=6)
        self.overview_flow_chart.plot_grouped_bar(
            labels,
            [("Receitas", incomes, "#10b981"), ("Despesas", expenses, "#ef4444")],
        )

        categories, values = self.controller.category_breakdown()
        self.overview_category_chart.plot_pie(categories, values, ["#f59e0b", "#10b981", "#ef4444", "#0891b2", "#6366f1"])

        self._reload_categories()
        self._reload_transactions()
        self._reload_budgets()
        self._reload_analytics()

    def _reload_transactions(self) -> None:
        rows = self.controller.list_transactions_advanced(
            period=self.filters.period.currentText(),
            tx_type=self.filters.tx_type.currentText(),
            category=self.filters.category.currentText(),
            start=self.filters.start_date.date().toPyDate(),
            end=self.filters.end_date.date().toPyDate(),
            search=self.filters.search.text(),
        )
        mapped = [
            {
                "id": tx.id,
                "date": tx.date.strftime("%d/%m/%Y"),
                "title": tx.title,
                "category": tx.category or "Outros",
                "type": tx.type,
                "account": tx.account or "Principal",
                "amount": tx.amount,
                "note": tx.note or "",
            }
            for tx in rows
        ]
        self.transactions_table.set_rows(mapped, self._currency)

    def _reload_budgets(self) -> None:
        while self.budgets_layout.count():
            child = self.budgets_layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

        budgets = self.controller.get_budget_status()
        if not budgets:
            empty = QLabel("Nenhum orcamento cadastrado")
            empty.setObjectName("label-muted")
            self.budgets_layout.addWidget(empty)
            self.budgets_layout.addStretch(1)
            return

        for item in budgets:
            card = BudgetProgressCard(
                str(item["category"]),
                float(item["spent"]),
                float(item["limit"]),
                float(item["ratio"]),
                str(item["status"]),
            )
            self.budgets_layout.addWidget(card)
        self.budgets_layout.addStretch(1)

    def _reload_analytics(self) -> None:
        labels, incomes, expenses, _ = self.controller.monthly_evolution(months=6)
        self.analytics_cash_flow.plot_grouped_bar(
            labels,
            [("Receitas", incomes, "#10b981"), ("Despesas", expenses, "#ef4444")],
        )
        categories, values = self.controller.category_breakdown()
        self.analytics_distribution.plot_pie(categories, values, ["#f59e0b", "#10b981", "#ef4444", "#0891b2", "#6366f1"])
        equity_labels, equity_values = self.controller.patrimonial_evolution(months=12)
        self.analytics_equity.plot_line(equity_labels, equity_values, color="#f39c12", fill=True)

    def _reload_categories(self) -> None:
        current_type = self.filters.tx_type.currentText()
        if current_type in {"income", "expense"}:
            categories = self.controller.list_categories(current_type)
        else:
            categories = self.controller.list_categories()

        selected = self.filters.category.currentText()
        self.filters.category.blockSignals(True)
        self.filters.category.clear()
        self.filters.category.addItem("Todas")
        self.filters.category.addItems(categories)
        if selected:
            self.filters.category.setCurrentText(selected)
        self.filters.category.blockSignals(False)

    def _create_transaction(self) -> None:
        dialog = TransactionDialog(self.controller.list_categories(), self._accounts())
        if dialog.exec() == dialog.DialogCode.Accepted:
            payload = dialog.payload()
            self.controller.save_transaction(**payload)
            self._notify("Transacao criada", "success")
            self._publish_data_changed()
            self.refresh()

    def _edit_selected_transaction(self) -> None:
        transaction_id = self.transactions_table.selected_transaction_id()
        if transaction_id is None:
            self._notify("Selecione uma transacao", "warning")
            return

        selected = self.controller.list_transactions_advanced(
            period=self.filters.period.currentText(),
            tx_type=self.filters.tx_type.currentText(),
            category=self.filters.category.currentText(),
            start=self.filters.start_date.date().toPyDate(),
            end=self.filters.end_date.date().toPyDate(),
            search=self.filters.search.text(),
        )
        target = next((tx for tx in selected if tx.id == transaction_id), None)
        if target is None:
            self._notify("Transacao nao encontrada", "error")
            return

        dialog = TransactionDialog(
            self.controller.list_categories(),
            self._accounts(),
            payload={
                "title": target.title,
                "amount": target.amount,
                "type": target.type,
                "category": target.category or "Outros",
                "account": target.account or "Principal",
                "date": target.date,
                "note": target.note or "",
            },
        )
        if dialog.exec() == dialog.DialogCode.Accepted:
            payload = dialog.payload()
            payload["transaction_id"] = transaction_id
            self.controller.save_transaction(**payload)
            self._notify("Transacao atualizada", "success")
            self._publish_data_changed()
            self.refresh()

    def _delete_selected_transaction(self) -> None:
        transaction_id = self.transactions_table.selected_transaction_id()
        if transaction_id is None:
            self._notify("Selecione uma transacao", "warning")
            return
        self.controller.delete_transaction(transaction_id)
        self._notify("Transacao removida", "success")
        self._publish_data_changed()
        self.refresh()

    def _create_budget(self) -> None:
        dialog = BudgetDialog(parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            payload = dialog.payload()
            if not payload["category"] or float(payload["amount"]) <= 0:
                self._notify("Categoria e limite valido sao obrigatorios", "warning")
                return
            self.controller.set_budget(
                str(payload["category"]),
                float(payload["amount"]),
                period=str(payload["period"]),
            )
            self._notify("Orcamento salvo", "success")
            self._publish_data_changed()
            self.refresh()

    def _select_and_review_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo", "", "Arquivos (*.csv *.ofx)")
        if file_path:
            self._review_file(file_path)

    def _review_file(self, file_path: str) -> None:
        try:
            result = self.controller.review_import(file_path)
        except Exception as exc:  # noqa: BLE001
            self._notify(f"Falha ao analisar arquivo: {exc}", "error")
            return

        self._import_rows = list(result["rows"])
        self.import_review_table.set_review_rows(self._import_rows)
        self.import_summary.setText(
            f"Arquivo: {Path(file_path).name} | Total: {result['total']} | Novas: {result['new']} | Duplicadas: {result['duplicates']}"
        )
        self._notify("Revisao de importacao concluida", "info")

    def _import_reviewed_rows(self) -> None:
        if not self._import_rows:
            self._notify("Nenhuma linha para importar", "warning")
            return
        result = self.controller.import_reviewed_transactions(self._import_rows, skip_duplicates=True)
        self._notify(f"Importadas: {result['inserted']} | Ignoradas: {result['skipped']}", "success")
        self._publish_data_changed()
        self.refresh()

    def _export_pdf(self) -> None:
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar PDF",
            str(Path.home() / "relatorio_financeiro_phoenix.pdf"),
            "PDF (*.pdf)",
        )
        if not output_path:
            return
        try:
            destination = self.controller.export_monthly_pdf(output_path, period=self.filters.period.currentText())
            self._notify(f"PDF exportado em {destination}", "success")
        except Exception as exc:  # noqa: BLE001
            self._notify(f"Falha ao exportar PDF: {exc}", "error")

    def _accounts(self) -> list[str]:
        rows = self.controller.list_transactions_advanced(period="ano")
        accounts = sorted({(tx.account or "Principal") for tx in rows})
        return accounts or ["Principal"]

    def _notify(self, message: str, level: str = "info") -> None:
        self.banner.set_message(message, level)
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": message})

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "finances"})

    def _currency(self, value: float) -> str:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _variation_label(self, value: float) -> str:
        sign = "+" if value >= 0 else ""
        return f"{sign}{value:.1f}% vs mes anterior"
