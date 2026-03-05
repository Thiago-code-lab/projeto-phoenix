from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def contributions_heatmap(df: pd.DataFrame, date_col: str, value_col: str, title: str) -> None:
    if df.empty:
        st.info("Sem dados suficientes para o heatmap ainda.")
        return

    frame = df.copy()
    frame[date_col] = pd.to_datetime(frame[date_col])
    frame["weekday"] = frame[date_col].dt.day_name(locale="pt_BR") if hasattr(frame[date_col].dt, "day_name") else frame[date_col].dt.day_name()
    frame["week"] = frame[date_col].dt.isocalendar().week.astype(int)

    pivot = frame.pivot_table(index="weekday", columns="week", values=value_col, aggfunc="sum", fill_value=0)
    fig = px.imshow(
        pivot,
        color_continuous_scale=[
            [0.0, "#1e2340"],
            [0.33, "#7b3fa0"],
            [0.66, "#e03a2f"],
            [1.0, "#f5a623"],
        ],
        aspect="auto",
        title=title,
    )
    fig.update_layout(height=260, margin=dict(l=0, r=0, t=40, b=0), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


def simple_line(df: pd.DataFrame, x: str, y: str, title: str) -> None:
    if df.empty:
        st.info("Sem dados para o gráfico.")
        return
    fig = px.line(df, x=x, y=y, title=title, markers=True, template="plotly_dark")
    fig.update_traces(line_color="#f07020")
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
