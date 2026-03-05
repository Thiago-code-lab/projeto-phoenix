from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import Database, get_setting, soft_delete
from utils.formatters import format_currency


def render() -> None:
    st.markdown("<h1 class='module-title'>💰 Finanças</h1>", unsafe_allow_html=True)
    st.markdown("<p class='module-subtitle'>Receitas, despesas, orçamento por categoria e visão mensal.</p>", unsafe_allow_html=True)

    db = Database()
    currency = get_setting("currency", "R$")

    with st.expander("+ Nova categoria", expanded=False):
        with st.form("cat_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Nome")
            cat_type = c2.selectbox("Tipo", ["expense", "income"])
            budget = c3.number_input("Orçamento limite", min_value=0.0, value=0.0)
            icon = st.text_input("Ícone", value="💳")
            color = st.color_picker("Cor", value="#6c63ff")
            if st.form_submit_button("Salvar categoria") and name.strip():
                db.execute(
                    """
                    INSERT INTO finance_categories(name, type, icon, color, budget_limit, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (name, cat_type, icon, color, budget, datetime.now().isoformat(), datetime.now().isoformat()),
                )
                st.rerun()

    categories = db.query("SELECT * FROM finance_categories WHERE deleted_at IS NULL ORDER BY name")

    with st.form("tx_form", clear_on_submit=True):
        st.markdown("### Novo lançamento")
        c1, c2, c3, c4 = st.columns(4)
        tx_type = c1.selectbox("Tipo", ["expense", "income"])
        amount = c2.number_input("Valor", min_value=0.0, value=0.0)
        tx_date = c3.date_input("Data", value=date.today())
        recurrence = c4.selectbox("Recorrência", ["none", "monthly", "weekly"])
        matching_categories = [c for c in categories if c["type"] == tx_type] if categories else []
        cat_label = st.selectbox("Categoria", ["Sem categoria"] + [f"{c['id']} - {c['name']}" for c in matching_categories])
        description = st.text_input("Descrição")
        if st.form_submit_button("Adicionar") and amount > 0:
            cat_id = None if cat_label == "Sem categoria" else int(cat_label.split(" - ")[0])
            db.execute(
                """
                INSERT INTO transactions(type, amount, category_id, description, date, recurrence, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tx_type,
                    amount,
                    cat_id,
                    description,
                    tx_date.isoformat(),
                    None if recurrence == "none" else recurrence,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            st.success("Lançamento registrado.")
            st.rerun()

    tx = db.query(
        """
        SELECT t.*, COALESCE(c.name, 'Sem categoria') AS category_name, COALESCE(c.budget_limit, 0) AS budget_limit
        FROM transactions t
        LEFT JOIN finance_categories c ON c.id = t.category_id
        WHERE t.deleted_at IS NULL
        ORDER BY t.date DESC, t.id DESC
        """
    )

    if not tx:
        st.info("Sem lançamentos ainda.")
        return

    frame = pd.DataFrame(tx)
    month_mask = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")
    month_df = frame[month_mask]
    income = month_df.loc[month_df["type"] == "income", "amount"].sum()
    expense = month_df.loc[month_df["type"] == "expense", "amount"].sum()
    saldo = income - expense

    m1, m2, m3 = st.columns(3)
    m1.markdown(f"<div style='background:linear-gradient(135deg,#7b3fa0,#5c2d8a);padding:14px;border-radius:14px;'><div class='phx-label'>Saldo do mês</div><h3>{format_currency(float(saldo), currency)}</h3></div>", unsafe_allow_html=True)
    m2.markdown(f"<div style='background:linear-gradient(135deg,#f5a623,#f07020);padding:14px;border-radius:14px;'><div class='phx-label'>Receitas</div><h3>{format_currency(float(income), currency)}</h3></div>", unsafe_allow_html=True)
    m3.markdown(f"<div style='background:linear-gradient(135deg,#e03a2f,#7b3fa0);padding:14px;border-radius:14px;'><div class='phx-label'>Despesas</div><h3>{format_currency(float(expense), currency)}</h3></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        exp_by_cat = month_df[month_df["type"] == "expense"].groupby("category_name", as_index=False)["amount"].sum()
        if not exp_by_cat.empty:
            fig = px.pie(exp_by_cat, names="category_name", values="amount", title="Despesas por categoria", template="plotly_dark", color="category_name", color_discrete_sequence=["#f5a623", "#f07020", "#e03a2f", "#c0273b", "#7b3fa0", "#4a5075"])
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        evolution = frame.copy()
        evolution["month"] = pd.to_datetime(evolution["date"]).dt.to_period("M").astype(str)
        monthly = evolution.groupby(["month", "type"], as_index=False)["amount"].sum()
        if not monthly.empty:
            fig = px.bar(monthly, x="month", y="amount", color="type", barmode="group", title="Receita vs despesa", template="plotly_dark", color_discrete_map={"income": "#f5a623", "expense": "#e03a2f"})
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Alertas de orçamento")
    budgets = frame[frame["type"] == "expense"].groupby("category_name", as_index=False)["amount"].sum()
    for _, row in budgets.iterrows():
        category = next((c for c in categories if c["name"] == row["category_name"]), None)
        if category and category.get("budget_limit") and row["amount"] > float(category["budget_limit"]):
            st.warning(f"{row['category_name']} ultrapassou o orçamento ({format_currency(row['amount'], currency)}).")

    csv_data = frame.to_csv(index=False).encode("utf-8")
    st.download_button("Exportar CSV", data=csv_data, file_name=f"financas_{datetime.now().strftime('%Y%m')}.csv", mime="text/csv")

    st.markdown("### Lançamentos")
    for row in tx[:50]:
        cols = st.columns([4, 1])
        cols[0].write(f"{row['date']} • {row['category_name']} • {format_currency(float(row['amount']), currency)}")
        if cols[1].button("Excluir", key=f"del_tx_{row['id']}"):
            soft_delete("transactions", row["id"])
            st.rerun()
