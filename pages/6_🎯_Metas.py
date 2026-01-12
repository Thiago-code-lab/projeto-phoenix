import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Metas - Meu LifeOS",
    page_icon="🎯",
    layout="wide"
)

# Estilo moderno
st.markdown("""
    <style>
    .goal-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 15px;
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    .goal-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    </style>
""", unsafe_allow_html=True)

def show():
    # Cabeçalho
    st.markdown("<h1 style='text-align: center; color: #667eea;'>🎯 Metas e Objetivos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 18px; margin-bottom: 30px;'>Defina, acompanhe e conquiste seus objetivos</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="stat-card">
                <h3>🎯 Total</h3>
                <h1 style='font-size: 42px; margin: 10px 0;'>24</h1>
                <p style='opacity: 0.9;'>metas ativas</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card-green">
                <h3>✅ Concluídas</h3>
                <h1 style='font-size: 42px; margin: 10px 0;'>8</h1>
                <p style='opacity: 0.9;'>este mês</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-card-orange">
                <h3>⏳ Em Andamento</h3>
                <h1 style='font-size: 42px; margin: 10px 0;'>12</h1>
                <p style='opacity: 0.9;'>progredindo</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="stat-card-blue">
                <h3>📈 Taxa Sucesso</h3>
                <h1 style='font-size: 42px; margin: 10px 0;'>75%</h1>
                <p style='opacity: 0.9;'>de conclusão</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Abas para diferentes tipos de metas
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Diárias/Semanais", "📊 Dashboard", "🏆 Longo Prazo", "➕ Nova Meta"])
    
    with tab1:
        st.markdown("### 📅 Metas Diárias e Semanais")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📋 Minhas Metas")
            
            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtro = st.selectbox("Filtrar por:", ["Todas", "Em Andamento", "Concluídas", "Atrasadas"])
            with col_f2:
                prioridade_filtro = st.selectbox("Prioridade:", ["Todas", "Alta", "Média", "Baixa"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Metas de exemplo
            metas = [
                {"titulo": "💻 Estudar Python", "categoria": "📚 Aprendizado", "prioridade": "Alta", "progresso": 75, "data_limite": "15/01/2026", "dias_restantes": 3},
                {"titulo": "🏃 Correr 5km", "categoria": "💪 Saúde", "prioridade": "Média", "progresso": 60, "data_limite": "13/01/2026", "dias_restantes": 1},
                {"titulo": "📖 Ler 50 páginas", "categoria": "📚 Cultura", "prioridade": "Baixa", "progresso": 80, "data_limite": "12/01/2026", "dias_restantes": 0},
                {"titulo": "🎨 Terminar design", "categoria": "💼 Trabalho", "prioridade": "Alta", "progresso": 45, "data_limite": "14/01/2026", "dias_restantes": 2},
            ]
            
            for meta in metas:
                cor_prioridade = {
                    "Alta": "#f5576c",
                    "Média": "#ffa500",
                    "Baixa": "#11998e"
                }
                
                cor_dias = "#f5576c" if meta['dias_restantes'] == 0 else "#ffa500" if meta['dias_restantes'] <= 2 else "#11998e"
                
                st.markdown(f"""
                    <div class="goal-card" style='border-left-color: {cor_prioridade[meta["prioridade"]]}'>
                        <div style='display: flex; justify-content: space-between; align-items: start;'>
                            <div style='flex: 1;'>
                                <h3 style='margin: 0; color: #333;'>{meta['titulo']}</h3>
                                <p style='margin: 5px 0; color: #666;'>{meta['categoria']}</p>
                                <div style='margin-top: 10px;'>
                                    <span style='background: {cor_prioridade[meta["prioridade"]]}; color: white; padding: 4px 12px; 
                                                 border-radius: 20px; font-size: 12px;'>{meta['prioridade']}</span>
                                    <span style='background: #f0f0f0; color: #666; padding: 4px 12px; 
                                                 border-radius: 20px; font-size: 12px; margin-left: 8px;'>📅 {meta['data_limite']}</span>
                                    <span style='background: {cor_dias}; color: white; padding: 4px 12px; 
                                                 border-radius: 20px; font-size: 12px; margin-left: 8px;'>⏰ {meta['dias_restantes']} dias</span>
                                </div>
                            </div>
                            <div style='text-align: right; min-width: 80px;'>
                                <h2 style='margin: 0; color: #667eea;'>{meta['progresso']}%</h2>
                            </div>
                        </div>
                        <div style='margin-top: 15px;'>
                            <div style='background: #e0e0e0; border-radius: 10px; height: 8px; overflow: hidden;'>
                                <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                                            width: {meta['progresso']}%; height: 100%;'></div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📊 Resumo Semanal")
            
            st.markdown("""
                <div style='background: white; padding: 20px; border-radius: 15px; 
                     box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); margin-bottom: 15px;'>
                    <h4 style='color: #333; margin-top: 0;'>🎯 Progresso Geral</h4>
                    <h1 style='color: #667eea; font-size: 48px; margin: 10px 0;'>68%</h1>
                    <p style='color: #666;'>das metas concluídas</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Metas por categoria
            st.markdown("#### 📈 Por Categoria")
            categorias_meta = [
                {"cat": "📚 Aprendizado", "concluidas": 5, "total": 8},
                {"cat": "💪 Saúde", "concluidas": 7, "total": 10},
                {"cat": "💼 Trabalho", "concluidas": 3, "total": 6},
            ]
            
            for cat in categorias_meta:
                perc = (cat['concluidas'] / cat['total']) * 100
                st.markdown(f"**{cat['cat']}** - {cat['concluidas']}/{cat['total']}")
                st.progress(perc / 100)
                st.markdown("<br>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📊 Dashboard de Metas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Evolução Mensal")
            meses_df = pd.DataFrame({
                'Mês': ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
                'Concluídas': [5, 6, 7, 8, 8, 10],
                'Total': [8, 10, 12, 12, 11, 14]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Concluídas', x=meses_df['Mês'], y=meses_df['Concluídas'],
                                marker_color='#11998e'))
            fig.add_trace(go.Bar(name='Total', x=meses_df['Mês'], y=meses_df['Total'],
                                marker_color='#e0e0e0'))
            fig.update_layout(
                height=350,
                margin=dict(t=0, b=0, l=0, r=0),
                barmode='overlay',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Taxa de Conclusão")
            taxa_df = pd.DataFrame({
                'Categoria': ['Saúde', 'Aprendizado', 'Trabalho', 'Finanças', 'Bem-estar'],
                'Taxa': [85, 72, 68, 90, 78]
            })
            
            fig = px.bar(taxa_df, x='Categoria', y='Taxa',
                         color='Taxa', color_continuous_scale='Teal',
                         text='Taxa')
            fig.update_traces(texttemplate='%{text}%', textposition='outside')
            fig.update_layout(
                height=350,
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=False,
                yaxis_range=[0, 100]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap de produtividade
        st.markdown("#### 🔥 Mapa de Calor - Última Semana")
        
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        horas = ['06h', '09h', '12h', '15h', '18h', '21h']
        
        # Dados simulados de produtividade
        import numpy as np
        dados_heatmap = np.random.randint(0, 10, size=(len(horas), len(dias_semana)))
        
        fig = px.imshow(dados_heatmap,
                        labels=dict(x="Dia da Semana", y="Horário", color="Produtividade"),
                        x=dias_semana,
                        y=horas,
                        color_continuous_scale='Purples',
                        aspect="auto")
        fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 🏆 Metas de Longo Prazo")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🎯 Grandes Objetivos")
            
            # Timeline de metas de longo prazo
            metas_lp = [
                {
                    "ano": "2026",
                    "titulo": "🏠 Comprar Imóvel Próprio",
                    "descricao": "Juntar entrada de R$ 100.000 e financiar apartamento",
                    "progresso": 35,
                    "status": "⏳ Em andamento"
                },
                {
                    "ano": "2027",
                    "titulo": "🎓 Mestrado no Exterior",
                    "descricao": "Iniciar processo de aplicação para universidades",
                    "progresso": 15,
                    "status": "📝 Planejando"
                },
                {
                    "ano": "2028",
                    "titulo": "💼 Abrir Negócio Próprio",
                    "descricao": "Desenvolver plano de negócios e capital inicial",
                    "progresso": 5,
                    "status": "💡 Idealizando"
                },
                {
                    "ano": "2029",
                    "titulo": "🌍 Viagem ao Redor do Mundo",
                    "descricao": "Visitar 20 países em 6 meses",
                    "progresso": 0,
                    "status": "🌟 Sonho"
                },
            ]
            
            for meta_lp in metas_lp:
                st.markdown(f"""
                    <div style='background: white; padding: 25px; border-radius: 15px; 
                         box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); margin-bottom: 20px;
                         border-left: 5px solid #667eea;'>
                        <div style='display: flex; justify-content: space-between; align-items: start;'>
                            <div>
                                <span style='background: #667eea; color: white; padding: 4px 12px; 
                                             border-radius: 20px; font-size: 14px; font-weight: 600;'>{meta_lp['ano']}</span>
                                <h3 style='margin: 10px 0 5px 0; color: #333;'>{meta_lp['titulo']}</h3>
                                <p style='color: #666; margin: 0 0 10px 0;'>{meta_lp['descricao']}</p>
                                <span style='background: #f0f0f0; color: #666; padding: 4px 12px; 
                                             border-radius: 20px; font-size: 12px;'>{meta_lp['status']}</span>
                            </div>
                            <div style='text-align: right; min-width: 80px;'>
                                <h2 style='margin: 0; color: #667eea;'>{meta_lp['progresso']}%</h2>
                            </div>
                        </div>
                        <div style='margin-top: 15px;'>
                            <div style='background: #e0e0e0; border-radius: 10px; height: 8px; overflow: hidden;'>
                                <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                                            width: {meta_lp['progresso']}%; height: 100%;'></div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 💭 Meus Sonhos")
            
            st.text_area(
                "O que você sonha em conquistar?",
                height=200,
                placeholder="Escreva seus maiores sonhos e aspirações..."
            )
            
            if st.button("💾 Registrar Sonho", use_container_width=True):
                st.success("Sonho registrado! Continue trabalhando para realizá-lo! 🌟")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("""
                <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                     padding: 20px; border-radius: 15px; text-align: center;'>
                    <h4 style='color: #333; margin: 0 0 10px 0;'>💡 Inspiração</h4>
                    <p style='color: #555; font-style: italic; margin: 0;'>
                        "O futuro pertence àqueles que acreditam na beleza de seus sonhos."
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### ➕ Criar Nova Meta")
        
        with st.form("nova_meta_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                titulo_meta = st.text_input("🎯 Título da Meta", placeholder="Ex: Ler 12 livros este ano")
                categoria_meta = st.selectbox(
                    "🏷️ Categoria",
                    ["📚 Aprendizado", "💪 Saúde", "💼 Trabalho", "💰 Finanças", 
                     "❤️ Relacionamentos", "🎨 Hobbies", "🌟 Crescimento Pessoal"]
                )
                prioridade_meta = st.select_slider(
                    "⚡ Prioridade",
                    options=["Baixa", "Média", "Alta", "Urgente"]
                )
            
            with col2:
                tipo_meta = st.selectbox(
                    "📊 Tipo de Meta",
                    ["📅 Diária", "📆 Semanal", "📋 Mensal", "📈 Anual", "🏆 Longo Prazo"]
                )
                data_inicio = st.date_input("📅 Data de Início", value=datetime.now())
                data_limite = st.date_input("🏁 Data Limite")
            
            descricao_meta = st.text_area(
                "📝 Descrição da Meta",
                height=100,
                placeholder="Descreva sua meta em detalhes..."
            )
            
            st.markdown("#### 🎯 Critérios de Sucesso")
            col1, col2, col3 = st.columns(3)
            with col1:
                metrica_1 = st.text_input("Métrica 1", placeholder="Ex: 12 livros")
            with col2:
                metrica_2 = st.text_input("Métrica 2", placeholder="Ex: 1 por mês")
            with col3:
                metrica_3 = st.text_input("Métrica 3", placeholder="Ex: Opcional")
            
            st.markdown("#### 🚀 Plano de Ação")
            passos = st.text_area(
                "Quais passos você precisa dar?",
                height=100,
                placeholder="Liste os passos necessários para alcançar esta meta..."
            )
            
            col_btn1, col_btn2 = st.columns([1, 5])
            with col_btn1:
                submitted = st.form_submit_button("🎯 Criar Meta", use_container_width=True)
            
            if submitted and titulo_meta:
                st.success("🎉 Meta criada com sucesso! Vamos alcançá-la juntos!")
                st.balloons()
            elif submitted:
                st.warning("⚠️ Por favor, adicione um título para a meta.")

if __name__ == "__main__":
    show()
