from __future__ import annotations

import streamlit as st
from streamlit_option_menu import option_menu

from config import MODULES
from database.db import get_setting


def render_sidebar() -> str:
    if "active_module" not in st.session_state:
        st.session_state.active_module = "dashboard"

    user_name = get_setting("user_name", "Thiago")
    avatar = get_setting("avatar", "🔥")

    with st.sidebar:
        st.markdown(f"<div class='sidebar-logo'><h2>{avatar} Projeto Phoenix</h2></div>", unsafe_allow_html=True)
        st.caption(f"Workspace pessoal de {user_name}")
        st.divider()

        labels = list(MODULES.items())
        current_idx = next((i for i, (key, _) in enumerate(labels) if key == st.session_state.active_module), 0)
        options = [label for _, label in labels]
        selected_label = option_menu(
            menu_title=None,
            options=options,
            icons=["house", "bullseye", "check2-circle", "cash-stack", "book", "heart-pulse", "journal-text", "kanban", "gear"],
            menu_icon=None,
            default_index=current_idx,
            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": "transparent",
                },
                "icon": {
                    "color": "#f07020",
                    "font-size": "15px",
                },
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "2px 0",
                    "color": "#8b93b8",
                    "border-radius": "8px",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(90deg, rgba(240,112,32,0.15) 0%, transparent 100%)",
                    "color": "#f5a623",
                    "border-left": "3px solid #f07020",
                },
            },
        )

        selected_key = next(key for key, label in labels if label == selected_label)
        st.session_state.active_module = selected_key

    return st.session_state.active_module
