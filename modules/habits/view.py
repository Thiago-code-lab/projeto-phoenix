from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from components.charts import contributions_heatmap
from database.db import Database, soft_delete


def _today_str() -> str:
    return date.today().isoformat()


def _habit_streak(db: Database, habit_id: int) -> tuple[int, int]:
    rows = db.query(
        "SELECT DISTINCT log_date FROM habit_logs WHERE deleted_at IS NULL AND habit_id = ? ORDER BY log_date DESC",
        (habit_id,),
    )
    dates = [r["log_date"] for r in rows]
    date_set = set(dates)

    current = 0
    cursor = date.today()
    while cursor.isoformat() in date_set:
        current += 1
        cursor -= timedelta(days=1)

    best = 0
    running = 0
    prev = None
    for d in sorted(dates):
        cur = datetime.strptime(d, "%Y-%m-%d").date()
        if prev and (cur - prev).days == 1:
            running += 1
        else:
            running = 1
        best = max(best, running)
        prev = cur

    return current, best


def render() -> None:
    st.markdown("<h1 class='module-title'>✅ Hábitos</h1>", unsafe_allow_html=True)
    st.markdown("<p class='module-subtitle'>Consistência diária com check-in rápido e visual estilo contribuição.</p>", unsafe_allow_html=True)

    db = Database()

    with st.form("habit_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Nome do hábito")
        icon = c2.text_input("Ícone", value="✅")
        frequency = c3.selectbox("Frequência", ["daily", "weekly", "custom"])
        c4, c5 = st.columns(2)
        target_count = c4.number_input("Meta diária", min_value=1, value=1)
        is_negative = c5.checkbox("Hábito negativo? (ex: não fumar)")
        description = st.text_area("Descrição")
        if st.form_submit_button("Criar hábito") and name.strip():
            db.execute(
                """
                INSERT INTO habits(name, icon, description, frequency, target_count, is_negative, color, active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (name, icon, description, frequency, target_count, int(is_negative), "#00d4aa", datetime.now().isoformat(), datetime.now().isoformat()),
            )
            st.success("Hábito criado.")
            st.rerun()

    habits = db.query("SELECT * FROM habits WHERE deleted_at IS NULL AND active = 1 ORDER BY id DESC")
    if not habits:
        st.info("Ainda não há hábitos. Crie o primeiro para começar.")
        return

    st.markdown("### Check-in de hoje")
    for habit in habits:
        left, right = st.columns([4, 1])
        with left:
            st.write(f"{habit.get('icon') or '✅'} **{habit['name']}**")
        with right:
            label = "Não fiz" if habit["is_negative"] else "Check"
            if st.button(label, key=f"check_{habit['id']}"):
                today = _today_str()
                existing = db.query_one(
                    "SELECT id, count FROM habit_logs WHERE deleted_at IS NULL AND habit_id = ? AND log_date = ?",
                    (habit["id"], today),
                )
                if existing:
                    db.execute(
                        "UPDATE habit_logs SET count = ?, updated_at = ? WHERE id = ?",
                        (int(existing["count"] or 0) + 1, datetime.now().isoformat(), existing["id"]),
                    )
                else:
                    db.execute(
                        "INSERT INTO habit_logs(habit_id, log_date, count, created_at, updated_at) VALUES (?, ?, 1, ?, ?)",
                        (habit["id"], today, datetime.now().isoformat(), datetime.now().isoformat()),
                    )
                st.rerun()

    st.divider()
    h1, h2 = st.columns(2)
    with h1:
        logs = db.query(
            """
            SELECT log_date, SUM(count) AS intensidade
            FROM habit_logs
            WHERE deleted_at IS NULL AND log_date >= date('now', '-365 day')
            GROUP BY log_date
            ORDER BY log_date
            """
        )
        contributions_heatmap(pd.DataFrame(logs), "log_date", "intensidade", "Mapa de consistência (último ano)")

    with h2:
        stats_rows = []
        overall_streak = 0
        for habit in habits:
            current, best = _habit_streak(db, habit["id"])
            overall_streak = max(overall_streak, current)
            stats_rows.append({"hábito": habit["name"], "streak atual": current, "recorde": best})
        st.markdown(
            f"<div style='display:inline-block;padding:8px 12px;border-radius:999px;background:linear-gradient(135deg,#f07020,#e03a2f);border:1px solid rgba(245,166,35,0.35);box-shadow:0 0 16px rgba(240,112,32,0.35);font-weight:600;'>🔥 Streak atual: {overall_streak} dias</div>",
            unsafe_allow_html=True,
        )
        st.markdown("### Streaks")
        st.dataframe(pd.DataFrame(stats_rows), use_container_width=True)

        monthly = db.query(
            """
            SELECT strftime('%Y-%m', log_date) AS mes, COUNT(*) AS concluidos
            FROM habit_logs
            WHERE deleted_at IS NULL
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT 12
            """
        )
        if monthly:
            chart = pd.DataFrame(monthly).sort_values("mes")
            fig = px.bar(chart, x="mes", y="concluidos", title="Conclusão por mês", template="plotly_dark", color="concluidos", color_continuous_scale=["#7b3fa0", "#e03a2f", "#f5a623"])
            fig.update_layout(height=260, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Gerenciar hábitos")
    for habit in habits:
        cols = st.columns([4, 1])
        cols[0].write(f"{habit.get('icon') or '✅'} {habit['name']}")
        if cols[1].button("Excluir", key=f"del_h_{habit['id']}"):
            soft_delete("habits", habit["id"])
            st.rerun()
