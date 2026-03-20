from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from dynaconf import Dynaconf
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import select

from phoenix.core.database import DATABASE_PATH, db_operation_class, get_session
from phoenix.core.models import Budget, Transaction
from phoenix.core.repository import Repository

SETTINGS = Dynaconf(settings_files=[str(DATABASE_PATH.parent / "settings.toml")])


@db_operation_class
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
        with open(file_path, "r", encoding="utf-8") as handler:
            reader = csv.DictReader(handler)
            mappings: list[dict[str, object]] = []
            for row in reader:
                parsed_date = datetime.strptime(row["data"], "%Y-%m-%d").date()
                mappings.append(
                    {
                        "title": row["descricao"],
                        "amount": float(row["valor"]),
                        "type": row["tipo"],
                        "category": row.get("categoria", "Outros"),
                        "account": SETTINGS.get("finance.default_account", "Principal"),
                        "date": parsed_date,
                        "note": row.get("nota") or None,
                    }
                )
        return self._bulk_insert_transactions(mappings)

    def import_ofx(self, file_path: str) -> int:
        """Importa transacoes de OFX usando parser leve por tags SGML."""

        content = Path(file_path).read_text(encoding="latin-1", errors="ignore")
        mappings: list[dict[str, object]] = []
        transactions = re.findall(r"<STMTTRN>(.*?)</STMTTRN>", content, flags=re.IGNORECASE | re.DOTALL)
        for block in transactions:
            amount_match = re.search(r"<TRNAMT>([^<\n\r]+)", block, flags=re.IGNORECASE)
            date_match = re.search(r"<DTPOSTED>(\d{8})", block, flags=re.IGNORECASE)
            memo_match = re.search(r"<MEMO>([^<\n\r]+)", block, flags=re.IGNORECASE)
            type_match = re.search(r"<TRNTYPE>([^<\n\r]+)", block, flags=re.IGNORECASE)
            if not amount_match or not date_match:
                continue
            amount = float(amount_match.group(1).replace(",", "."))
            tx_date = datetime.strptime(date_match.group(1), "%Y%m%d").date()
            trn_type = (type_match.group(1).strip().lower() if type_match else "debit")
            normalized_type = "income" if trn_type in {"credit", "dep", "int"} or amount > 0 else "expense"
            mappings.append(
                {
                    "title": (memo_match.group(1).strip() if memo_match else "Lancamento OFX")[:200],
                    "amount": abs(amount),
                    "type": normalized_type,
                    "category": "Outros",
                    "account": SETTINGS.get("finance.default_account", "Principal"),
                    "date": tx_date,
                    "note": "Importado via OFX",
                }
            )
        return self._bulk_insert_transactions(mappings)

    def import_file(self, file_path: str) -> int:
        """Importa movimentacoes por extensao suportada (CSV/OFX)."""

        suffix = Path(file_path).suffix.lower()
        if suffix == ".ofx":
            return self.import_ofx(file_path)
        if suffix == ".csv":
            return self.import_csv(file_path)
        raise ValueError("Formato nao suportado. Use CSV ou OFX.")

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

    def generate_monthly_pdf_if_due(self) -> str | None:
        """Gera automaticamente relatorio mensal unico por mes corrente."""

        reports_dir = DATABASE_PATH.parent / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        marker = reports_dir / ".last_monthly_report"
        current_key = date.today().strftime("%Y-%m")
        if marker.exists() and marker.read_text(encoding="utf-8").strip() == current_key:
            return None
        destination = reports_dir / f"extrato-{current_key}.pdf"
        self.export_monthly_pdf(str(destination), period="mes")
        marker.write_text(current_key, encoding="utf-8")
        return str(destination)

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

    def _bulk_insert_transactions(self, mappings: list[dict[str, object]]) -> int:
        """Insere transacoes em lote para reduzir overhead de ORM por registro."""

        if not mappings:
            return 0
        with get_session() as session:
            session.bulk_insert_mappings(Transaction, mappings)
            session.flush()
        return len(mappings)
