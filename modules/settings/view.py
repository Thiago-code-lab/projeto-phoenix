from __future__ import annotations

from datetime import datetime

import streamlit as st

from config import DB_PATH
from database.db import Database, get_setting, set_setting


def render() -> None:
    st.markdown("## ⚙️ Configurações")
    st.caption("Perfil, preferências, backup local e limpeza por módulo.")

    with st.form("settings_form"):
        name = st.text_input("Nome", value=get_setting("user_name", "Thiago"))
        avatar = st.text_input("Avatar", value=get_setting("avatar", "🔥"))
        theme = st.selectbox("Tema", ["dark", "light"], index=0 if get_setting("theme", "dark") == "dark" else 1)
        currency = st.selectbox("Moeda", ["R$", "$", "€"], index=["R$", "$", "€"].index(get_setting("currency", "R$")))
        week_start = st.selectbox("Primeiro dia da semana", ["Segunda", "Domingo"], index=0 if get_setting("week_start", "Segunda") == "Segunda" else 1)
        notifications = st.checkbox("Notificações locais", value=get_setting("notifications", "0") == "1")

        if st.form_submit_button("Salvar configurações"):
            set_setting("user_name", name)
            set_setting("avatar", avatar)
            set_setting("theme", theme)
            set_setting("currency", currency)
            set_setting("week_start", week_start)
            set_setting("notifications", "1" if notifications else "0")
            st.success("Configurações atualizadas.")

    st.divider()
    st.markdown("### Backup")
    with open(DB_PATH, "rb") as f:
        st.download_button(
            "Exportar phoenix.db",
            data=f.read(),
            file_name=f"phoenix_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
            mime="application/octet-stream",
        )

    st.divider()
    st.markdown("### Reset por módulo")
    reset_map = {
        "Metas": ["goals"],
        "Hábitos": ["habits", "habit_logs"],
        "Finanças": ["transactions", "finance_categories"],
        "Biblioteca": ["books", "reading_sessions"],
        "Saúde": ["workouts", "body_metrics", "hydration_logs", "sleep_logs"],
        "Diário": ["journal_entries"],
        "Projetos": ["project_tasks", "project_columns", "projects"],
    }
    selected_module = st.selectbox("Módulo para limpar", list(reset_map.keys()))

    if st.button("Limpar dados do módulo", type="primary"):
        db = Database()
        for table in reset_map[selected_module]:
            db.execute(f"DELETE FROM {table}")
        st.warning(f"Dados do módulo {selected_module} removidos.")
