from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select

from phoenix.core.database import DATABASE_PATH, db_operation_class, get_session
from phoenix.core.models import Budget, Transaction
from phoenix.core.repository import Repository

SETTINGS = Dynaconf(settings_files=[str(DATABASE_PATH.parent / "settings.toml")])


@db_operation_class
class FinancesController:
    def get_monthly_summary(self, reference: date | None = None) -> dict[str, float]:
        reference_date = reference or date.today()
        start, end = self._month_interval(reference_date)
        prev_start = (start - timedelta(days=1)).replace(day=1)
        prev_end = start - timedelta(days=1)

        current = self._sum_period(start, end)
        previous = self._sum_period(prev_start, prev_end)

        income_variation = self._variation(current["income"], previous["income"])
        expense_variation = self._variation(current["expense"], previous["expense"])
        savings_variation = self._variation(current["savings"], previous["savings"])

        return {
            "balance": current["balance"],
            "income": current["income"],
            "expense": current["expense"],
            "savings": current["savings"],
            "income_variation": income_variation,
            "expense_variation": expense_variation,
            "savings_variation": savings_variation,
        }

    def list_transactions_advanced(
        self,
        period: str = "mes",
        tx_type: str = "Todos",
        category: str = "Todas",
        start: date | None = None,
        end: date | None = None,
        search: str | None = None,
        account: str | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
    ) -> list[Transaction]:
        start_date, end_date = self._resolve_period(period, start, end)
        with get_session() as session:
            query = select(Transaction).where(Transaction.date >= start_date, Transaction.date <= end_date)
            records = list(session.scalars(query.order_by(Transaction.date.desc())).all())

        filtered = records
        if tx_type != "Todos":
            filtered = [tx for tx in filtered if tx.type == tx_type]
        if category != "Todas":
            filtered = [tx for tx in filtered if (tx.category or "Outros") == category]
        if account:
            filtered = [tx for tx in filtered if (tx.account or "") == account]
        if min_amount is not None:
            filtered = [tx for tx in filtered if tx.amount >= min_amount]
        if max_amount is not None:
            filtered = [tx for tx in filtered if tx.amount <= max_amount]
        if search:
            term = search.strip().lower()
            if term:
                filtered = [
                    tx
                    for tx in filtered
                    if term in tx.title.lower() or term in (tx.note or "").lower() or term in (tx.category or "").lower()
                ]
        return filtered

    def save_transaction(
        self,
        title: str,
        amount: float,
        tx_type: str,
        category: str,
        account: str,
        tx_date: date,
        note: str = "",
        transaction_id: int | None = None,
    ) -> Transaction:
        payload = {
            "title": title.strip(),
            "amount": abs(float(amount)),
            "type": tx_type,
            "category": category.strip() or "Outros",
            "account": account.strip() or "Principal",
            "date": tx_date,
            "note": note.strip() or None,
        }
        with get_session() as session:
            repo = Repository(session, Transaction)
            if transaction_id is None:
                return repo.add(**payload)
            target = repo.get(transaction_id)
            if target is None:
                raise ValueError("Transacao nao encontrada")
            return repo.update(transaction_id, **payload)

    def update_transaction(self, transaction_id: int, **payload: Any) -> Transaction:
        with get_session() as session:
            repo = Repository(session, Transaction)
            target = repo.get(transaction_id)
            if target is None:
                raise ValueError("Transacao nao encontrada")
            return repo.update(transaction_id, **payload)

    def delete_transaction(self, transaction_id: int) -> None:
        with get_session() as session:
            repo = Repository(session, Transaction)
            target = repo.get(transaction_id)
            if target is None:
                raise ValueError("Transacao nao encontrada")
            repo.delete(transaction_id)

    def set_budget(self, category: str, amount: float, period: str = "monthly", color: str = "#f59e0b") -> Budget:
        with get_session() as session:
            repo = Repository(session, Budget)
            existing = session.scalar(select(Budget).where(Budget.category == category, Budget.period == period))
            if existing is None:
                return repo.add(category=category, amount=float(amount), period=period, color=color, active=True)
            return repo.update(existing.id, amount=float(amount), color=color, active=True)

    def remove_budget(self, budget_id: int) -> None:
        with get_session() as session:
            repo = Repository(session, Budget)
            if repo.get(budget_id) is None:
                raise ValueError("Orcamento nao encontrado")
            repo.delete(budget_id)

    def get_budget_status(self, reference: date | None = None) -> list[dict[str, Any]]:
        reference_date = reference or date.today()
        start, end = self._month_interval(reference_date)
        with get_session() as session:
            budgets = list(session.scalars(select(Budget).where(Budget.active.is_(True))).all())
            expenses = list(
                session.scalars(
                    select(Transaction).where(
                        Transaction.type == "expense",
                        Transaction.date >= start,
                        Transaction.date <= end,
                    )
                ).all()
            )

        rows: list[dict[str, Any]] = []
        for budget in budgets:
            spent = sum(tx.amount for tx in expenses if (tx.category or "Outros") == budget.category)
            ratio = spent / budget.amount if budget.amount else 0.0
            status = "ok"
            if ratio >= 1:
                status = "exceeded"
            elif ratio >= 0.8:
                status = "warning"
            rows.append(
                {
                    "id": budget.id,
                    "category": budget.category,
                    "limit": round(float(budget.amount), 2),
                    "spent": round(float(spent), 2),
                    "remaining": round(float(max(budget.amount - spent, 0)), 2),
                    "ratio": round(float(ratio), 4),
                    "status": status,
                    "color": budget.color,
                }
            )
        return sorted(rows, key=lambda row: row["ratio"], reverse=True)

    def category_breakdown(self, reference: date | None = None) -> tuple[list[str], list[float]]:
        reference_date = reference or date.today()
        start, end = self._month_interval(reference_date)
        totals: dict[str, float] = defaultdict(float)
        with get_session() as session:
            expenses = session.scalars(
                select(Transaction).where(
                    Transaction.type == "expense",
                    Transaction.date >= start,
                    Transaction.date <= end,
                )
            ).all()
        for tx in expenses:
            totals[tx.category or "Outros"] += float(tx.amount)
        return list(totals.keys()), [round(value, 2) for value in totals.values()]

    def monthly_evolution(self, months: int = 6) -> tuple[list[str], list[float], list[float], list[float]]:
        labels: list[str] = []
        incomes: list[float] = []
        expenses: list[float] = []
        balances: list[float] = []

        today = date.today().replace(day=1)
        with get_session() as session:
            records = list(session.scalars(select(Transaction).order_by(Transaction.date.asc())).all())

        for offset in range(months - 1, -1, -1):
            month_start = (today - timedelta(days=offset * 31)).replace(day=1)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            month_records = [tx for tx in records if month_start <= tx.date < next_month]
            month_income = sum(tx.amount for tx in month_records if tx.type == "income")
            month_expense = sum(tx.amount for tx in month_records if tx.type == "expense")
            labels.append(month_start.strftime("%b/%y"))
            incomes.append(round(month_income, 2))
            expenses.append(round(month_expense, 2))
            balances.append(round(month_income - month_expense, 2))

        return labels, incomes, expenses, balances

    def patrimonial_evolution(self, months: int = 12) -> tuple[list[str], list[float]]:
        labels: list[str] = []
        values: list[float] = []
        running = 0.0

        with get_session() as session:
            records = list(session.scalars(select(Transaction).order_by(Transaction.date.asc())).all())

        checkpoints: list[tuple[str, date]] = []
        anchor = date.today().replace(day=1)
        for offset in range(months - 1, -1, -1):
            month_start = (anchor - timedelta(days=offset * 31)).replace(day=1)
            checkpoints.append((month_start.strftime("%b/%y"), month_start))

        for tx in records:
            if tx.type == "income":
                running += tx.amount
            elif tx.type == "expense":
                running -= tx.amount

        if not records:
            return [date.today().strftime("%b/%y")], [0.0]

        for label, month_start in checkpoints:
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            partial = 0.0
            for tx in records:
                if tx.date < month_end:
                    partial += tx.amount if tx.type == "income" else -tx.amount if tx.type == "expense" else 0.0
            labels.append(label)
            values.append(round(partial, 2))
        return labels, values

    def review_import(self, file_path: str) -> dict[str, Any]:
        parsed = self._parse_import_file(file_path)
        signatures = self._existing_signatures()
        reviewed: list[dict[str, Any]] = []
        duplicates = 0

        for row in parsed:
            signature = self._signature(row)
            is_duplicate = signature in signatures
            if is_duplicate:
                duplicates += 1
            reviewed.append(
                {
                    **row,
                    "duplicate": is_duplicate,
                }
            )

        return {
            "total": len(reviewed),
            "duplicates": duplicates,
            "new": len(reviewed) - duplicates,
            "rows": reviewed,
        }

    def import_reviewed_transactions(self, rows: list[dict[str, Any]], skip_duplicates: bool = True) -> dict[str, int]:
        signatures = self._existing_signatures()
        mappings: list[dict[str, Any]] = []
        skipped = 0

        for row in rows:
            signature = self._signature(row)
            if skip_duplicates and signature in signatures:
                skipped += 1
                continue
            mappings.append(
                {
                    "title": str(row["title"])[:200],
                    "amount": abs(float(row["amount"])),
                    "type": str(row["type"]),
                    "category": str(row.get("category") or "Outros"),
                    "account": str(row.get("account") or SETTINGS.get("finance.default_account", "Principal")),
                    "date": self._coerce_date(row["date"]),
                    "note": row.get("note"),
                }
            )
            signatures.add(signature)

        inserted = self._bulk_insert_transactions(mappings)
        return {"inserted": inserted, "skipped": skipped}

    def import_file(self, file_path: str) -> int:
        review = self.review_import(file_path)
        result = self.import_reviewed_transactions(review["rows"], skip_duplicates=True)
        return result["inserted"]

    def export_monthly_pdf(self, output_path: str, period: str = "mes") -> str:
        summary = self.get_monthly_summary()
        transactions = self.list_transactions_advanced(period=period)
        budgets = self.get_budget_status()

        styles = getSampleStyleSheet()
        document = SimpleDocTemplate(output_path, pagesize=A4)
        story: list[Any] = []

        story.append(Paragraph("Relatorio Financeiro Phoenix", styles["Title"]))
        story.append(Spacer(1, 12))

        summary_rows = [
            ["Indicador", "Valor"],
            ["Saldo", self._currency(summary["balance"])],
            ["Receitas", self._currency(summary["income"])],
            ["Despesas", self._currency(summary["expense"])],
            ["Economia", self._currency(summary["savings"])],
        ]
        story.append(self._styled_table(summary_rows, header_color="#111827"))
        story.append(Spacer(1, 18))

        budget_rows = [["Categoria", "Gasto", "Limite", "%", "Status"]]
        for budget in budgets:
            budget_rows.append(
                [
                    str(budget["category"]),
                    self._currency(float(budget["spent"])),
                    self._currency(float(budget["limit"])),
                    f"{float(budget['ratio']) * 100:.1f}%",
                    str(budget["status"]),
                ]
            )
        if len(budget_rows) > 1:
            story.append(Paragraph("Orcamentos", styles["Heading2"]))
            story.append(self._styled_table(budget_rows, header_color="#1f2937"))
            story.append(PageBreak())

        transaction_rows = [["Data", "Descricao", "Categoria", "Tipo", "Valor"]]
        for tx in transactions:
            transaction_rows.append(
                [
                    tx.date.strftime("%d/%m/%Y"),
                    tx.title,
                    tx.category or "Outros",
                    tx.type,
                    self._currency(float(tx.amount)),
                ]
            )
        story.append(Paragraph("Transacoes", styles["Heading2"]))
        story.append(self._styled_table(transaction_rows, header_color="#0f172a"))

        document.build(story)
        return output_path

    def generate_monthly_pdf_if_due(self) -> str | None:
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
        normalized = category.strip()
        if normalized and normalized not in categories:
            categories.append(normalized)
            SETTINGS.set(key, categories)
        return categories

    def list_categories(self, tx_type: str | None = None) -> list[str]:
        if tx_type == "income":
            return list(SETTINGS.get("finance.categories_income", []))
        if tx_type == "expense":
            return list(SETTINGS.get("finance.categories_expense", []))
        return sorted(set(self.list_categories("income") + self.list_categories("expense")))

    # Compatibilidade com a API antiga
    def list_transactions(
        self,
        period: str = "mes",
        tx_type: str = "Todos",
        category: str = "Todas",
        start: date | None = None,
        end: date | None = None,
    ) -> list[Transaction]:
        return self.list_transactions_advanced(period, tx_type, category, start, end)

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
        return self.save_transaction(title, amount, tx_type, category, account, tx_date, note)

    def summary_cards(self) -> dict[str, float]:
        return self.get_monthly_summary()

    def budget_progress(self) -> list[dict[str, float | str]]:
        rows = []
        for item in self.get_budget_status():
            rows.append(
                {
                    "category": str(item["category"]),
                    "spent": float(item["spent"]),
                    "limit": float(item["limit"]),
                    "ratio": float(item["ratio"]),
                }
            )
        return rows

    def cash_flow_last_six_months(self) -> tuple[list[str], list[float], list[float]]:
        labels, incomes, expenses, _ = self.monthly_evolution(months=6)
        return labels, incomes, expenses

    def category_distribution(self) -> tuple[list[str], list[float]]:
        return self.category_breakdown()

    def net_worth_trend(self) -> tuple[list[str], list[float]]:
        return self.patrimonial_evolution(months=12)

    def _sum_period(self, start: date, end: date) -> dict[str, float]:
        with get_session() as session:
            records = list(
                session.scalars(
                    select(Transaction).where(Transaction.date >= start, Transaction.date <= end)
                ).all()
            )
            all_records = list(session.scalars(select(Transaction)).all())

        income = sum(tx.amount for tx in records if tx.type == "income")
        expense = sum(tx.amount for tx in records if tx.type == "expense")
        balance = sum(tx.amount for tx in all_records if tx.type == "income") - sum(
            tx.amount for tx in all_records if tx.type == "expense"
        )
        return {
            "income": round(income, 2),
            "expense": round(expense, 2),
            "savings": round(income - expense, 2),
            "balance": round(balance, 2),
        }

    def _resolve_period(self, period: str, start: date | None, end: date | None) -> tuple[date, date]:
        today = date.today()
        if period == "semana":
            start_date = today - timedelta(days=today.weekday())
            return start_date, today
        if period == "ano":
            return today.replace(month=1, day=1), today
        if period == "trimestre":
            quarter = (today.month - 1) // 3
            quarter_start_month = quarter * 3 + 1
            return today.replace(month=quarter_start_month, day=1), today
        if period == "personalizado" and start and end:
            return start, end
        return today.replace(day=1), today

    def _month_interval(self, reference: date) -> tuple[date, date]:
        start = reference.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return start, end

    def _variation(self, current: float, previous: float) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / abs(previous)) * 100.0, 2)

    def _currency(self, value: float) -> str:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _styled_table(self, rows: list[list[str]], header_color: str) -> Table:
        table = Table(rows, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ]
            )
        )
        return table

    def _parse_import_file(self, file_path: str) -> list[dict[str, Any]]:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".csv":
            return self._parse_csv(file_path)
        if suffix == ".ofx":
            return self._parse_ofx(file_path)
        raise ValueError("Formato nao suportado. Use CSV ou OFX.")

    def _parse_csv(self, file_path: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        with open(file_path, "r", encoding="utf-8") as handler:
            reader = csv.DictReader(handler)
            for raw in reader:
                amount = float(str(raw.get("valor", "0")).replace(",", "."))
                parsed_date = self._coerce_date(raw.get("data") or date.today())
                tx_type = str(raw.get("tipo") or "expense").strip().lower()
                rows.append(
                    {
                        "title": str(raw.get("descricao") or "Lancamento importado")[:200],
                        "amount": abs(amount),
                        "type": tx_type if tx_type in {"income", "expense", "transfer"} else "expense",
                        "category": str(raw.get("categoria") or "Outros"),
                        "account": str(raw.get("conta") or SETTINGS.get("finance.default_account", "Principal")),
                        "date": parsed_date,
                        "note": raw.get("nota") or "Importado via CSV",
                    }
                )
        return rows

    def _parse_ofx(self, file_path: str) -> list[dict[str, Any]]:
        content = Path(file_path).read_text(encoding="latin-1", errors="ignore")
        blocks = re.findall(r"<STMTTRN>(.*?)</STMTTRN>", content, flags=re.IGNORECASE | re.DOTALL)
        rows: list[dict[str, Any]] = []
        for block in blocks:
            amount_match = re.search(r"<TRNAMT>([^<\n\r]+)", block, flags=re.IGNORECASE)
            date_match = re.search(r"<DTPOSTED>(\d{8})", block, flags=re.IGNORECASE)
            memo_match = re.search(r"<MEMO>([^<\n\r]+)", block, flags=re.IGNORECASE)
            type_match = re.search(r"<TRNTYPE>([^<\n\r]+)", block, flags=re.IGNORECASE)
            if not amount_match or not date_match:
                continue

            amount = float(amount_match.group(1).replace(",", "."))
            trn_type = (type_match.group(1).strip().lower() if type_match else "debit")
            normalized_type = "income" if trn_type in {"credit", "dep", "int"} or amount > 0 else "expense"
            rows.append(
                {
                    "title": (memo_match.group(1).strip() if memo_match else "Lancamento OFX")[:200],
                    "amount": abs(amount),
                    "type": normalized_type,
                    "category": "Outros",
                    "account": SETTINGS.get("finance.default_account", "Principal"),
                    "date": datetime.strptime(date_match.group(1), "%Y%m%d").date(),
                    "note": "Importado via OFX",
                }
            )
        return rows

    def _existing_signatures(self) -> set[str]:
        with get_session() as session:
            records = list(session.scalars(select(Transaction)).all())
        return {self._signature(tx) for tx in records}

    def _signature(self, row: Any) -> str:
        if isinstance(row, Transaction):
            tx_date = row.date
            title = row.title
            amount = row.amount
            tx_type = row.type
            account = row.account or ""
        else:
            tx_date = self._coerce_date(row["date"])
            title = str(row["title"])
            amount = float(row["amount"])
            tx_type = str(row["type"])
            account = str(row.get("account") or "")
        return f"{tx_date.isoformat()}|{title.strip().lower()}|{abs(amount):.2f}|{tx_type}|{account.strip().lower()}"

    def _coerce_date(self, value: Any) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        text = str(value).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Data invalida: {value}")

    def _bulk_insert_transactions(self, mappings: list[dict[str, Any]]) -> int:
        if not mappings:
            return 0
        with get_session() as session:
            session.bulk_insert_mappings(Transaction, mappings)
            session.flush()
        return len(mappings)
