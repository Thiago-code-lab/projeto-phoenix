import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Estudos - Meu LifeOS",
    page_icon="💻"
)

st.title("💻 Estudos")
st.write("Acompanhe seu progresso nos estudos.")

# Seção de metas
with st.expander("📅 Metas de Estudo"):
    st.write("Defina suas metas de estudo aqui.")
    st.text_input("Objetivo Principal")
    st.number_input("Horas semanais", min_value=1, value=10)
    st.date_input("Data Alvo")
    st.button("Salvar Metas")

# Sessões de estudo
st.subheader("Sessões de Estudo")

# Formulário para nova sessão
with st.form("nova_sessao"):
    st.write("### Registrar Nova Sessão")
    col1, col2 = st.columns(2)
    with col1:
        materia = st.text_input("Matéria/Tópico")
    with col2:
        duracao = st.number_input("Duração (horas)", min_value=0.5, step=0.5)
    
    data = st.date_input("Data", datetime.now())
    anotacoes = st.text_area("Anotações")
    
    if st.form_submit_button("Registrar Sessão"):
        st.success("Sessão registrada com sucesso!")

# Lista de sessões
st.subheader("Histórico")
st.info("Nenhuma sessão registrada. Comece adicionando sua primeira sessão acima.")
