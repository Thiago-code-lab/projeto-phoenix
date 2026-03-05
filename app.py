from __future__ import annotations

import streamlit as st

from components.sidebar import render_sidebar
from config import APP_ICON, APP_LAYOUT, APP_NAME, STYLE_PATH
from database.db import init_db
from modules.dashboard import render as render_dashboard
from modules.finances import render as render_finances
from modules.goals import render as render_goals
from modules.habits import render as render_habits
from modules.health import render as render_health
from modules.journal import render as render_journal
from modules.library import render as render_library
from modules.projects import render as render_projects
from modules.settings import render as render_settings


def inject_css() -> None:
    with open(STYLE_PATH, encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout=APP_LAYOUT, initial_sidebar_state="expanded")
    init_db()
    inject_css()

    module_key = render_sidebar()

    render_map = {
        "dashboard": render_dashboard,
        "goals": render_goals,
        "habits": render_habits,
        "finances": render_finances,
        "library": render_library,
        "health": render_health,
        "journal": render_journal,
        "projects": render_projects,
        "settings": render_settings,
    }

    view = render_map.get(module_key, render_dashboard)
    view()


if __name__ == "__main__":
    main()
