from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from database.db import Database, soft_delete


TEMPLATES = {
    "Livre": "",
    "Diário matinal": "## Intenção do dia\n-\n\n## Prioridades\n-\n\n## Gratidão\n-",
    "Reflexão noturna": "## Como foi meu dia\n\n## O que aprendi\n\n## O que posso melhorar amanhã",
    "Revisão semanal": "## Vitórias da semana\n\n## Desafios\n\n## Foco da próxima semana",
}

MOOD_OPTIONS = {
    "😞": 1,
    "😕": 2,
    "😐": 3,
    "🙂": 4,
    "😁": 5,
}


def _journal_streak(entries: list[dict]) -> int:
    dates = {e["entry_date"] for e in entries}
    streak = 0
    cursor = date.today()
    while cursor.isoformat() in dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def render() -> None:
    st.markdown("<h1 class='module-title'>📝 Diário</h1>", unsafe_allow_html=True)
    st.markdown("<div class='journal-hero'><p class='module-subtitle'>Escreva em markdown com foco e acompanhe consistência.</p></div>", unsafe_allow_html=True)

    db = Database()
    with st.form("journal_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        entry_date = c1.date_input("Data", value=date.today())
        title = c2.text_input("Título (opcional)")
        template_name = c3.selectbox("Template", list(TEMPLATES.keys()))
        content = st.text_area("Conteúdo", value=TEMPLATES[template_name], height=220)
        mood_emoji = st.select_slider("Humor", options=list(MOOD_OPTIONS.keys()), value="😐")
        mood = MOOD_OPTIONS[mood_emoji]
        g1, g2, g3 = st.columns(3)
        grat1 = g1.text_input("Gratidão 1")
        grat2 = g2.text_input("Gratidão 2")
        grat3 = g3.text_input("Gratidão 3")
        tags = st.text_input("Tags (separadas por vírgula)")
        if st.form_submit_button("Salvar entrada") and content.strip():
            db.execute(
                """
                INSERT INTO journal_entries(entry_date, title, content, mood, gratitude_1, gratitude_2, gratitude_3, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry_date.isoformat(),
                    title,
                    content,
                    mood,
                    grat1,
                    grat2,
                    grat3,
                    tags,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            st.success("Entrada registrada.")
            st.rerun()

    entries = db.query("SELECT * FROM journal_entries WHERE deleted_at IS NULL ORDER BY entry_date DESC, id DESC")
    if not entries:
        st.info("Nenhuma entrada ainda. Escreva sua primeira! ✍️")
        return

    left, right = st.columns([2, 1])
    with left:
        query = st.text_input("Buscar por texto/tag")
        filtered = entries
        if query.strip():
            q = query.lower()
            filtered = [e for e in entries if q in (e.get("content") or "").lower() or q in (e.get("tags") or "").lower()]

        for entry in filtered[:50]:
            with st.container():
                st.markdown(f"### {entry.get('title') or 'Sem título'}")
                st.caption(f"{entry['entry_date']} • Humor {entry.get('mood') or '-'}")
                st.markdown(entry.get("content")[:700])
                if st.button("Excluir", key=f"del_j_{entry['id']}"):
                    soft_delete("journal_entries", entry["id"])
                    st.rerun()

    with right:
        streak = _journal_streak(entries)
        words = sum(len((e.get("content") or "").split()) for e in entries if e["entry_date"].startswith(datetime.now().strftime("%Y-%m")))
        st.metric("Streak escrita", f"{streak} dias")
        st.metric("Word count (mês)", words)

        moods = pd.DataFrame(entries)[["entry_date", "mood"]]
        moods = moods.dropna(subset=["mood"]).sort_values("entry_date")
        if not moods.empty:
            st.line_chart(moods, x="entry_date", y="mood")

        txt_export = "\n\n".join([f"{e['entry_date']} - {e.get('title') or ''}\n{e.get('content') or ''}" for e in entries])
        st.download_button("Exportar TXT", data=txt_export.encode("utf-8"), file_name="diario_phoenix.txt", mime="text/plain")
