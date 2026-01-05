import streamlit as st
from datetime import datetime, timedelta

def show():
    st.title('🎯 Metas e Objetivos')
    
    # Abas para diferentes tipos de metas
    tab1, tab2, tab3 = st.tabs(["📅 Diárias/Semanais", "📅 Mensais/Anuais", "🏆 Longo Prazo"])
    
    with tab1:
        st.header("Metas Diárias/Semanais")
        
        # Adicionar nova meta
        with st.expander("➕ Adicionar Nova Meta"):
            with st.form("meta_diaria_form"):
                titulo = st.text_input("Título da Meta")
                descricao = st.text_area("Descrição")
                data_limite = st.date_input("Data Limite")
                prioridade = st.select_slider("Prioridade", ["Baixa", "Média", "Alta"])
                
                submitted = st.form_submit_button("Adicionar Meta")
                if submitted and titulo:
                    st.success(f"Meta '{titulo}' adicionada com sucesso!")
        
        # Lista de metas de exemplo
        metas = [
            {"título": "Estudar Python", "categoria": "Aprendizado", "prioridade": "Alta", "progresso": 75, "data_limite": "2025-01-10"},
            {"título": "Exercícios Físicos", "categoria": "Saúde", "prioridade": "Média", "progresso": 60, "data_limite": "2025-01-12"},
            {"título": "Ler Livro", "categoria": "Cultura", "prioridade": "Baixa", "progresso": 30, "data_limite": "2025-01-15"}
        ]
        
        # Exibir metas
        for meta in metas:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(meta["título"])
                    st.caption(f"Categoria: {meta['categoria']} | Prioridade: {meta['prioridade']}")
                    st.caption(f"Data Limite: {meta['data_limite']}")
                with col2:
                    st.metric("Progresso", f"{meta['progresso']}%")
                st.progress(meta["progresso"] / 100)
    
    with tab2:
        st.header("Metas Mensais/Anuais")
        
        # Visão geral com métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Metas Concluídas", "8", "+2 em relação ao mês passado")
        with col2:
            st.metric("Em Andamento", "5", "-1 em relação ao mês passado")
        with col3:
            st.metric("Taxa de Sucesso", "72%", "+5%")
        
        # Gráfico de progresso
        import pandas as pd
        import plotly.express as px
        
        dados_metas = pd.DataFrame({
            'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            'Concluídas': [5, 6, 7, 8, 8, 8],
            'Em Andamento': [3, 4, 5, 4, 5, 5]
        })
        
        fig = px.line(dados_metas, x='Mês', y=['Concluídas', 'Em Andamento'], 
                     title='Evolução das Metas', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Metas de Longo Prazo")
        
        # Linha do tempo de metas
        st.subheader("Linha do Tempo")
        
        # Exemplo de linha do tempo
        def timeline_item(year, title, description, completed=False):
            status = "✅" if completed else "⏳"
            with st.container(border=True):
                st.markdown(f"**{year} - {title}** {status}")
                st.caption(description)
        
        # Exemplos de metas de longo prazo
        timeline_item(2025, "Comprar um Imóvel", "Juntar entrada de R$ 100.000,00", False)
        timeline_item(2026, "Mestrado no Exterior", "Iniciar processo de aplicação", False)
        timeline_item(2027, "Abrir Negócio Próprio", "Plano de negócios e capital inicial", False)
        
        # Seção de sonhos e aspirações
        st.subheader("Meus Sonhos")
        sonho = st.text_area("O que você sonha em conquistar?")
        if st.button("Registrar Sonho"):
            if sonho:
                st.success("Sonho registrado com sucesso! Vamos trabalhar para realizá-lo!")

if __name__ == "__main__":
    show()
