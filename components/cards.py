from __future__ import annotations

import streamlit as st


def metric_card_phoenix(
    title: str,
    value: str,
    subtitle: str = "",
    gradient_index: int = 0,
    icon: str = "🔥",
) -> None:
    gradients = [
        "linear-gradient(135deg, #f5a623, #f07020)",
        "linear-gradient(135deg, #f07020, #e03a2f)",
        "linear-gradient(135deg, #e03a2f, #c0273b)",
        "linear-gradient(135deg, #c0273b, #7b3fa0)",
    ]
    glow_colors = [
        "rgba(245,166,35,0.3)",
        "rgba(240,112,32,0.3)",
        "rgba(224,58,47,0.3)",
        "rgba(123,63,160,0.3)",
    ]
    gradient = gradients[gradient_index % 4]
    glow = glow_colors[gradient_index % 4]

    html = f"""
    <div style="
        background: {gradient};
        border-radius: 14px;
        padding: 24px 20px;
        text-align: center;
        box-shadow: 0 8px 32px {glow}, 0 2px 8px rgba(0,0,0,0.4);
        cursor: default;
    ">
        <div style="font-size: 1.6rem; margin-bottom: 4px;">{icon}</div>
        <div style="color: rgba(255,255,255,0.85); font-size: 13px; font-weight: 500; letter-spacing: 0.5px;">{title}</div>
        <div style="color: #fff; font-size: 2.2rem; font-weight: 700; margin: 8px 0 4px;">{value}</div>
        <div style="color: rgba(255,255,255,0.65); font-size: 12px;">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def metric_card(title: str, value: str, delta: str | None = None, icon: str = "📊", gradient_index: int = 0) -> None:
    metric_card_phoenix(title=title, value=value, subtitle=delta or "", gradient_index=gradient_index, icon=icon)


def progress_bar(label: str, percentage: float) -> None:
    pct = max(0.0, min(100.0, percentage))
    st.markdown(
        f"""
        <div class='phx-card' style='margin-bottom:8px;'>
          <div style='display:flex;justify-content:space-between;'>
            <span>{label}</span><span>{pct:.0f}%</span>
          </div>
          <div style='margin-top:8px;background:#1e2340;border-radius:999px;height:10px;'>
            <div style='width:{pct}%;height:10px;background:linear-gradient(90deg,#7b3fa0,#e03a2f,#f07020,#f5a623);border-radius:999px;box-shadow:0 0 8px rgba(240,112,32,0.4);'></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_ring(percentage: float, label: str, color: str = "#f07020") -> None:
    pct = max(0.0, min(100.0, percentage))
    radius = 36
    circumference = 2 * 3.1416 * radius
    offset = circumference - (pct / 100.0) * circumference
    st.markdown(
        f"""
        <div class='phx-card' style='display:flex;align-items:center;gap:12px;'>
          <svg width='92' height='92'>
            <circle cx='46' cy='46' r='{radius}' stroke='#252b4a' stroke-width='8' fill='none' />
            <circle cx='46' cy='46' r='{radius}' stroke='{color}' stroke-width='8' fill='none'
                    stroke-dasharray='{circumference}' stroke-dashoffset='{offset}'
                    transform='rotate(-90 46 46)' />
            <text x='46' y='52' fill='#edf0ff' text-anchor='middle' font-size='14'>{pct:.0f}%</text>
          </svg>
          <div><div class='phx-label'>{label}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(text: str, kind: str) -> str:
    return f"<span class='status-badge {kind}'>{text}</span>"


def surface_open() -> None:
    st.markdown("<div class='phx-card'>", unsafe_allow_html=True)


def surface_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
