import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Academia - Meu LifeOS",
    page_icon="🏋️"
)

st.title("🏋️ Academia")
st.write("Acompanhe seu progresso na academia.")

# Seção de metas
with st.expander("🎯 Metas"):
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Peso Atual (kg)", min_value=30.0, value=75.0, step=0.1)
        st.number_input("Meta de Peso (kg)", min_value=30.0, value=85.0, step=0.1)
    with col2:
        st.number_input("Dias de Treino por Semana", min_value=1, max_value=7, value=5)
        st.text_input("Objetivo Principal")
    st.button("Salvar Metas")

# Registrar treino
st.subheader("Registrar Treino")
with st.form("novo_treino"):
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.now())
        tipo_treino = st.selectbox("Tipo de Treino", 
                                 ["Peito/Tríceps", "Costa/Bíceps", "Perna", "Ombro/Abdômen", "Cardio"])
    with col2:
        duracao = st.number_input("Duração (minutos)", min_value=1, value=60)
        intensidade = st.slider("Intensidade", 1, 10, 7)
    
    observacoes = st.text_area("Observações")
    
    if st.form_submit_button("Registrar Treino"):
        st.success("Treino registrado com sucesso!")

# Histórico
st.subheader("Histórico")
st.info("Nenhum treino registrado. Comece adicionando seu primeiro treino acima.")
