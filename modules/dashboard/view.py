from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from components.cards import metric_card, progress_bar
from database.db import Database, get_setting
from utils.formatters import format_currency, greeting_by_hour


@st.cache_data(ttl=60)
def _load_dashboard_data() -> dict:
    db = Database()
    today = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=6)).isoformat()

    goals_active = db.query_one("SELECT COUNT(*) AS n FROM goals WHERE deleted_at IS NULL AND status = 'active'")
    habits_today = db.query_one("SELECT COUNT(*) AS n FROM habit_logs WHERE deleted_at IS NULL AND log_date = ?", (today,))
    saldo_mes = db.query_one(
        """
        SELECT COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE -amount END), 0) AS total
        FROM transactions
        WHERE deleted_at IS NULL AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        """
    )
    paginas_lidas = db.query_one(
        """
        SELECT COALESCE(SUM(pages), 0) AS total
        FROM reading_sessions
        WHERE deleted_at IS NULL AND strftime('%Y-%m', session_date) = strftime('%Y-%m', 'now')
        """
    )

    activity = db.query(
        """
        SELECT log_date AS day, COUNT(*) AS qtd
        FROM habit_logs
        WHERE deleted_at IS NULL AND log_date >= ?
        GROUP BY log_date
        ORDER BY log_date
        """,
        (week_ago,),
    )

    moods = db.query(
        """
        SELECT entry_date, mood
        FROM journal_entries
        WHERE deleted_at IS NULL AND entry_date >= ?
        ORDER BY entry_date
        """,
        (week_ago,),
    )

    goals_progress = db.query(
        """
        SELECT title,
               CASE WHEN COALESCE(target_value, 0) = 0 THEN 0
                    ELSE ROUND((COALESCE(current_value, 0) / target_value) * 100, 2)
               END AS progress
        FROM goals
        WHERE deleted_at IS NULL AND status = 'active'
        ORDER BY COALESCE(deadline, '9999-12-31')
        LIMIT 8
        """
    )

    journal_recent = db.query(
        """
        SELECT entry_date, COALESCE(title, 'Sem título') AS title, substr(content, 1, 120) AS preview
        FROM journal_entries
        WHERE deleted_at IS NULL
        ORDER BY entry_date DESC, id DESC
        LIMIT 5
        """
    )

    tasks_today = db.query(
        """
        SELECT 'Meta' AS tipo, title AS nome, deadline AS data
        FROM goals
        WHERE deleted_at IS NULL AND deadline = ?
        UNION ALL
        SELECT 'Projeto' AS tipo, title AS nome, due_date AS data
        FROM project_tasks
        WHERE deleted_at IS NULL AND due_date = ?
        """,
        (today, today),
    )

    return {
        "goals_active": goals_active["n"] if goals_active else 0,
        "habits_today": habits_today["n"] if habits_today else 0,
        "saldo_mes": float(saldo_mes["total"]) if saldo_mes else 0.0,
        "paginas_lidas": paginas_lidas["total"] if paginas_lidas else 0,
        "activity": activity,
        "moods": moods,
        "goals_progress": goals_progress,
        "journal_recent": journal_recent,
        "tasks_today": tasks_today,
    }


def _habit_streak() -> int:
    db = Database()
    rows = db.query(
        """
        SELECT DISTINCT log_date FROM habit_logs
        WHERE deleted_at IS NULL
        ORDER BY log_date DESC
        """
    )
    dates = {r["log_date"] for r in rows}
    streak = 0
    cursor = date.today()
    while cursor.isoformat() in dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def render() -> None:
    user_name = get_setting("user_name", "Thiago")
    greeting = greeting_by_hour(datetime.now())
    data = _load_dashboard_data()

    st.markdown(f"<h1 class='module-title'>{greeting}, {user_name} 🔥</h1>", unsafe_allow_html=True)
    st.markdown("<p class='module-subtitle'>Visão unificada da sua evolução pessoal</p>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Metas ativas", str(data["goals_active"]), "este mês", icon="🎯", gradient_index=0)
    with col2:
        metric_card("Hábitos hoje", str(data["habits_today"]), "concluídos hoje", icon="✅", gradient_index=1)
    with col3:
        metric_card("Saldo do mês", format_currency(data["saldo_mes"], get_setting("currency", "R$")), "+ vs mês anterior", icon="💰", gradient_index=2)
    with col4:
        metric_card("Páginas lidas", str(data["paginas_lidas"]), "acumulado no mês", icon="📚", gradient_index=3)

    a, b, c = st.columns([2, 1, 1])
    with a:
        st.markdown("### Atividade semanal")
        frame = pd.DataFrame(data["activity"])
        if frame.empty:
            st.info("Sem atividade registrada nos últimos 7 dias.")
        else:
            fig = px.bar(frame, x="day", y="qtd", color="qtd", color_continuous_scale=["#7b3fa0", "#e03a2f", "#f07020", "#f5a623"], template="plotly_dark")
            fig.update_layout(height=260, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    with b:
        st.markdown("### Próximas tarefas")
        if not data["tasks_today"]:
            st.info("Sem tarefas para hoje.")
        for row in data["tasks_today"][:6]:
            st.markdown(f"- **{row['tipo']}**: {row['nome']}")
    with c:
        st.markdown("### Humor (7 dias)")
        moods = pd.DataFrame(data["moods"])
        if moods.empty:
            st.info("Sem registros de humor.")
        else:
            moods["mood"] = moods["mood"].fillna(0)
            fig = px.line(moods, x="entry_date", y="mood", markers=True, template="plotly_dark")
            fig.update_traces(line_color="#f07020")
            fig.update_layout(height=260, margin=dict(l=0, r=0, t=0, b=0), yaxis_range=[0, 5], paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    d, e = st.columns(2)
    with d:
        st.markdown("### Progresso das metas")
        if not data["goals_progress"]:
            st.info("Ainda não há metas. Crie sua primeira! 🎯")
        for goal in data["goals_progress"]:
            progress_bar(goal["title"], float(goal["progress"] or 0))
    with e:
        st.markdown("### Últimas entradas do diário")
        if not data["journal_recent"]:
            st.info("Nenhuma entrada ainda.")
        for entry in data["journal_recent"]:
            st.markdown(f"**{entry['entry_date']} • {entry['title']}**")
            st.caption(entry["preview"])

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(f"<div class='phx-card'><div class='phx-label'>🔥 Streak de hábitos</div><h3 style='color:#f07020'>{_habit_streak()} dias</h3></div>", unsafe_allow_html=True)
    with f2:
        st.markdown("**Mini-calendário**")
        st.date_input("Dia atual", value=date.today(), disabled=True)
    with f3:
        st.markdown("**Atalhos rápidos**")
        if st.button("+ Entrada no Diário"):
            st.session_state.active_module = "journal"
            st.rerun()
        if st.button("+ Nova Meta"):
            st.session_state.active_module = "goals"
            st.rerun()
        if st.button("+ Lançamento Financeiro"):
            st.session_state.active_module = "finances"
            st.rerun()
