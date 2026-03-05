from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import streamlit as st

from components.cards import progress_bar, status_badge, surface_close, surface_open
from database.db import Database, soft_delete


def _save_goal(
    title: str,
    description: str,
    category: str,
    target_value: float,
    unit: str,
    deadline: date | None,
    parent_id: int | None,
) -> None:
    db = Database()
    db.execute(
        """
        INSERT INTO goals(title, description, category, target_value, unit, deadline, parent_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            description,
            category,
            target_value,
            unit,
            deadline.isoformat() if deadline else None,
            parent_id,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ),
    )


def render() -> None:
    st.markdown("<h1 class='module-title'>🎯 Metas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='module-subtitle'>Defina objetivos, acompanhe progresso e mantenha foco.</p>", unsafe_allow_html=True)

    db = Database()

    with st.form("goal_form", clear_on_submit=True):
        st.markdown("### Nova meta")
        c1, c2 = st.columns(2)
        title = c1.text_input("Título")
        category = c2.text_input("Categoria", value="Geral")
        description = st.text_area("Descrição")
        c3, c4, c5 = st.columns(3)
        target_value = c3.number_input("Meta numérica", min_value=0.0, value=100.0)
        unit = c4.text_input("Unidade", value="%")
        deadline = c5.date_input("Prazo", value=None)

        possible_parents = db.query("SELECT id, title FROM goals WHERE deleted_at IS NULL AND parent_id IS NULL")
        parent_option = st.selectbox("Sub-meta de", options=["Nenhuma"] + [f"{g['id']} - {g['title']}" for g in possible_parents])
        submitted = st.form_submit_button("Salvar meta")
        if submitted and title.strip():
            parent_id = None
            if parent_option != "Nenhuma":
                parent_id = int(parent_option.split(" - ")[0])
            _save_goal(title, description, category, target_value, unit, deadline, parent_id)
            st.success("Meta criada com sucesso.")
            st.rerun()

    st.divider()
    filters_col, _ = st.columns([2, 5])
    with filters_col:
        filter_status = st.selectbox("Filtro", ["Todas", "Ativas", "Concluídas", "Atrasadas"])

    query = "SELECT * FROM goals WHERE deleted_at IS NULL"
    rows = db.query(query)
    today = date.today().isoformat()
    if filter_status == "Ativas":
        rows = [r for r in rows if r["status"] == "active"]
    elif filter_status == "Concluídas":
        rows = [r for r in rows if r["status"] == "completed"]
    elif filter_status == "Atrasadas":
        rows = [r for r in rows if r["deadline"] and r["deadline"] < today and r["status"] != "completed"]

    if not rows:
        st.info("Ainda não há metas para este filtro.")
        return

    for goal in rows:
        with st.container():
            surface_open()
            top1, top2, top3 = st.columns([3, 2, 1])
            with top1:
                st.markdown(f"### {goal['title']}")
                st.caption(goal.get("description") or "Sem descrição")
            with top2:
                st.write(f"Categoria: {goal.get('category') or '-'}")
                st.write(f"Prazo: {goal.get('deadline') or '-'}")
                if goal.get("status") == "completed":
                    st.markdown(status_badge("Concluída", "badge-completed"), unsafe_allow_html=True)
                elif goal.get("status") == "active":
                    st.markdown(status_badge("Em andamento", "badge-active"), unsafe_allow_html=True)
                else:
                    st.markdown(status_badge("Pausada", "badge-high"), unsafe_allow_html=True)
            with top3:
                new_status = st.selectbox(
                    "Status",
                    options=["active", "completed", "paused"],
                    index=["active", "completed", "paused"].index(goal["status"] if goal["status"] in ["active", "completed", "paused"] else "active"),
                    key=f"status_{goal['id']}",
                )
                if st.button("Atualizar", key=f"upd_status_{goal['id']}"):
                    db.execute(
                        "UPDATE goals SET status = ?, updated_at = ? WHERE id = ?",
                        (new_status, datetime.now().isoformat(), goal["id"]),
                    )
                    st.rerun()

            target = float(goal.get("target_value") or 0)
            current = float(goal.get("current_value") or 0)
            pct = (current / target * 100) if target > 0 else 0
            progress_bar(f"{goal['title']} ({current:.1f}/{target:.1f} {goal.get('unit') or ''})", pct)

            quick = st.slider("Quick update", 0.0, target if target > 0 else 100.0, float(current), key=f"quick_{goal['id']}")
            cta1, cta2 = st.columns(2)
            with cta1:
                if st.button("Salvar progresso", key=f"save_progress_{goal['id']}"):
                    db.execute(
                        "UPDATE goals SET current_value = ?, updated_at = ? WHERE id = ?",
                        (quick, datetime.now().isoformat(), goal["id"]),
                    )
                    st.success("Progresso atualizado.")
                    st.rerun()
            with cta2:
                if st.button("Excluir", key=f"del_goal_{goal['id']}"):
                    soft_delete("goals", goal["id"])
                    st.warning("Meta removida.")
                    st.rerun()
            surface_close()

    frame = pd.DataFrame(rows)
    if not frame.empty:
        st.markdown("### Timeline de prazos")
        timeline = frame[["title", "deadline", "status"]].dropna(subset=["deadline"])
        st.dataframe(timeline, use_container_width=True)
