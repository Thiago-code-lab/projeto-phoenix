from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import Database, soft_delete


def render() -> None:
    st.markdown("<h1 class='module-title'>📚 Biblioteca</h1>", unsafe_allow_html=True)
    st.markdown("<p class='module-subtitle'>Estante pessoal, progresso de leitura e sessões.</p>", unsafe_allow_html=True)

    db = Database()

    with st.form("book_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        title = c1.text_input("Título")
        author = c2.text_input("Autor")
        c3, c4, c5 = st.columns(3)
        total_pages = c3.number_input("Páginas totais", min_value=0, value=0)
        genre = c4.text_input("Gênero")
        status = c5.selectbox("Status", ["quero_ler", "lendo", "lido", "abandonado"])
        cover = st.text_input("Capa (URL/local)")
        rating = st.slider("Nota", 0.0, 5.0, 0.0, 0.5)
        if st.form_submit_button("Salvar livro") and title.strip():
            db.execute(
                """
                INSERT INTO books(title, author, cover, total_pages, genre, rating, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (title, author, cover, total_pages, genre, rating, status, datetime.now().isoformat(), datetime.now().isoformat()),
            )
            st.rerun()

    books = db.query("SELECT * FROM books WHERE deleted_at IS NULL ORDER BY id DESC")
    if not books:
        st.info("Sem livros cadastrados ainda.")
        return

    with st.form("reading_session", clear_on_submit=True):
        st.markdown("### Registrar sessão de leitura")
        selected = st.selectbox("Livro", [f"{b['id']} - {b['title']}" for b in books])
        c1, c2, c3 = st.columns(3)
        session_date = c1.date_input("Data", value=date.today())
        pages = c2.number_input("Páginas", min_value=0, value=0)
        minutes = c3.number_input("Minutos", min_value=0, value=0)
        quote = st.text_input("Destaque")
        if st.form_submit_button("Registrar sessão"):
            book_id = int(selected.split(" - ")[0])
            db.execute(
                """
                INSERT INTO reading_sessions(book_id, session_date, pages, minutes, quote, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (book_id, session_date.isoformat(), pages, minutes, quote, datetime.now().isoformat(), datetime.now().isoformat()),
            )
            db.execute(
                "UPDATE books SET pages_read = COALESCE(pages_read, 0) + ?, updated_at = ? WHERE id = ?",
                (pages, datetime.now().isoformat(), book_id),
            )
            st.success("Sessão registrada.")
            st.rerun()

    frame = pd.DataFrame(books)
    k1, k2, k3, k4 = st.columns(4)
    total = len(books)
    read_count = len([b for b in books if b.get("status") == "lido"])
    reading_count = len([b for b in books if b.get("status") == "lendo"])
    todo_count = len([b for b in books if b.get("status") == "quero_ler"])
    k1.markdown(f"<div style='background:linear-gradient(135deg,#f5a623,#f07020);padding:12px;border-radius:14px;'><div class='phx-label'>Total de livros</div><h3>{total}</h3></div>", unsafe_allow_html=True)
    k2.markdown(f"<div style='background:linear-gradient(135deg,#f07020,#e03a2f);padding:12px;border-radius:14px;'><div class='phx-label'>Lidos</div><h3>{read_count}</h3></div>", unsafe_allow_html=True)
    k3.markdown(f"<div style='background:linear-gradient(135deg,#e03a2f,#7b3fa0);padding:12px;border-radius:14px;'><div class='phx-label'>Lendo</div><h3>{reading_count}</h3></div>", unsafe_allow_html=True)
    k4.markdown(f"<div style='background:linear-gradient(135deg,#7b3fa0,#252b4a);padding:12px;border-radius:14px;'><div class='phx-label'>Para ler</div><h3>{todo_count}</h3></div>", unsafe_allow_html=True)

    st.markdown("### Estante")
    cols = st.columns(4)
    for i, book in enumerate(books):
        with cols[i % 4]:
            with st.container():
                st.markdown(f"**{book['title']}**")
                st.caption(f"{book.get('author') or 'Autor não informado'} • {book.get('status')}")
                total = int(book.get("total_pages") or 0)
                read = int(book.get("pages_read") or 0)
                progress = (read / total * 100) if total > 0 else 0
                st.progress(min(progress / 100, 1.0))
                st.caption(f"{read}/{total} páginas")
                st.markdown(f"<div style='color:#f5a623'>{'★' * int(round(float(book.get('rating') or 0)))}{'☆' * (5-int(round(float(book.get('rating') or 0))))}</div>", unsafe_allow_html=True)
                if st.button("Excluir", key=f"del_book_{book['id']}"):
                    soft_delete("books", book["id"])
                    st.rerun()

    sessions = db.query("SELECT session_date, pages, minutes FROM reading_sessions WHERE deleted_at IS NULL")
    if sessions:
        sdf = pd.DataFrame(sessions)
        sdf["session_date"] = pd.to_datetime(sdf["session_date"])
        sdf["month"] = sdf["session_date"].dt.to_period("M").astype(str)
        pages_month = sdf.groupby("month", as_index=False)["pages"].sum()
        fig = px.bar(pages_month, x="month", y="pages", title="Páginas lidas por mês", template="plotly_dark", color="pages", color_continuous_scale=["#7b3fa0", "#f5a623"])
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    col_a.metric("Páginas no mês", int(sum(s["pages"] for s in sessions if s["session_date"].startswith(datetime.now().strftime("%Y-%m")))))
    if not frame.empty:
        genre_pref = frame["genre"].value_counts().head(1)
        col_b.metric("Gênero mais comum", genre_pref.index[0] if not genre_pref.empty else "-")
