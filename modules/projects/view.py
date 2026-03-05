from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import streamlit as st

from database.db import Database, soft_delete


DEFAULT_COLUMNS = ["To Do", "Em andamento", "Revisão", "Concluído"]


def _priority_badge(priority: str | None) -> str:
    value = (priority or "média").lower()
    if value == "alta":
        return "<span class='status-badge badge-high'>Alta</span>"
    if value == "baixa":
        return "<span class='status-badge badge-completed'>Baixa</span>"
    return "<span class='status-badge badge-active'>Média</span>"


def _create_project(name: str, color: str, description: str, deadline: date | None) -> None:
    db = Database()
    project_id = db.execute(
        "INSERT INTO projects(name, color, description, deadline, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, color, description, deadline.isoformat() if deadline else None, datetime.now().isoformat(), datetime.now().isoformat()),
    )
    for i, col in enumerate(DEFAULT_COLUMNS):
        db.execute(
            "INSERT INTO project_columns(project_id, name, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (project_id, col, i, datetime.now().isoformat(), datetime.now().isoformat()),
        )


def render() -> None:
    st.markdown("<h1 class='module-title'>📋 Projetos</h1>", unsafe_allow_html=True)
    st.markdown("<p class='module-subtitle'>Kanban funcional com alternativa simples de mover tarefas por coluna.</p>", unsafe_allow_html=True)

    db = Database()

    with st.form("project_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Nome do projeto")
        color = c2.color_picker("Cor", value="#6c63ff")
        deadline = c3.date_input("Prazo geral", value=None)
        description = st.text_area("Descrição")
        if st.form_submit_button("Criar projeto") and name.strip():
            _create_project(name, color, description, deadline)
            st.success("Projeto criado.")
            st.rerun()

    projects = db.query("SELECT * FROM projects WHERE deleted_at IS NULL ORDER BY id DESC")
    if not projects:
        st.info("Nenhum projeto ainda.")
        return

    selected = st.selectbox("Projeto", [f"{p['id']} - {p['name']}" for p in projects])
    project_id = int(selected.split(" - ")[0])

    columns = db.query(
        "SELECT * FROM project_columns WHERE deleted_at IS NULL AND project_id = ? ORDER BY position",
        (project_id,),
    )
    goals = db.query("SELECT id, title FROM goals WHERE deleted_at IS NULL")

    with st.form("task_form", clear_on_submit=True):
        st.markdown("### Nova tarefa")
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Título")
        priority = c2.selectbox("Prioridade", ["baixa", "média", "alta"])
        due_date = c3.date_input("Prazo", value=date.today())
        description = st.text_area("Descrição")
        labels = st.text_input("Etiquetas")
        col_opt = st.selectbox("Coluna", [f"{c['id']} - {c['name']}" for c in columns])
        goal_opt = st.selectbox("Meta vinculada", ["Nenhuma"] + [f"{g['id']} - {g['title']}" for g in goals])
        if st.form_submit_button("Salvar tarefa") and title.strip():
            db.execute(
                """
                INSERT INTO project_tasks(project_id, column_id, goal_id, title, description, priority, due_date, labels, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    int(col_opt.split(" - ")[0]),
                    None if goal_opt == "Nenhuma" else int(goal_opt.split(" - ")[0]),
                    title,
                    description,
                    priority,
                    due_date.isoformat(),
                    labels,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            st.rerun()

    tasks = db.query(
        """
        SELECT t.*, c.name AS column_name
        FROM project_tasks t
        JOIN project_columns c ON c.id = t.column_id
        WHERE t.deleted_at IS NULL AND t.project_id = ?
        ORDER BY t.id DESC
        """,
        (project_id,),
    )

    st.markdown("### Board")
    board_cols = st.columns(len(columns)) if columns else []
    for i, col in enumerate(columns):
        with board_cols[i]:
            st.markdown(f"**{col['name']}**")
            col_tasks = [t for t in tasks if t["column_id"] == col["id"]]
            for task in col_tasks:
                with st.container():
                    st.write(task["title"])
                    st.markdown(_priority_badge(task.get("priority")), unsafe_allow_html=True)
                    st.caption(f"Prioridade: {task.get('priority') or '-'} • Prazo: {task.get('due_date') or '-'}")
                    move_to = st.selectbox(
                        "Mover para",
                        [f"{c['id']} - {c['name']}" for c in columns],
                        key=f"mv_{task['id']}",
                    )
                    if st.button("Mover", key=f"move_btn_{task['id']}"):
                        db.execute(
                            "UPDATE project_tasks SET column_id = ?, updated_at = ? WHERE id = ?",
                            (int(move_to.split(" - ")[0]), datetime.now().isoformat(), task["id"]),
                        )
                        st.rerun()
                    if st.button("Excluir", key=f"del_task_{task['id']}"):
                        soft_delete("project_tasks", task["id"])
                        st.rerun()

    st.markdown("### Visão em lista")
    if tasks:
        frame = pd.DataFrame(tasks)[["title", "column_name", "priority", "due_date", "labels"]]
        frame["prioridade"] = frame["priority"].map({"alta": "🔴 Alta", "média": "🟠 Média", "baixa": "🟢 Baixa"}).fillna("🟠 Média")
        st.dataframe(frame[["title", "column_name", "prioridade", "due_date", "labels"]], use_container_width=True)
