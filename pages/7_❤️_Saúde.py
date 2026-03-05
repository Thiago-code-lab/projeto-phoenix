import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

def show():
    st.title('❤️ Saúde e Bem-Estar')
    
    # Abas para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "💪 Atividade Física", "🍎 Nutrição", "😴 Sono"])
    
    with tab1:
        st.header("Visão Geral da Saúde")
        
        # Métricas de saúde
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Batimento Cardíaco", "72 bpm", "-2 bpm")
        with col2:
            st.metric("Pressão Arterial", "120/80", "Normal")
        with col3:
            st.metric("Passos Hoje", "5,842", "de 8.000")
        with col4:
            st.metric("Horas de Sono", "7h 23m", "Boa noite")
        
        # Gráfico de saúde semanal
        st.subheader("Sua Saúde na Semana")
        
        # Dados de exemplo
        dias = [(datetime.now() - timedelta(days=i)).strftime('%A')[:3] for i in range(6, -1, -1)]
        dados_saude = pd.DataFrame({
            'Dia': dias,
            'Nível de Estresse': [3, 4, 2, 5, 3, 2, 4],
            'Energia': [7, 6, 8, 5, 7, 8, 6],
            'Qualidade do Sono': [8, 7, 9, 6, 8, 9, 7]
        })
        
        fig = px.line(dados_saude, x='Dia', y=['Nível de Estresse', 'Energia', 'Qualidade do Sono'],
                     title='Métricas de Saúde na Semana', markers=True,
                     labels={'value': 'Pontuação', 'variable': 'Métrica'},
                     color_discrete_map={
                         'Nível de Estresse': '#FF4B4B',
                         'Energia': '#4CAF50',
                         'Qualidade do Sono': '#1E88E5'
                     })
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Atividade Física")
        
        # Dados de exercícios
        exercicios = [
            {"data": "2025-01-01", "tipo": "Corrida", "duracao": 45, "calorias": 320, "intensidade": "Alta"},
            {"data": "2025-01-02", "tipo": "Musculação", "duracao": 60, "calorias": 280, "intensidade": "Média"},
            {"data": "2025-01-03", "tipo": "Ciclismo", "duracao": 90, "calorias": 550, "intensidade": "Alta"},
            {"data": "2025-01-04", "tipo": "Yoga", "duracao": 60, "calorias": 180, "intensidade": "Baixa"},
            {"data": "2025-01-05", "tipo": "Natação", "duracao": 45, "calorias": 400, "intensidade": "Alta"},
        ]
        
        # Gráfico de calorias por tipo de exercício
        df_exercicios = pd.DataFrame(exercicios)
        fig1 = px.bar(df_exercicios, x='tipo', y='calorias', color='intensidade',
                     title='Calorias Queimadas por Tipo de Exercício',
                     color_discrete_map={"Alta": "#FF4B4B", "Média": "#FFC107", "Baixa": "#4CAF50"})
        st.plotly_chart(fig1, use_container_width=True)
        
        # Formulário para adicionar novo exercício
        with st.expander("➕ Adicionar Atividade Física"):
            with st.form("exercicio_form"):
                col1, col2 = st.columns(2)
                with col1:
                    tipo = st.selectbox("Tipo de Exercício", ["Corrida", "Caminhada", "Ciclismo", "Natação", "Musculação", "Yoga", "Outro"])
                    data = st.date_input("Data")
                with col2:
                    duracao = st.number_input("Duração (minutos)", min_value=1, max_value=240, value=30)
                    intensidade = st.select_slider("Intensidade", ["Baixa", "Média", "Alta"])
                
                submitted = st.form_submit_button("Registrar Atividade")
                if submitted:
                    st.success(f"Atividade registrada: {duracao} minutos de {tipo} com intensidade {intensidade}")
    
    with tab3:
        st.header("Nutrição e Alimentação")
        
        # Contador de macronutrientes
        st.subheader("Ingestão Diária")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Calorias", "1,850", "de 2.200")
        with col2:
            st.metric("Proteínas", "120g", "de 150g")
        with col3:
            st.metric("Carboidratos", "210g", "de 250g")
        with col4:
            st.metric("Gorduras", "65g", "de 70g")
        
        # Registro de refeições
        st.subheader("Registro de Refeições")
        
        # Exemplo de refeições
        refeicoes = [
            {"hora": "08:00", "refeicao": "Café da Manhã", "alimentos": "Omelete com queijo e pão integral", "calorias": 420},
            {"hora": "12:30", "refeicao": "Almoço", "alimentos": "Arroz integral, feijão, frango grelhado e salada", "calorias": 650},
            {"hora": "16:00", "refeicao": "Lanche", "alimentos": "Iogurte natural com granola", "calorias": 280},
            {"hora": "20:00", "refeicao": "Jantar", "alimentos": "Sopa de legumes e pão integral", "calorias": 500}
        ]
        
        for refeicao in refeicoes:
            with st.container():
                st.markdown(f"**{refeicao['hora']} - {refeicao['refeicao']}** ({refeicao['calorias']} kcal)")
                st.caption(refeicao['alimentos'])
        
        # Adicionar nova refeição
        with st.expander("➕ Adicionar Refeição"):
            with st.form("refeicao_form"):
                col1, col2 = st.columns(2)
                with col1:
                    tipo_refeicao = st.selectbox("Refeição", ["Café da Manhã", "Lanche da Manhã", "Almoço", "Lanche da Tarde", "Jantar", "Ceia"])
                    hora = st.time_input("Horário")
                with col2:
                    alimentos = st.text_area("Alimentos consumidos")
                    calorias = st.number_input("Total de calorias", min_value=0, step=1)
                
                submitted = st.form_submit_button("Registrar Refeição")
                if submitted:
                    st.success(f"Refeição registrada: {tipo_refeicao} às {hora.strftime('%H:%M')}")
    
    with tab4:
        st.header("Monitoramento do Sono")
        
        # Estatísticas do sono
        st.subheader("Qualidade do Sono")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Duração Média", "7h 15m", "+12min")
        with col2:
            st.metric("Eficiência", "88%", "+3%")
        with col3:
            st.metric("Tempo para Dormir", "15 min", "-2min")
        with col4:
            st.metric("Despertares", "2.3", "-0.7")
        
        # Gráfico de sono semanal
        st.subheader("Padrão de Sono na Semana")
        
        dados_sono = pd.DataFrame({
            'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            'Hora de Dormir': ['22:30', '23:15', '22:45', '23:00', '00:30', '01:15', '23:45'],
            'Hora de Acordar': ['06:15', '06:30', '06:15', '06:30', '07:45', '08:30', '07:15'],
            'Qualidade': [8, 7, 8, 9, 6, 7, 8],
            'Fase REM': [90, 85, 95, 100, 80, 75, 85],
            'Sono Profundo': [120, 110, 115, 125, 90, 100, 110]
        })
        
        fig = px.bar(dados_sono, x='Dia', y=['Fase REM', 'Sono Profundo'], 
                     title='Tempo nas Fases do Sono (minutos)',
                     color_discrete_map={"Fase REM": "#5E35B1", "Sono Profundo": "#3949AB"},
                     barmode='stack')
        st.plotly_chart(fig, use_container_width=True)
        
        # Dicas para melhorar o sono
        with st.expander("💡 Dicas para Melhorar o Sono"):
            st.markdown("""
            - Mantenha um horário regular para dormir e acordar, mesmo nos finais de semana
            - Evite cafeína e álcool antes de dormir
            - Mantenha o quarto escuro, fresco e silencioso
            - Evite telas pelo menos 1 hora antes de dormir
            - Pratique técnicas de relaxamento antes de dormir
            - Evite refeições pesadas à noite
            - Pratique exercícios físicos regularmente, mas evite atividades intensas perto da hora de dormir
            """)

if __name__ == "__main__":
    show()
