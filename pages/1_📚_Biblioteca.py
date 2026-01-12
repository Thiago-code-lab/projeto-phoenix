import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Biblioteca - Meu LifeOS",
    page_icon="📚",
    layout="wide"
)

# Estilo moderno
st.markdown("""
    <style>
    .book-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #667eea;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .book-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
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
    .stat-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("<h1 style='text-align: center; color: #667eea;'>📚 Minha Biblioteca</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 18px; margin-bottom: 30px;'>Organize sua jornada literária</p>", unsafe_allow_html=True)
st.markdown("---")

# Métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="stat-card">
            <h3>📖 Total de Livros</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>24</h1>
            <p style='opacity: 0.9;'>na biblioteca</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="stat-card-green">
            <h3>✅ Lidos</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>8</h1>
            <p style='opacity: 0.9;'>este ano</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="stat-card-orange">
            <h3>📚 Lendo</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>3</h1>
            <p style='opacity: 0.9;'>atualmente</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="stat-card-blue">
            <h3>⏳ Para Ler</h3>
            <h1 style='font-size: 42px; margin: 10px 0;'>13</h1>
            <p style='opacity: 0.9;'>na fila</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📚 Meus Livros", "➕ Adicionar Livro", "📊 Estatísticas", "🎯 Meta de Leitura"])

with tab1:
    st.markdown("### 📚 Biblioteca Pessoal")
    
    # Filtros
    col1, col2 = st.columns([2, 1])
    with col1:
        filtro = st.selectbox("Filtrar por:", ["Todos", "Lendo", "Lidos", "Para Ler", "Abandonados"])
    with col2:
        ordenar = st.selectbox("Ordenar por:", ["Título", "Autor", "Data", "Avaliação"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Livros de exemplo
    livros = [
        {"titulo": "Sapiens", "autor": "Yuval Noah Harari", "status": "Lido", "rating": 5, "categoria": "História"},
        {"titulo": "Atomic Habits", "autor": "James Clear", "status": "Lendo", "rating": 5, "categoria": "Autoajuda"},
        {"titulo": "1984", "autor": "George Orwell", "status": "Lido", "rating": 4, "categoria": "Ficção"},
        {"titulo": "Clean Code", "autor": "Robert Martin", "status": "Lendo", "rating": 5, "categoria": "Tecnologia"},
        {"titulo": "O Poder do Hábito", "autor": "Charles Duhigg", "status": "Para Ler", "rating": 0, "categoria": "Autoajuda"},
    ]
    
    for livro in livros:
        cor_status = {
            "Lido": "#11998e",
            "Lendo": "#f5576c",
            "Para Ler": "#667eea",
            "Abandonado": "#999"
        }
        
        st.markdown(f"""
            <div class="book-card" style='border-left-color: {cor_status[livro["status"]]}'>>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h3 style='margin: 0; color: #333;'>{livro['titulo']}</h3>
                        <p style='margin: 5px 0; color: #666;'>{livro['autor']}</p>
                        <span style='background: {cor_status[livro["status"]]}; color: white; padding: 4px 12px; 
                                     border-radius: 20px; font-size: 12px;'>{livro['status']}</span>
                        <span style='background: #f0f0f0; color: #666; padding: 4px 12px; 
                                     border-radius: 20px; font-size: 12px; margin-left: 8px;'>{livro['categoria']}</span>
                    </div>
                    <div style='text-align: right;'>
                        <p style='margin: 0; color: #f5b942; font-size: 24px;'>{'⭐' * livro['rating'] if livro['rating'] > 0 else '—'}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### ➕ Adicionar Novo Livro")
    
    with st.form("adicionar_livro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            titulo = st.text_input("📖 Título do Livro")
            autor = st.text_input("✍️ Autor")
            isbn = st.text_input("🔢 ISBN (opcional)")
        
        with col2:
            categoria = st.selectbox("🏷️ Categoria", 
                ["Ficção", "Não-ficção", "Autoajuda", "Tecnologia", "Negócios", 
                 "História", "Biografia", "Romance", "Fantasia", "Outro"])
            status = st.selectbox("📊 Status", ["Para Ler", "Lendo", "Lido", "Abandonado"])
            paginas = st.number_input("📄 Número de Páginas", min_value=1, value=300)
        
        data_inicio = st.date_input("📅 Data de Início (opcional)")
        notas = st.text_area("📝 Notas e Observações")
        
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            submitted = st.form_submit_button("💾 Adicionar", use_container_width=True)
        
        if submitted and titulo and autor:
            st.success(f"✅ Livro '{titulo}' adicionado com sucesso!")
            st.balloons()

with tab3:
    st.markdown("### 📊 Estatísticas de Leitura")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📚 Livros por Categoria")
        categorias_df = pd.DataFrame({
            'Categoria': ['Autoajuda', 'Tecnologia', 'Ficção', 'História', 'Negócios'],
            'Quantidade': [5, 7, 6, 4, 2]
        })
        
        fig = px.pie(categorias_df, values='Quantidade', names='Categoria', 
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Leitura ao Longo do Ano")
        meses_df = pd.DataFrame({
            'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            'Livros Lidos': [2, 1, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0]
        })
        
        fig = px.bar(meses_df, x='Mês', y='Livros Lidos', 
                     color_discrete_sequence=['#667eea'])
        fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Top 5 autores
    st.markdown("#### ⭐ Top 5 Autores Mais Lidos")
    autores_df = pd.DataFrame({
        'Autor': ['James Clear', 'Yuval Harari', 'Robert Martin', 'Cal Newport', 'Charles Duhigg'],
        'Livros': [3, 2, 2, 1, 1]
    })
    st.dataframe(autores_df, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("### 🎯 Meta de Leitura 2026")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 padding: 40px; border-radius: 15px; color: white; text-align: center;'>
                <h2>Meta de Leitura 2026</h2>
                <h1 style='font-size: 72px; margin: 20px 0;'>8 / 24</h1>
                <p style='font-size: 20px; opacity: 0.9;'>livros lidos</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        progresso = (8 / 24) * 100
        st.progress(progresso / 100)
        st.markdown(f"<p style='text-align: center; color: #666;'>Você está a {progresso:.1f}% da sua meta!</p>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ⚙️ Configurar Meta")
        nova_meta = st.number_input("Livros para 2026", min_value=1, value=24, step=1)
        if st.button("💾 Salvar Meta", use_container_width=True):
            st.success(f"Meta atualizada para {nova_meta} livros!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 Progresso")
        st.metric("Livros Restantes", "16")
        st.metric("Ritmo Necessário", "1.5 livros/mês")
        st.metric("Dias Médios/Livro", "45 dias")
