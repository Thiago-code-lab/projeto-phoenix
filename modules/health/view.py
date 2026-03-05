from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import Database, soft_delete


def render() -> None:
    st.markdown("<h1 class='module-title'>🏋️ Saúde</h1>", unsafe_allow_html=True)
    st.markdown("<p class='module-subtitle'>Treinos, métricas corporais, hidratação e sono.</p>", unsafe_allow_html=True)

    db = Database()
    tabs = st.tabs(["Treinos", "Métricas", "Hidratação", "Sono"])

    with tabs[0]:
        with st.form("workout_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            workout_date = c1.date_input("Data", value=date.today())
            exercise = c2.text_input("Exercício")
            sets = c3.number_input("Séries", min_value=0, value=3)
            c4, c5, c6 = st.columns(3)
            reps = c4.number_input("Reps", min_value=0, value=10)
            weight = c5.number_input("Carga (kg)", min_value=0.0, value=0.0)
            duration = c6.number_input("Duração (min)", min_value=0, value=45)
            notes = st.text_area("Observações")
            if st.form_submit_button("Registrar treino") and exercise.strip():
                db.execute(
                    """
                    INSERT INTO workouts(workout_date, exercise, sets, reps, weight, duration_minutes, notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (workout_date.isoformat(), exercise, sets, reps, weight, duration, notes, datetime.now().isoformat(), datetime.now().isoformat()),
                )
                st.rerun()

        workouts = db.query("SELECT * FROM workouts WHERE deleted_at IS NULL ORDER BY workout_date DESC, id DESC")
        if workouts:
            frame = pd.DataFrame(workouts)
            line = frame.groupby("workout_date", as_index=False)["weight"].max()
            fig = px.line(line, x="workout_date", y="weight", markers=True, title="Evolução de carga", template="plotly_dark")
            fig.update_traces(line_color="#f07020")
            fig.update_layout(height=280, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            for row in workouts[:20]:
                cols = st.columns([4, 1])
                cols[0].write(f"{row['workout_date']} • {row['exercise']} • {row.get('weight') or 0} kg")
                if cols[1].button("Excluir", key=f"del_w_{row['id']}"):
                    soft_delete("workouts", row["id"])
                    st.rerun()

    with tabs[1]:
        with st.form("body_form", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            metric_date = c1.date_input("Data", value=date.today(), key="metric_date")
            weight = c2.number_input("Peso", min_value=0.0, value=0.0)
            body_fat = c3.number_input("% Gordura", min_value=0.0, value=0.0)
            waist = c4.number_input("Cintura (cm)", min_value=0.0, value=0.0)
            if st.form_submit_button("Salvar métrica"):
                db.execute(
                    "INSERT INTO body_metrics(metric_date, weight, body_fat, waist, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (metric_date.isoformat(), weight, body_fat, waist, datetime.now().isoformat(), datetime.now().isoformat()),
                )
                st.rerun()

        metrics = db.query("SELECT * FROM body_metrics WHERE deleted_at IS NULL ORDER BY metric_date")
        if metrics:
            mdf = pd.DataFrame(metrics)
            fig = px.line(mdf, x="metric_date", y=["weight", "body_fat"], markers=True, title="Histórico corporal", template="plotly_dark")
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            if len(fig.data) > 0:
                fig.data[0].line.color = "#f5a623"
            if len(fig.data) > 1:
                fig.data[1].line.color = "#e03a2f"
            st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        cups = st.number_input("Copos de água hoje", min_value=0, value=0)
        if st.button("Salvar hidratação"):
            existing = db.query_one("SELECT id FROM hydration_logs WHERE deleted_at IS NULL AND log_date = ?", (date.today().isoformat(),))
            if existing:
                db.execute(
                    "UPDATE hydration_logs SET cups = ?, updated_at = ? WHERE id = ?",
                    (cups, datetime.now().isoformat(), existing["id"]),
                )
            else:
                db.execute(
                    "INSERT INTO hydration_logs(log_date, cups, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (date.today().isoformat(), cups, datetime.now().isoformat(), datetime.now().isoformat()),
                )
            st.success("Hidratação atualizada.")

        hyd = db.query("SELECT * FROM hydration_logs WHERE deleted_at IS NULL ORDER BY log_date DESC LIMIT 14")
        if hyd:
            hdf = pd.DataFrame(hyd).sort_values("log_date")
            fig = px.bar(hdf, x="log_date", y="cups", title="Últimos 14 dias", template="plotly_dark", color="cups", color_continuous_scale=["#7b3fa0", "#f5a623"])
            fig.update_layout(height=260, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:
        with st.form("sleep_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            d = c1.date_input("Data", value=date.today(), key="sleep_date")
            hours = c2.number_input("Horas", min_value=0.0, max_value=24.0, value=8.0)
            quality = c3.slider("Qualidade", min_value=1, max_value=5, value=3)
            if st.form_submit_button("Salvar sono"):
                db.execute(
                    "INSERT INTO sleep_logs(log_date, hours, quality, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (d.isoformat(), hours, quality, datetime.now().isoformat(), datetime.now().isoformat()),
                )
                st.rerun()

        sleep = db.query("SELECT * FROM sleep_logs WHERE deleted_at IS NULL ORDER BY log_date DESC LIMIT 30")
        if sleep:
            sdf = pd.DataFrame(sleep).sort_values("log_date")
            fig = px.line(sdf, x="log_date", y=["hours", "quality"], markers=True, title="Sono semanal", template="plotly_dark")
            fig.update_layout(height=260, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            if len(fig.data) > 0:
                fig.data[0].line.color = "#f07020"
            if len(fig.data) > 1:
                fig.data[1].line.color = "#4a90d9"
            st.plotly_chart(fig, use_container_width=True)
