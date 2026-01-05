import streamlit as st

def show():
    st.title('💰 Finanças Pessoais')
    
    # Abas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "💸 Despesas", "📈 Investimentos"])
    
    with tab1:
        st.header("Visão Geral Financeira")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Receita Mensal", "R$ 5.000,00", "+2%")
        with col2:
            st.metric("Despesas", "R$ 3.200,00", "-5%")
        with col3:
            st.metric("Saldo", "R$ 1.800,00", "+7%")
            
        st.subheader("Gráfico de Gastos por Categoria")
        # Gráfico de pizza de exemplo
        import pandas as pd
        import numpy as np
        
        chart_data = pd.DataFrame(
            np.random.randn(5, 3),
            columns=['Alimentação', 'Moradia', 'Lazer']
        )
        st.bar_chart(chart_data)
    
    with tab2:
        st.header("Registrar Despesa")
        with st.form("despesa_form"):
            valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
            categoria = st.selectbox(
                "Categoria",
                ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"]
            )
            data = st.date_input("Data")
            descricao = st.text_area("Descrição")
            
            submitted = st.form_submit_button("Salvar Despesa")
            if submitted:
                st.success(f"Despesa de R$ {valor:.2f} registrada com sucesso!")
    
    with tab3:
        st.header("Meus Investimentos")
        investimentos = {
            "Tipo": ["Tesouro Direto", "Ações", "FIIs", "CDB"],
            "Valor Investido (R$)": [15000, 8500, 12000, 5000],
            "Rendimento (%)": [12.5, 8.3, 15.2, 9.7]
        }
        st.dataframe(investimentos)
        
        st.subheader("Distribuição de Carteira")
        # Gráfico de rosca
        import plotly.express as px
        
        fig = px.pie(
            values=investimentos["Valor Investido (R$)"],
            names=investimentos["Tipo"],
            hole=0.5,
            title="Distribuição da Carteira de Investimentos"
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show()
