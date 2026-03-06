from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QInputDialog, QPushButton, QTabWidget, QVBoxLayout, QWidget

from phoenix.core.events import EventBus
from phoenix.modules.finances.controller import FinancesController
from phoenix.modules.finances.widgets import BudgetProgressItem, CashFlowChart, CategoryPie, FiltersBar, TransactionForm
from phoenix.ui.workers import WorkerThread
from phoenix.ui.widgets.card import CardWidget
from phoenix.ui.widgets.empty_state import EmptyState
from phoenix.ui.widgets.stat_card import StatCard
from phoenix.ui.widgets.table_widget import DataTableWidget
from phoenix.utils.constants import Events
from phoenix.utils.validators import validate_positive_number, validate_required


class FinancesView(QWidget):
    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = FinancesController()
        self.event_bus = event_bus
        self._workers: list[WorkerThread] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.summary_tab = QWidget()
        self.transactions_tab = QWidget()
        self.budgets_tab = QWidget()
        self.charts_tab = QWidget()
        self.tabs.addTab(self.summary_tab, "Resumo")
        self.tabs.addTab(self.transactions_tab, "Transacoes")
        self.tabs.addTab(self.budgets_tab, "Orcamentos")
        self.tabs.addTab(self.charts_tab, "Graficos")

        self._build_summary_tab()
        self._build_transactions_tab()
        self._build_budgets_tab()
        self._build_charts_tab()
        self.refresh()

    def _build_summary_tab(self) -> None:
        layout = QVBoxLayout(self.summary_tab)
        grid = QHBoxLayout()
        self.balance_card = StatCard("Saldo total", "R$ 0,00", "")
        self.income_card = StatCard("Receita do mes", "R$ 0,00", "")
        self.expense_card = StatCard("Despesa do mes", "R$ 0,00", "")
        self.savings_card = StatCard("Economia do mes", "R$ 0,00", "")
        for card in [self.balance_card, self.income_card, self.expense_card, self.savings_card]:
            grid.addWidget(card)
        layout.addLayout(grid)

        charts = QHBoxLayout()
        self.summary_flow_chart = CashFlowChart()
        self.summary_category_chart = CategoryPie()
        charts.addWidget(self.summary_flow_chart, 1)
        charts.addWidget(self.summary_category_chart, 1)
        layout.addLayout(charts)

    def _build_transactions_tab(self) -> None:
        layout = QVBoxLayout(self.transactions_tab)
        self.filters = FiltersBar()
        layout.addWidget(self.filters)
        controls = QHBoxLayout()
        self.import_button = QPushButton("Importar CSV")
        self.import_button.setObjectName("btn-secondary")
        self.export_button = QPushButton("Exportar PDF")
        self.export_button.setObjectName("btn-secondary")
        self.category_button = QPushButton("Nova categoria")
        self.category_button.setObjectName("btn-secondary")
        controls.addWidget(self.import_button)
        controls.addWidget(self.export_button)
        controls.addWidget(self.category_button)
        controls.addStretch(1)
        layout.addLayout(controls)

        self.form = TransactionForm()
        layout.addWidget(self.form)
        self.table = DataTableWidget()
        layout.addWidget(self.table)
        self.empty_state = EmptyState("Sem transacoes", "Adicione uma transacao ou importe um CSV para visualizar movimentos.", "Nova transacao")
        self.empty_state.action_button.clicked.connect(lambda: self.form.title_input.setFocus())
        layout.addWidget(self.empty_state)
        self.empty_state.hide()

        self.filters.period.currentTextChanged.connect(lambda _: self._reload())
        self.filters.tx_type.currentTextChanged.connect(self._on_type_changed)
        self.filters.category.currentTextChanged.connect(lambda _: self._reload())
        self.filters.start_date.dateChanged.connect(lambda _: self._reload())
        self.filters.end_date.dateChanged.connect(lambda _: self._reload())
        self.form.save_button.clicked.connect(self._save)
        self.import_button.clicked.connect(self._import_csv)
        self.export_button.clicked.connect(self._export_pdf)
        self.category_button.clicked.connect(self._add_category)

    def _build_budgets_tab(self) -> None:
        self.budgets_layout = QVBoxLayout(self.budgets_tab)
        self.budgets_layout.setSpacing(12)

    def _build_charts_tab(self) -> None:
        layout = QHBoxLayout(self.charts_tab)
        self.pie_chart = CategoryPie()
        self.flow_chart = CashFlowChart()
        self.net_worth_chart = CashFlowChart()
        layout.addWidget(self.pie_chart, 1)
        layout.addWidget(self.flow_chart, 1)
        layout.addWidget(self.net_worth_chart, 1)

    def refresh(self) -> None:
        summary = self.controller.summary_cards()
        self.balance_card.update_values(self._currency(summary["balance"]), "+saldo consolidado")
        self.income_card.update_values(self._currency(summary["income"]), "+entrada no periodo")
        self.expense_card.update_values(self._currency(summary["expense"]), "-saida no periodo")
        self.savings_card.update_values(self._currency(summary["savings"]), "+economia liquida")

        labels, incomes, expenses = self.controller.cash_flow_last_six_months()
        self.summary_flow_chart.plot_grouped_bar(labels, [("Receitas", incomes, "#10b981"), ("Despesas", expenses, "#ef4444")])
        category_labels, category_values = self.controller.category_distribution()
        self.summary_category_chart.plot_pie(category_labels, category_values, ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#0891b2"])
        self.flow_chart.plot_grouped_bar(labels, [("Receitas", incomes, "#10b981"), ("Despesas", expenses, "#ef4444")])
        self.pie_chart.plot_pie(category_labels, category_values, ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#0891b2"])
        net_labels, net_values = self.controller.net_worth_trend()
        self.net_worth_chart.plot_line(net_labels, net_values, color="#6366f1", fill=True)
        self._reload_categories()
        self._reload()
        self._reload_budgets()

    def _reload(self) -> None:
        start = self.filters.start_date.date().toPyDate()
        end = self.filters.end_date.date().toPyDate()
        rows = []
        for transaction in self.controller.list_transactions(
            period=self.filters.period.currentText(),
            tx_type=self.filters.tx_type.currentText(),
            category=self.filters.category.currentText(),
            start=start,
            end=end,
        ):
            rows.append([
                transaction.date.strftime("%d/%m/%Y"),
                transaction.title,
                transaction.category or "Outros",
                transaction.type,
                self._currency(transaction.amount),
            ])
        self.table.set_data(["Data", "Descricao", "Categoria", "Tipo", "Valor"], rows)
        self.table.setVisible(bool(rows))
        self.empty_state.setVisible(not rows)

    def _save(self) -> None:
        title = self.form.title_input.text().strip()
        amount_text = self.form.amount_input.text().strip()
        tx_type = self.form.type_input.currentText()
        category = self.form.category_input.currentText() or "Outros"
        account = self.form.account_input.text().strip() or "Principal"
        note = self.form.note_input.text().strip()
        tx_date = self.form.date_input.date().toPyDate()

        try:
            validate_required(title, "Titulo")
            amount = float(amount_text.replace(",", "."))
            validate_positive_number(amount, "Valor")
        except ValueError as exc:
            self._publish_toast(str(exc))
            return

        self.controller.create_transaction(title, amount, tx_type, category, account, tx_date, note)
        self.form.title_input.clear()
        self.form.amount_input.clear()
        self.form.note_input.clear()
        self.refresh()
        self._publish_toast("Transacao salva com sucesso.")
        self._publish_data_changed()

    def _reload_budgets(self) -> None:
        while self.budgets_layout.count():
            item = self.budgets_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for budget in self.controller.budget_progress():
            self.budgets_layout.addWidget(
                BudgetProgressItem(
                    str(budget["category"]),
                    float(budget["spent"]),
                    float(budget["limit"]),
                    float(budget["ratio"]),
                )
            )
        self.budgets_layout.addStretch(1)

    def _reload_categories(self) -> None:
        current_type = self.form.type_input.currentText()
        categories = self.controller.list_categories("income" if current_type == "income" else "expense")
        self.form.category_input.clear()
        self.form.category_input.addItems(categories or ["Outros"])
        self.filters.category.clear()
        self.filters.category.addItem("Todas")
        self.filters.category.addItems(self.controller.list_categories())

    def _on_type_changed(self, value: str) -> None:
        self._reload_categories()
        self._reload()

    def _import_csv(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Importar CSV", "", "CSV (*.csv)")
        if not file_path:
            return
        self._run_worker(
            self.controller.import_csv,
            file_path,
            success_message=lambda imported: f"{imported} transacoes adicionadas.",
        )

    def _export_pdf(self) -> None:
        output_path, _ = QFileDialog.getSaveFileName(self, "Exportar PDF", str(Path.home() / "extrato_phoenix.pdf"), "PDF (*.pdf)")
        if not output_path:
            return
        self._run_worker(
            self.controller.export_monthly_pdf,
            output_path,
            self.filters.period.currentText(),
            success_message=lambda result: f"Extrato salvo em {result}.",
            refresh_after=False,
        )

    def _add_category(self) -> None:
        category, ok = QInputDialog.getText(self, "Nova categoria", "Nome da categoria:")
        if not ok or not category.strip():
            return
        kind = self.form.type_input.currentText()
        self.controller.add_category(category.strip(), "income" if kind == "income" else "expense")
        self._reload_categories()
        self._publish_toast("Categoria adicionada.")

    def _run_worker(
        self,
        task,
        *args: object,
        success_message,
        refresh_after: bool = True,
    ) -> None:
        worker = WorkerThread(task, *args)
        worker.completed.connect(lambda result: self._handle_worker_success(worker, result, success_message, refresh_after))
        worker.failed.connect(lambda message: self._handle_worker_failure(worker, message))
        self._workers.append(worker)
        worker.start()
        self._publish_toast("Processando em segundo plano...")

    def _handle_worker_success(self, worker: WorkerThread, result: object, success_message, refresh_after: bool) -> None:
        self._dispose_worker(worker)
        if refresh_after:
            self.refresh()
            self._publish_data_changed()
        self._publish_toast(str(success_message(result)))

    def _handle_worker_failure(self, worker: WorkerThread, message: str) -> None:
        self._dispose_worker(worker)
        self._publish_toast(f"Falha: {message}")

    def _dispose_worker(self, worker: WorkerThread) -> None:
        if worker in self._workers:
            self._workers.remove(worker)
        worker.deleteLater()

    def _publish_data_changed(self) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "finances"})

    def _publish_toast(self, message: str) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(Events.SHOW_TOAST, {"message": message})

    def _currency(self, value: float) -> str:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
