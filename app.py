import streamlit as st
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Meu LifeOS 2026",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo moderno e clean
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: white;
        border-radius: 20px;
        margin: 1rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    .hero-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border: 1px solid #f0f0f0;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        color: white;
        text-align: center;
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        color: white;
        text-align: center;
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        color: white;
        text-align: center;
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        color: white;
        text-align: center;
    }
    
    h1 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        font-weight: 600;
    }
    
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 24px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    .css-1d391kg {
        padding-top: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

# Barra lateral moderna
with st.sidebar:
    st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🚀 LifeOS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.9; margin-bottom: 30px;'>Projeto Phoenix 2026</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.page_link("app.py", label="🏠 Dashboard", icon="🏠")
    st.page_link("pages/1_📚_Biblioteca.py", label="📚 Biblioteca", icon="📚")
    st.page_link("pages/2_🏋️_Academia.py", label="🏋️ Academia", icon="🏋️")
    st.page_link("pages/3_💻_Estudos.py", label="💻 Estudos", icon="💻")
    st.page_link("pages/4_📔_Diário.py", label="📔 Diário", icon="📔")
    st.page_link("pages/5_💰_Finanças.py", label="💰 Finanças", icon="💰")
    st.page_link("pages/6_🎯_Metas.py", label="🎯 Metas", icon="🎯")
    st.page_link("pages/7_❤️_Saúde.py", label="❤️ Saúde", icon="❤️")
    
    st.markdown("---")
    st.markdown(f"<p style='text-align: center; opacity: 0.8; font-size: 12px;'>Iniciado em {datetime.now().strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div class="hero-card">
        <h1 style='font-size: 48px; margin-bottom: 10px;'>🚀 Bem-vindo ao seu LifeOS</h1>
        <p style='font-size: 20px; opacity: 0.95;'>Seu sistema completo de gestão pessoal para 2026</p>
    </div>
""", unsafe_allow_html=True)

# Métricas principais com design moderno
st.markdown("<h2 style='margin-top: 30px; margin-bottom: 20px; color: #333;'>📊 Visão Geral</h2>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="metric-card">
            <h3 style='margin-bottom: 10px;'>📚 Biblioteca</h3>
            <h1 style='font-size: 42px; margin: 15px 0;'>8</h1>
            <p style='opacity: 0.9;'>livros lidos este ano</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="metric-card-green">
            <h3 style='margin-bottom: 10px;'>🏋️ Academia</h3>
            <h1 style='font-size: 42px; margin: 15px 0;'>12</h1>
            <p style='opacity: 0.9;'>treinos este mês</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="metric-card-orange">
            <h3 style='margin-bottom: 10px;'>💻 Estudos</h3>
            <h1 style='font-size: 42px; margin: 15px 0;'>42h</h1>
            <p style='opacity: 0.9;'>de estudo este mês</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="metric-card-blue">
            <h3 style='margin-bottom: 10px;'>📔 Diário</h3>
            <h1 style='font-size: 42px; margin: 15px 0;'>15</h1>
            <p style='opacity: 0.9;'>entradas escritas</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Gráfico de atividades
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 style='color: #333; margin-bottom: 15px;'>📈 Atividade Semanal</h3>", unsafe_allow_html=True)
    dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    atividade_df = pd.DataFrame({
        'Dia': dias,
        'Estudos (h)': [3, 4, 2, 5, 6, 3, 2],
        'Academia (h)': [1.5, 0, 1.5, 1, 1.5, 2, 1],
        'Leitura (h)': [1, 0.5, 1, 1.5, 0.5, 2, 3]
    })
    
    fig = px.bar(atividade_df, x='Dia', y=['Estudos (h)', 'Academia (h)', 'Leitura (h)'],
                 color_discrete_sequence=['#667eea', '#11998e', '#f5576c'],
                 barmode='group')
    fig.update_layout(
        height=300,
        margin=dict(t=0, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("<h3 style='color: #333; margin-bottom: 15px;'>🎯 Progresso das Metas</h3>", unsafe_allow_html=True)
    metas_df = pd.DataFrame({
        'Área': ['Saúde', 'Educação', 'Finanças', 'Bem-estar'],
        'Progresso': [85, 72, 68, 90]
    })
    
    fig = go.Figure(data=[
        go.Bar(x=metas_df['Área'], y=metas_df['Progresso'],
               marker_color=['#11998e', '#667eea', '#f5576c', '#4facfe'],
               text=metas_df['Progresso'].apply(lambda x: f'{x}%'),
               textposition='outside')
    ])
    fig.update_layout(
        height=300,
        margin=dict(t=0, b=0, l=0, r=0),
        yaxis_range=[0, 100],
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_title='Progresso (%)'
    )
    st.plotly_chart(fig, use_container_width=True)

# Cards de funcionalidades
st.markdown("<h2 style='margin-top: 40px; margin-bottom: 20px; color: #333;'>✨ Explore o Sistema</h2>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="feature-card">
            <h2 style='text-align: center; font-size: 48px; margin-bottom: 15px;'>📚</h2>
            <h3 style='text-align: center; color: #333; margin-bottom: 10px;'>Biblioteca</h3>
            <p style='text-align: center; color: #666; font-size: 14px;'>Organize sua lista de leitura e acompanhe seus livros favoritos</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <h2 style='text-align: center; font-size: 48px; margin-bottom: 15px;'>🏋️</h2>
            <h3 style='text-align: center; color: #333; margin-bottom: 10px;'>Academia</h3>
            <p style='text-align: center; color: #666; font-size: 14px;'>Registre treinos e monitore seu progresso físico</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <h2 style='text-align: center; font-size: 48px; margin-bottom: 15px;'>💰</h2>
            <h3 style='text-align: center; color: #333; margin-bottom: 10px;'>Finanças</h3>
            <p style='text-align: center; color: #666; font-size: 14px;'>Gerencie despesas, receitas e investimentos</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="feature-card">
            <h2 style='text-align: center; font-size: 48px; margin-bottom: 15px;'>🎯</h2>
            <h3 style='text-align: center; color: #333; margin-bottom: 10px;'>Metas</h3>
            <p style='text-align: center; color: #666; font-size: 14px;'>Defina e acompanhe seus objetivos pessoais</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Dica do dia
st.markdown("""
    <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
         padding: 25px; border-radius: 15px; margin-top: 30px;'>
        <h3 style='color: #333; margin-bottom: 10px;'>💡 Dica do Dia</h3>
        <p style='color: #555; font-size: 16px; margin: 0;'>
            "A jornada de mil milhas começa com um único passo. Comece hoje a transformar sua vida!"
        </p>
    </div>
""", unsafe_allow_html=True)
