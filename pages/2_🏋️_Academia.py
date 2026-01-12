import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Academia - Meu LifeOS",
    page_icon="🏋️",
    layout="wide"
)

# Estilo moderno
st.markdown("""
    <style>
    .workout-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #11998e;
        margin-bottom: 15px;
    }
    .stat-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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
    .stat-card-purple {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("<h1 style='text-align: center; color: #11998e;'>🏋️ Academia</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 18px; margin-bottom: 30px;'>Acompanhe seu progresso físico</p>", unsafe_allow_html=True)
st.markdown("---")

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="stat-card">
            <h3>💪 Treinos</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>12</h1>
            <p style='opacity: 0.9;'>este mês</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="stat-card-orange">
            <h3>🔥 Calorias</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>3.2k</h1>
            <p style='opacity: 0.9;'>queimadas</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="stat-card-blue">
            <h3>⚖️ Peso</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>75kg</h1>
            <p style='opacity: 0.9;'>atual</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="stat-card-purple">
            <h3>📈 Progresso</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>+3kg</h1>
            <p style='opacity: 0.9;'>de ganho</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Registrar Treino", "📅 Histórico", "🎯 Metas"])

with tab1:
    st.markdown("### 📈 Visão Geral")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Treinos por Tipo")
        tipos_treino = pd.DataFrame({
            'Tipo': ['💪 Musculação', '🏃 Cardio', '🧘 Flexibilidade', '🤸 Funcional'],
            'Quantidade': [18, 12, 8, 6]
        })
        
        fig = px.pie(tipos_treino, values='Quantidade', names='Tipo',
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔥 Calorias Queimadas")
        calorias_df = pd.DataFrame({
            'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            'Calorias': [320, 0, 450, 380, 420, 500, 280]
        })
        
        fig = px.bar(calorias_df, x='Dia', y='Calorias',
                     color='Calorias', color_continuous_scale='Reds')
        fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Evolução do peso
    st.markdown("#### ⚖️ Evolução do Peso")
    peso_df = pd.DataFrame({
        'Data': pd.date_range(start='2025-07-01', end='2026-01-12', freq='W'),
        'Peso': [72, 72.5, 73, 73.2, 73.8, 74.2, 74.5, 74.8, 75.2, 75, 75.3, 75.5, 75.8, 76, 75.8, 76.2, 76.5, 77, 77.2, 76.8, 77.5, 78, 78.2, 78.5, 79]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=peso_df['Data'],
        y=peso_df['Peso'],
        mode='lines+markers',
        line=dict(color='#11998e', width=3),
        fill='tozeroy',
        marker=dict(size=8)
    ))
    fig.update_layout(
        height=300,
        margin=dict(t=0, b=0, l=0, r=0),
        xaxis_title="Data",
        yaxis_title="Peso (kg)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### ➕ Registrar Novo Treino")
    
    with st.form("treino_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            data_treino = st.date_input("📅 Data", value=datetime.now())
            tipo_treino = st.selectbox(
                "🏋️ Tipo de Treino",
                ["💪 Peito/Tríceps", "🔙 Costa/Bíceps", "🦵 Perna", "👐 Ombro/Abdômen", 
                 "🏃 Cardio", "🧘 Yoga/Alongamento", "🤸 Funcional", "🥊 Luta"]
            )
            duracao = st.number_input("⏱️ Duração (minutos)", min_value=5, max_value=180, value=60)
        
        with col2:
            intensidade = st.slider("💥 Intensidade", 1, 10, 7)
            calorias = st.number_input("🔥 Calorias Estimadas", min_value=0, value=300, step=10)
            peso_atual = st.number_input("⚖️ Peso Atual (kg)", min_value=30.0, max_value=200.0, value=75.0, step=0.1)
        
        exercicios = st.text_area(
            "📝 Exercícios Realizados",
            placeholder="Ex: Supino 4x12, Crucifixo 3x15, Tríceps Testa 3x12..."
        )
        
        observacoes = st.text_area(
            "💭 Observações",
            placeholder="Como você se sentiu? Alguma observação importante?"
        )
        
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)
        
        if submitted:
            st.success(f"✅ Treino de {tipo_treino} registrado com sucesso!")
            st.balloons()

with tab3:
    st.markdown("### 📅 Histórico de Treinos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_tipo = st.selectbox("Filtrar por tipo:", ["Todos", "Musculação", "Cardio", "Funcional"])
    with col2:
        periodo = st.selectbox("Período:", ["Última Semana", "Último Mês", "Últimos 3 Meses", "Todos"])
    with col3:
        ordenar = st.selectbox("Ordenar por:", ["Mais Recente", "Mais Antigo", "Maior Duração"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Treinos de exemplo
    treinos = [
        {"data": "10/01/2026", "tipo": "💪 Peito/Tríceps", "duracao": 75, "calorias": 380, "intensidade": 8},
        {"data": "08/01/2026", "tipo": "🦵 Perna", "duracao": 90, "calorias": 520, "intensidade": 9},
        {"data": "06/01/2026", "tipo": "🔙 Costa/Bíceps", "duracao": 70, "calorias": 350, "intensidade": 7},
        {"data": "05/01/2026", "tipo": "🏃 Cardio", "duracao": 45, "calorias": 420, "intensidade": 8},
        {"data": "03/01/2026", "tipo": "👐 Ombro/Abdômen", "duracao": 60, "calorias": 300, "intensidade": 7},
    ]
    
    for treino in treinos:
        st.markdown(f"""
            <div class="workout-card">
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h3 style='margin: 0; color: #333;'>{treino['tipo']}</h3>
                        <p style='margin: 5px 0; color: #666;'>📅 {treino['data']}</p>
                        <span style='background: #11998e; color: white; padding: 4px 12px; 
                                     border-radius: 20px; font-size: 12px;'>⏱️ {treino['duracao']} min</span>
                        <span style='background: #f5576c; color: white; padding: 4px 12px; 
                                     border-radius: 20px; font-size: 12px; margin-left: 8px;'>🔥 {treino['calorias']} kcal</span>
                        <span style='background: #667eea; color: white; padding: 4px 12px; 
                                     border-radius: 20px; font-size: 12px; margin-left: 8px;'>💥 Intensidade {treino['intensidade']}/10</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("### 🎯 Metas de Academia")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🎯 Metas Principais")
        
        metas = [
            {"meta": "Ganhar Massa Muscular", "atual": "75kg", "alvo": "85kg", "progresso": 30},
            {"meta": "Treinar 5x por Semana", "atual": "3x", "alvo": "5x", "progresso": 60},
            {"meta": "Supino 100kg", "atual": "75kg", "alvo": "100kg", "progresso": 75},
        ]
        
        for meta in metas:
            st.markdown(f"**{meta['meta']}** - {meta['atual']} / {meta['alvo']}")
            st.progress(meta['progresso'] / 100)
            st.markdown("<br>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ➕ Nova Meta")
        with st.form("nova_meta"):
            titulo_meta = st.text_input("Título da Meta")
            valor_atual = st.number_input("Valor Atual", min_value=0.0, step=0.1)
            valor_alvo = st.number_input("Valor Alvo", min_value=0.0, step=0.1)
            data_limite = st.date_input("Data Limite")
            
            if st.form_submit_button("💾 Adicionar Meta", use_container_width=True):
                st.success("Meta adicionada!")
    
    # Estatísticas
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Estatísticas do Mês")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Treinos", "12", "+2")
    with col2:
        st.metric("Horas Treinadas", "15h", "+3h")
    with col3:
        st.metric("Calorias Totais", "4.8k", "+800")
    with col4:
        st.metric("Sequência Atual", "5 dias", "+2")
