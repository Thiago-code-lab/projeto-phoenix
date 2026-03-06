from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from dynaconf import Dynaconf
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import select

from phoenix.core.database import DATABASE_PATH, get_session
from phoenix.core.models import Budget, Transaction
from phoenix.core.database import get_session
from phoenix.core.repository import Repository

SETTINGS = Dynaconf(settings_files=[str(DATABASE_PATH.parent / "settings.toml")])


class FinancesController:
    def list_transactions(
        self,
        period: str = "mes",
        tx_type: str = "Todos",
        category: str = "Todas",
        start: date | None = None,
        end: date | None = None,
    ) -> list[Transaction]:
        start_date, end_date = self._resolve_period(period, start, end)
        with get_session() as session:
            transactions = list(
                session.scalars(
                    select(Transaction).where(Transaction.date >= start_date, Transaction.date <= end_date).order_by(Transaction.date.desc())
                ).all()
            )
            if tx_type != "Todos":
                transactions = [tx for tx in transactions if tx.type == tx_type]
            if category != "Todas":
                transactions = [tx for tx in transactions if (tx.category or "Outros") == category]
            return transactions

    def create_transaction(
        self,
        title: str,
        amount: float,
        tx_type: str,
        category: str,
        account: str,
        tx_date: date,
        note: str = "",
    ) -> Transaction:
        with get_session() as session:
            return Repository(session, Transaction).add(
                title=title,
                amount=amount,
                type=tx_type,
                category=category,
                account=account,
                date=tx_date,
                note=note,
            )

    def summary_cards(self) -> dict[str, float]:
        today = date.today()
        month_start = today.replace(day=1)
        with get_session() as session:
            transactions = Repository(session, Transaction).list_all()
            income = sum(tx.amount for tx in transactions if tx.type == "income" and tx.date >= month_start)
            expense = sum(tx.amount for tx in transactions if tx.type == "expense" and tx.date >= month_start)
            balance = sum(tx.amount for tx in transactions if tx.type == "income") - sum(
                tx.amount for tx in transactions if tx.type == "expense"
            )
            return {
                "balance": round(balance, 2),
                "income": round(income, 2),
                "expense": round(expense, 2),
                "savings": round(income - expense, 2),
            }

    def budget_progress(self) -> list[dict[str, float | str]]:
        today = date.today()
        month_start = today.replace(day=1)
        with get_session() as session:
            budgets = Repository(session, Budget).list_all()
            transactions = list(
                session.scalars(
                    select(Transaction).where(Transaction.type == "expense", Transaction.date >= month_start)
                ).all()
            )
            progress: list[dict[str, float | str]] = []
            for budget in budgets:
                spent = sum(tx.amount for tx in transactions if (tx.category or "Outros") == budget.category)
                progress.append(
                    {
                        "category": budget.category,
                        "spent": round(spent, 2),
                        "limit": round(budget.amount, 2),
                        "ratio": min(spent / budget.amount, 1.0) if budget.amount else 0.0,
                    }
                )
            return progress

    def cash_flow_last_six_months(self) -> tuple[list[str], list[float], list[float]]:
        labels: list[str] = []
        incomes: list[float] = []
        expenses: list[float] = []
        today = date.today().replace(day=1)
        with get_session() as session:
            transactions = Repository(session, Transaction).list_all()
            for offset in range(5, -1, -1):
                month_start = (today - timedelta(days=offset * 31)).replace(day=1)
                next_month = (month_start + timedelta(days=32)).replace(day=1)
                labels.append(month_start.strftime("%b/%y"))
                month_transactions = [tx for tx in transactions if month_start <= tx.date < next_month]
                incomes.append(sum(tx.amount for tx in month_transactions if tx.type == "income"))
                expenses.append(sum(tx.amount for tx in month_transactions if tx.type == "expense"))
        return labels, incomes, expenses

    def category_distribution(self) -> tuple[list[str], list[float]]:
        today = date.today()
        month_start = today.replace(day=1)
        categories: dict[str, float] = defaultdict(float)
        with get_session() as session:
            transactions = session.scalars(
                select(Transaction).where(Transaction.type == "expense", Transaction.date >= month_start)
            ).all()
            for tx in transactions:
                categories[tx.category or "Outros"] += tx.amount
        return list(categories.keys()), list(categories.values())

    def net_worth_trend(self) -> tuple[list[str], list[float]]:
        labels: list[str] = []
        values: list[float] = []
        running = 0.0
        with get_session() as session:
            for tx in session.scalars(select(Transaction).order_by(Transaction.date.asc())).all():
                running += tx.amount if tx.type == "income" else -tx.amount if tx.type == "expense" else 0
                labels.append(tx.date.strftime("%d/%m"))
                values.append(round(running, 2))
        if not labels:
            return [date.today().strftime("%d/%m")], [0.0]
        return labels[-12:], values[-12:]

    def import_csv(self, file_path: str) -> int:
        imported = 0
        with open(file_path, "r", encoding="utf-8") as handler:
            reader = csv.DictReader(handler)
            for row in reader:
                parsed_date = datetime.strptime(row["data"], "%Y-%m-%d").date()
                self.create_transaction(
                    title=row["descricao"],
                    amount=float(row["valor"]),
                    tx_type=row["tipo"],
                    category=row.get("categoria", "Outros"),
                    account=SETTINGS.get("finance.default_account", "Principal"),
                    tx_date=parsed_date,
                )
                imported += 1
        return imported

    def export_monthly_pdf(self, output_path: str, period: str = "mes") -> str:
        transactions = self.list_transactions(period=period)
        styles = getSampleStyleSheet()
        document = SimpleDocTemplate(output_path, pagesize=A4)
        story = [Paragraph("Extrato Phoenix", styles["Title"]), Spacer(1, 16)]
        rows = [["Data", "Descricao", "Categoria", "Tipo", "Valor"]]
        for tx in transactions:
            rows.append([
                tx.date.strftime("%d/%m/%Y"),
                tx.title,
                tx.category or "Outros",
                tx.type,
                f"R$ {tx.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            ])
        table = Table(rows, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#18181b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#2e2e33")),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ]
            )
        )
        story.append(table)
        document.build(story)
        return output_path

    def add_category(self, category: str, kind: str) -> list[str]:
        key = "finance.categories_income" if kind == "income" else "finance.categories_expense"
        categories = list(SETTINGS.get(key, []))
        if category and category not in categories:
            categories.append(category)
            SETTINGS.set(key, categories)
        return categories

    def list_categories(self, tx_type: str | None = None) -> list[str]:
        if tx_type == "income":
            return list(SETTINGS.get("finance.categories_income", []))
        if tx_type == "expense":
            return list(SETTINGS.get("finance.categories_expense", []))
        return sorted(set(self.list_categories("income") + self.list_categories("expense")))

    def _resolve_period(self, period: str, start: date | None, end: date | None) -> tuple[date, date]:
        today = date.today()
        if period == "semana":
            start_date = today - timedelta(days=today.weekday())
            return start_date, today
        if period == "ano":
            return today.replace(month=1, day=1), today
        if period == "personalizado" and start and end:
            return start, end
        return today.replace(day=1), today
