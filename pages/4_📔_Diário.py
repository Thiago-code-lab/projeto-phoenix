import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Diário - Meu LifeOS",
    page_icon="📔",
    layout="wide"
)

# Estilo minimalista e elegante
st.markdown("""
    <style>
    .diary-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    .entry-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    .entry-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    .mood-emoji {
        font-size: 32px;
        margin-right: 10px;
    }
    .stat-badge {
        background: #f0f2f6;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        color: #666;
        display: inline-block;
        margin-right: 10px;
    }
    .quote-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 30px 0;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        font-size: 16px;
        line-height: 1.8;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho elegante
st.markdown("""
    <div class="diary-header">
        <h1 style='font-size: 48px; margin-bottom: 10px;'>📔 Meu Diário</h1>
        <p style='font-size: 20px; opacity: 0.95;'>Um espaço para refletir e registrar sua jornada</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["✍️ Nova Entrada", "📚 Entradas Recentes", "📊 Estatísticas", "🎯 Prompt do Dia"])

with tab1:
    st.markdown("### ✍️ Escrever Nova Entrada")
    
    with st.form("diario_form", clear_on_submit=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            data = st.date_input("📅 Data", datetime.now())
            titulo = st.text_input("🏷️ Título da Entrada", placeholder="Dê um título para este dia...")
        
        with col2:
            humor = st.select_slider(
                "😊 Como você se sente?",
                options=["😢 Triste", "😐 Neutro", "🙂 Bem", "😄 Feliz", "🤩 Incrível"]
            )
            categoria = st.selectbox(
                "🏷️ Categoria",
                ["💭 Reflexão", "✨ Gratidão", "🎯 Conquistas", "🙏 Desafios", "💡 Aprendizados", "🌟 Sonhos"]
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Área de escrita principal
        conteudo = st.text_area(
            "📝 Escreva seus pensamentos...",
            height=300,
            placeholder="Como foi seu dia? O que você aprendeu? Pelo que é grato(a)?\n\nDeixe seus pensamentos fluirem livremente..."
        )
        
        # Perguntas reflexivas
        with st.expander("💡 Perguntas Reflexivas (opcional)"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**O que foi bem hoje?**")
                pontos_positivos = st.text_area("Pontos positivos", height=100, label_visibility="collapsed")
                
                st.markdown("**Pelo que sou grato(a)?**")
                gratidao = st.text_area("Gratidão", height=100, label_visibility="collapsed")
            
            with col2:
                st.markdown("**O que poderia melhorar?**")
                melhorias = st.text_area("Melhorias", height=100, label_visibility="collapsed")
                
                st.markdown("**Aprendizado do dia**")
                aprendizado = st.text_area("Aprendizado", height=100, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        with col_btn1:
            submitted = st.form_submit_button("💾 Salvar Entrada", use_container_width=True)
        with col_btn2:
            st.form_submit_button("🗑️ Limpar", use_container_width=True)
        
        if submitted:
            if titulo and conteudo:
                st.success("✅ Entrada salva com sucesso!")
                st.balloons()
            else:
                st.warning("⚠️ Por favor, adicione um título e conteúdo para salvar.")

with tab2:
    st.markdown("### 📚 Minhas Entradas")
    
    # Filtros
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        busca = st.text_input("🔍 Buscar", placeholder="Pesquisar em entradas...")
    with col2:
        filtro_humor = st.selectbox("Humor", ["Todos", "Feliz", "Bem", "Neutro", "Triste"])
    with col3:
        filtro_categoria = st.selectbox("Categoria", ["Todas", "Reflexão", "Gratidão", "Conquistas"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Entradas de exemplo
    entradas = [
        {
            "data": "12/01/2026",
            "titulo": "Um dia de conquistas",
            "humor": "😄 Feliz",
            "categoria": "🎯 Conquistas",
            "preview": "Hoje finalmente consegui terminar o projeto que estava desenvolvendo há semanas. A sensação de realização é incrível...",
            "palavras": 342
        },
        {
            "data": "10/01/2026",
            "titulo": "Reflexões sobre o ano",
            "humor": "🙂 Bem",
            "categoria": "💭 Reflexão",
            "preview": "Olhando para trás, vejo o quanto cresci nos últimos meses. Cada desafio foi uma oportunidade de aprendizado...",
            "palavras": 528
        },
        {
            "data": "08/01/2026",
            "titulo": "Gratidão pela família",
            "humor": "🤩 Incrível",
            "categoria": "✨ Gratidão",
            "preview": "Hoje passei o dia com minha família e percebi o quanto sou sortudo por tê-los ao meu lado...",
            "palavras": 215
        },
        {
            "data": "05/01/2026",
            "titulo": "Superando desafios",
            "humor": "😐 Neutro",
            "categoria": "🙏 Desafios",
            "preview": "Foi um dia difícil, mas consegui manter o foco e seguir em frente. Aprendi que persistência é fundamental...",
            "palavras": 412
        },
    ]
    
    for entrada in entradas:
        st.markdown(f"""
            <div class="entry-card">
                <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;'>
                    <div>
                        <h3 style='margin: 0; color: #333;'>{entrada['titulo']}</h3>
                        <p style='margin: 5px 0; color: #999; font-size: 14px;'>📅 {entrada['data']}</p>
                    </div>
                    <div style='text-align: right;'>
                        <span class='mood-emoji'>{entrada['humor'].split()[0]}</span>
                    </div>
                </div>
                <p style='color: #666; line-height: 1.6; margin-bottom: 15px;'>{entrada['preview']}</p>
                <div>
                    <span class='stat-badge'>{entrada['categoria']}</span>
                    <span class='stat-badge'>📝 {entrada['palavras']} palavras</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("### 📊 Estatísticas do Diário")
    
    # Cards de estatísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 padding: 25px; border-radius: 15px; color: white; text-align: center;'>
                <h3>📖 Total</h3>
                <h1 style='font-size: 42px; margin: 10px 0;'>48</h1>
                <p style='opacity: 0.9;'>entradas</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                 padding: 25px; border-radius: 15px; color: white; text-align: center;'>
                <h3>🔥 Sequência</h3>
                <h1 style='font-size: 42px; margin: 10px 0;'>12</h1>
                <p style='opacity: 0.9;'>dias seguidos</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                 padding: 25px; border-radius: 15px; color: white; text-align: center;'>
                <h3>✍️ Palavras</h3>
                <h1 style='font-size: 42px; margin: 10px 0;'>18.5k</h1>
                <p style='opacity: 0.9;'>escritas</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                 padding: 25px; border-radius: 15px; color: white; text-align: center;'>
                <h3>😄 Humor Médio</h3>
                <h1 style='font-size: 42px; margin: 10px 0;'>7.8</h1>
                <p style='opacity: 0.9;'>de 10</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 😊 Distribuição de Humor")
        import plotly.express as px
        humor_df = pd.DataFrame({
            'Humor': ['Incrível', 'Feliz', 'Bem', 'Neutro', 'Triste'],
            'Quantidade': [12, 18, 10, 6, 2]
        })
        fig = px.pie(humor_df, values='Quantidade', names='Humor',
                     color_discrete_sequence=['#11998e', '#667eea', '#4facfe', '#f5576c', '#999'],
                     hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📅 Entradas por Mês")
        meses_df = pd.DataFrame({
            'Mês': ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez', 'Jan'],
            'Entradas': [8, 12, 10, 15, 18, 20, 12]
        })
        fig = px.bar(meses_df, x='Mês', y='Entradas',
                     color='Entradas', color_continuous_scale='Purples')
        fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### 🎯 Prompt de Reflexão do Dia")
    
    # Citação inspiradora
    st.markdown("""
        <div class="quote-card">
            <p style='font-size: 24px; font-style: italic; color: #333; margin: 0;'>
                "A vida é 10% o que acontece com você e 90% como você reage a isso."
            </p>
            <p style='color: #666; margin-top: 15px; font-size: 16px;'>- Charles R. Swindoll</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Prompts de reflexão
    st.markdown("#### 💭 Perguntas para Refletir Hoje")
    
    prompts = [
        "🌟 Qual foi o momento mais significativo do seu dia?",
        "💪 Que desafio você superou recentemente?",
        "❤️ Por quem ou pelo quê você é grato hoje?",
        "🎯 O que você aprendeu sobre si mesmo esta semana?",
        "🌈 Se você pudesse mudar algo no seu dia, o que seria?",
        "🚀 Qual é o próximo passo em direção aos seus sonhos?"
    ]
    
    col1, col2 = st.columns(2)
    
    for i, prompt in enumerate(prompts):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
                <div style='background: white; padding: 20px; border-radius: 12px; 
                     box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); margin-bottom: 15px;'>
                    <p style='color: #667eea; font-weight: 600; font-size: 16px; margin: 0;'>{prompt}</p>
                </div>
            """, unsafe_allow_html=True)
