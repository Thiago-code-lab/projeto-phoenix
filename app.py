import streamlit as st
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Meu LifeOS 2026",
    page_icon="📊",
    layout="wide"
)

# Estilo simples
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# Barra lateral
with st.sidebar:
    st.title("📊 LifeOS 2026")
    st.markdown("---")
    st.page_link("app.py", label="Dashboard", icon="🏠")
    st.page_link("pages/1_📚_Biblioteca.py", label="Biblioteca")
    st.page_link("pages/2_🏋️_Academia.py", label="Academia")
    st.page_link("pages/3_💻_Estudos.py", label="Estudos")
    st.page_link("pages/4_📔_Diário.py", label="Diário")
    st.markdown("---")
    st.caption(f"Iniciado em {datetime.now().strftime('%d/%m/%Y')}")

# Página principal
st.title("📊 Bem-vindo ao Meu LifeOS 2026")
st.write("Seu sistema de acompanhamento pessoal para 2026")
st.markdown("---")

# Seção de boas-vindas
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Comece agora!")
    st.write("1. 📚 Adicione livros à sua biblioteca")
    st.write("2. 🏋️ Registre seus treinos")
    st.write("3. 💻 Acompanhe seus estudos")
    st.write("4. 📔 Mantenha um diário")

with col2:
    st.info("💡 Dica: Use o menu lateral para navegar entre as seções do sistema.")

# Seção de status
st.markdown("---")
st.subheader("Status Atual")

# Métricas vazias
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📚 Livros Lidos", "0/0")
with col2:
    st.metric("🏋️ Treinos na Semana", "0/0")
with col3:
    st.metric("💻 Horas de Estudo", "0")
with col4:
    st.metric("📅 Dias no Diário", "0")
