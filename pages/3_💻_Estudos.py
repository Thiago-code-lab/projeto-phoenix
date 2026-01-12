import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Estudos - Meu LifeOS",
    page_icon="💻",
    layout="wide"
)

# Estilo moderno
st.markdown("""
    <style>
    .study-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #667eea;
        margin-bottom: 15px;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .stat-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .stat-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .stat-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("<h1 style='text-align: center; color: #667eea;'>💻 Estudos</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 18px; margin-bottom: 30px;'>Organize e acompanhe seu aprendizado</p>", unsafe_allow_html=True)
st.markdown("---")

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="stat-card">
            <h3>⏰ Horas Totais</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>42h</h1>
            <p style='opacity: 0.9;'>este mês</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="stat-card-orange">
            <h3>📅 Sessões</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>18</h1>
            <p style='opacity: 0.9;'>este mês</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="stat-card-blue">
            <h3>📚 Disciplinas</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>6</h1>
            <p style='opacity: 0.9;'>ativas</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="stat-card-green">
            <h3>🔥 Sequência</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>7</h1>
            <p style='opacity: 0.9;'>dias seguidos</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Nova Sessão", "📅 Histórico", "🎯 Metas de Estudo"])

with tab1:
    st.markdown("### 📈 Visão Geral dos Estudos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Horas por Disciplina")
        disciplinas_df = pd.DataFrame({
            'Disciplina': ['🐍 Python', '⚙️ JavaScript', '📐 Machine Learning', '🎨 Design', '📊 Matemática', '🌐 Inglês'],
            'Horas': [12, 8, 10, 5, 4, 3]
        })
        
        fig = px.bar(disciplinas_df, x='Disciplina', y='Horas',
                     color='Horas', color_continuous_scale='Purples')
        fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📅 Horas de Estudo na Semana")
        semana_df = pd.DataFrame({
            'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            'Horas': [3, 2, 4, 3, 5, 6, 2]
        })
        
        fig = px.line(semana_df, x='Dia', y='Horas',
                      markers=True, line_shape='spline')
        fig.update_traces(line=dict(color='#667eea', width=3), marker=dict(size=10))
        fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Progresso por disciplina
    st.markdown("#### 🎯 Progresso por Disciplina")
    
    disciplinas_progresso = [
        {"nome": "🐍 Python Avançado", "progresso": 75, "horas": "12h", "meta": "16h"},
        {"nome": "📐 Machine Learning", "progresso": 60, "horas": "10h", "meta": "17h"},
        {"nome": "⚙️ JavaScript Moderno", "progresso": 45, "horas": "8h", "meta": "18h"},
        {"nome": "🎨 UI/UX Design", "progresso": 30, "horas": "5h", "meta": "17h"},
    ]
    
    col1, col2 = st.columns(2)
    
    for i, disc in enumerate(disciplinas_progresso):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"**{disc['nome']}** - {disc['horas']} / {disc['meta']}")
            st.progress(disc['progresso'] / 100)
            st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.markdown("### ➕ Registrar Nova Sessão de Estudo")
    
    with st.form("sessao_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            materia = st.selectbox(
                "📚 Disciplina/Tópico",
                ["🐍 Python", "⚙️ JavaScript", "📐 Machine Learning", "🎨 Design", 
                 "📊 Matemática", "🌐 Inglês", "💻 Algoritmos", "📦 Outro"]
            )
            data = st.date_input("📅 Data", value=datetime.now())
            duracao = st.number_input("⏰ Duração (horas)", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
        
        with col2:
            tipo_estudo = st.selectbox(
                "📄 Tipo de Estudo",
                ["📚 Leitura", "💻 Prática/Código", "🎥 Vídeo Aula", "✍️ Exercícios", 
                 "📝 Anotações", "🗣️ Aula/Curso", "🧑‍🏫 Mentoria"]
            )
            produtividade = st.slider("🎯 Produtividade", 1, 10, 7)
            dificuldade = st.slider("🧩 Dificuldade", 1, 10, 5)
        
        topicos = st.text_area(
            "📝 Tópicos Estudados",
            placeholder="Ex: Funções Lambda, List Comprehension, Decorators..."
        )
        
        anotacoes = st.text_area(
            "💭 Anotações e Aprendizados",
            placeholder="O que você aprendeu hoje? Alguma dúvida ou insight importante?"
        )
        
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            submitted = st.form_submit_button("💾 Salvar Sessão", use_container_width=True)
        
        if submitted:
            st.success(f"✅ Sessão de {duracao}h em {materia} registrada com sucesso!")
            st.balloons()

with tab3:
    st.markdown("### 📅 Histórico de Estudos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_disciplina = st.selectbox("Disciplina:", ["Todas", "Python", "JavaScript", "Machine Learning"])
    with col2:
        periodo = st.selectbox("Período:", ["Última Semana", "Último Mês", "Últimos 3 Meses", "Todos"])
    with col3:
        ordenar = st.selectbox("Ordenar por:", ["Mais Recente", "Maior Duração", "Disciplina"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sessões de exemplo
    sessoes = [
        {"data": "12/01/2026", "disciplina": "🐍 Python", "duracao": 3.0, "tipo": "💻 Prática", "produtividade": 8},
        {"data": "11/01/2026", "disciplina": "📐 Machine Learning", "duracao": 2.5, "tipo": "🎥 Vídeo Aula", "produtividade": 7},
        {"data": "10/01/2026", "disciplina": "⚙️ JavaScript", "duracao": 4.0, "tipo": "💻 Prática", "produtividade": 9},
        {"data": "09/01/2026", "disciplina": "🎨 Design", "duracao": 2.0, "tipo": "📚 Leitura", "produtividade": 6},
        {"data": "08/01/2026", "disciplina": "🐍 Python", "duracao": 3.5, "tipo": "✍️ Exercícios", "produtividade": 8},
    ]
    
    for sessao in sessoes:
        st.markdown(f"""
            <div class="study-card">
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h3 style='margin: 0; color: #333;'>{sessao['disciplina']}</h3>
                        <p style='margin: 5px 0; color: #666;'>📅 {sessao['data']}</p>
                        <span style='background: #667eea; color: white; padding: 4px 12px; 
                                     border-radius: 20px; font-size: 12px;'>{sessao['tipo']}</span>
                        <span style='background: #11998e; color: white; padding: 4px 12px; 
                                     border-radius: 20px; font-size: 12px; margin-left: 8px;'>⏰ {sessao['duracao']}h</span>
                        <span style='background: #f5576c; color: white; padding: 4px 12px; 
                                     border-radius: 20px; font-size: 12px; margin-left: 8px;'>🎯 {sessao['produtividade']}/10</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("### 🎯 Metas de Estudo")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 padding: 40px; border-radius: 15px; color: white; text-align: center;'>
                <h2>Meta Semanal de Estudo</h2>
                <h1 style='font-size: 72px; margin: 20px 0;'>25 / 40</h1>
                <p style='font-size: 20px; opacity: 0.9;'>horas estudadas</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        progresso = (25 / 40) * 100
        st.progress(progresso / 100)
        st.markdown(f"<p style='text-align: center; color: #666;'>Você completou {progresso:.1f}% da sua meta semanal!</p>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ⚙️ Configurar Metas")
        meta_semanal = st.number_input("Horas Semanais", min_value=1, value=40, step=1)
        meta_diaria = st.number_input("Horas Diárias", min_value=1, value=6, step=1)
        
        if st.button("💾 Salvar Metas", use_container_width=True):
            st.success("Metas atualizadas!")
    
    # Estatísticas
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Estatísticas do Mês")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Sessões", "18", "+3")
    with col2:
        st.metric("Média Diária", "3.2h", "+0.5h")
    with col3:
        st.metric("Dias Estudados", "22", "+4")
    with col4:
        st.metric("Produtividade Média", "7.8/10", "+0.3")
