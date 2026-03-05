from __future__ import annotations

import streamlit as st


def section_header(title: str, subtitle: str = "") -> None:
    subtitle_html = f"<div class='phx-muted'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div style='margin-bottom:10px;'>
          <h2 style='margin-bottom:2px;'>{title}</h2>
          {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
