import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def show():
    # Configuração da página com estilo moderno
    st.markdown("""
        <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
            text-align: center;
        }
        .expense-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
        }
        .income-card {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
        }
        .balance-card {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Título principal com emoji e estilo
    st.markdown("<h1 style='text-align: center; color: #667eea;'>💰 Finanças Pessoais</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 18px;'>Gerencie suas finanças de forma inteligente</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Abas para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "💸 Despesas", "💵 Receitas", "📈 Investimentos"])
    
    with tab1:
        st.markdown("### 📈 Dashboard Financeiro")
        
        # Cards de métricas principais com estilo personalizado
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
                <div class="income-card">
                    <h3>💵 Receita Mensal</h3>
                    <h2>R$ 5.000,00</h2>
                    <p style='color: #d4f8ff;'>↑ +2% vs mês anterior</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="expense-card">
                    <h3>💸 Despesas</h3>
                    <h2>R$ 3.200,00</h2>
                    <p style='color: #ffd4e5;'>↓ -5% vs mês anterior</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="balance-card">
                    <h3>💰 Saldo</h3>
                    <h2>R$ 1.800,00</h2>
                    <p style='color: #d4ffe5;'>↑ +7% vs mês anterior</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
                <div class="metric-card">
                    <h3>🎯 Taxa Poupança</h3>
                    <h2>36%</h2>
                    <p style='color: #e5e4ff;'>Meta: 30%</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos lado a lado
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🍕 Gastos por Categoria")
            # Dados de gastos por categoria
            categorias_df = pd.DataFrame({
                'Categoria': ['🍔 Alimentação', '🏠 Moradia', '🚗 Transporte', '🎮 Lazer', '💊 Saúde', '📚 Educação'],
                'Valor': [850, 1200, 450, 300, 250, 150]
            })
            
            fig = px.pie(
                categorias_df,
                values='Valor',
                names='Categoria',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
            fig.update_layout(
                showlegend=False,
                height=350,
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Evolução Mensal")
            # Dados de evolução dos últimos 6 meses
            meses = ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            evolucao_df = pd.DataFrame({
                'Mês': meses,
                'Receitas': [4800, 5000, 4900, 5100, 4950, 5000],
                'Despesas': [3400, 3300, 3500, 3200, 3350, 3200],
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=evolucao_df['Mês'], 
                y=evolucao_df['Receitas'],
                name='Receitas',
                line=dict(color='#4facfe', width=3),
                fill='tonexty',
                mode='lines+markers'
            ))
            fig.add_trace(go.Scatter(
                x=evolucao_df['Mês'], 
                y=evolucao_df['Despesas'],
                name='Despesas',
                line=dict(color='#f5576c', width=3),
                mode='lines+markers'
            ))
            fig.update_layout(
                height=350,
                margin=dict(t=20, b=0, l=0, r=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de últimas transações
        st.markdown("#### 📝 Últimas Transações")
        transacoes_df = pd.DataFrame({
            '📅 Data': ['10/01/2026', '08/01/2026', '05/01/2026', '03/01/2026', '01/01/2026'],
            '📋 Descrição': ['Supermercado', 'Netflix', 'Combustível', 'Restaurante', 'Academia'],
            '🏷️ Categoria': ['Alimentação', 'Lazer', 'Transporte', 'Alimentação', 'Saúde'],
            '💵 Valor': ['R$ 235,00', 'R$ 49,90', 'R$ 180,00', 'R$ 125,00', 'R$ 150,00'],
            '📊 Tipo': ['Despesa', 'Despesa', 'Despesa', 'Despesa', 'Despesa']
        })
        st.dataframe(transacoes_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("### 💸 Gerenciar Despesas")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### ➕ Registrar Nova Despesa")
            with st.form("despesa_form", clear_on_submit=True):
                valor = st.number_input("💰 Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
                
                col_cat, col_data = st.columns(2)
                with col_cat:
                    categoria = st.selectbox(
                        "🏷️ Categoria",
                        ["🍔 Alimentação", "🏠 Moradia", "🚗 Transporte", "🎮 Lazer", "💊 Saúde", "📚 Educação", "👕 Vestuário", "📱 Outros"]
                    )
                with col_data:
                    data = st.date_input("📅 Data", value=datetime.now())
                
                descricao = st.text_area("📝 Descrição", placeholder="Adicione detalhes sobre a despesa...")
                
                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    submitted = st.form_submit_button("💾 Salvar Despesa", use_container_width=True)
                with col_btn2:
                    st.form_submit_button("🔄 Limpar", use_container_width=True)
                
                if submitted:
                    st.success(f"✅ Despesa de R$ {valor:.2f} registrada com sucesso!")
                    st.balloons()
        
        with col2:
            st.markdown("#### 📊 Resumo de Despesas")
            
            # Card de total do mês
            st.markdown("""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                     padding: 30px; border-radius: 15px; text-align: center; color: white; margin-bottom: 20px;'>
                    <h2>Total do Mês</h2>
                    <h1 style='font-size: 48px; margin: 10px 0;'>R$ 3.200,00</h1>
                    <p style='font-size: 18px;'>🎯 Orçamento: R$ 3.500,00 | Restante: R$ 300,00</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Progresso por categoria
            st.markdown("##### 📈 Orçamento por Categoria")
            categorias_orcamento = {
                '🍔 Alimentação': (850, 1000),
                '🚗 Transporte': (450, 500),
                '🎮 Lazer': (300, 400),
                '💊 Saúde': (250, 300)
            }
            
            for cat, (gasto, limite) in categorias_orcamento.items():
                percentual = (gasto / limite) * 100
                cor = '#43e97b' if percentual < 80 else '#f5576c' if percentual > 100 else '#ffa500'
                st.markdown(f"**{cat}** - R$ {gasto:.2f} / R$ {limite:.2f}")
                st.progress(min(percentual / 100, 1.0))
    
    with tab3:
        st.markdown("### 💵 Gerenciar Receitas")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### ➕ Registrar Nova Receita")
            with st.form("receita_form", clear_on_submit=True):
                valor_receita = st.number_input("💰 Valor (R$)", min_value=0.01, step=0.01, format="%.2f", key="receita_valor")
                
                col_cat, col_data = st.columns(2)
                with col_cat:
                    tipo_receita = st.selectbox(
                        "🏷️ Tipo",
                        ["💼 Salário", "💸 Freelance", "📈 Investimentos", "🎁 Bônus", "💰 Outros"]
                    )
                with col_data:
                    data_receita = st.date_input("📅 Data", value=datetime.now(), key="receita_data")
                
                descricao_receita = st.text_area("📝 Descrição", placeholder="Adicione detalhes sobre a receita...", key="receita_desc")
                
                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    submitted_receita = st.form_submit_button("💾 Salvar Receita", use_container_width=True)
                with col_btn2:
                    st.form_submit_button("🔄 Limpar", use_container_width=True)
                
                if submitted_receita:
                    st.success(f"✅ Receita de R$ {valor_receita:.2f} registrada com sucesso!")
                    st.balloons()
        
        with col2:
            st.markdown("#### 📊 Fontes de Receita")
            
            receitas_df = pd.DataFrame({
                'Fonte': ['💼 Salário', '💸 Freelance', '📈 Investimentos', '🎁 Bônus'],
                'Valor': [4000, 600, 300, 100]
            })
            
            fig = px.bar(
                receitas_df,
                x='Fonte',
                y='Valor',
                color='Valor',
                color_continuous_scale='Teal',
                text='Valor'
            )
            fig.update_traces(texttemplate='R$ %{text}', textposition='outside')
            fig.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="",
                yaxis_title="Valor (R$)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### 📈 Carteira de Investimentos")
        
        # Card de total investido
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     padding: 20px; border-radius: 15px; text-align: center; color: white;'>
                    <h4>💼 Total Investido</h4>
                    <h2>R$ 40.500,00</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                     padding: 20px; border-radius: 15px; text-align: center; color: white;'>
                    <h4>📈 Rendimento Total</h4>
                    <h2>R$ 4.850,00</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                     padding: 20px; border-radius: 15px; text-align: center; color: white;'>
                    <h4>💹 Rentabilidade</h4>
                    <h2>11.97%</h2>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 🥧 Distribuição de Carteira")
            investimentos = {
                "Tipo": ["💰 Tesouro Direto", "📊 Ações", "🏢 FIIs", "💳 CDB"],
                "Valor Investido": [15000, 8500, 12000, 5000],
                "Rendimento (%)": [12.5, 8.3, 15.2, 9.7]
            }
            
            fig = px.pie(
                values=investimentos["Valor Investido"],
                names=investimentos["Tipo"],
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
            fig.update_layout(
                showlegend=False,
                height=350,
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Detalhes dos Investimentos")
            inv_df = pd.DataFrame(investimentos)
            
            # Adicionar coluna de rendimento em reais
            inv_df['💵 Rendimento (R$)'] = inv_df.apply(
                lambda row: f"R$ {(row['Valor Investido'] * row['Rendimento (%)'] / 100):.2f}", 
                axis=1
            )
            inv_df['💰 Valor (R$)'] = inv_df['Valor Investido'].apply(lambda x: f"R$ {x:,.2f}")
            inv_df['📈 Rent. (%)'] = inv_df['Rendimento (%)'].apply(lambda x: f"{x}%")
            
            st.dataframe(
                inv_df[['Tipo', '💰 Valor (R$)', '📈 Rent. (%)', '💵 Rendimento (R$)']],
                use_container_width=True,
                hide_index=True
            )
        
        # Gráfico de evolução do patrimônio
        st.markdown("#### 📈 Evolução do Patrimônio")
        meses = pd.date_range(start='2025-07-01', end='2026-01-01', freq='MS')
        patrimonio_df = pd.DataFrame({
            'Mês': meses,
            'Valor': [35000, 36200, 37500, 38100, 39200, 40500, 45350]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=patrimonio_df['Mês'],
            y=patrimonio_df['Valor'],
            fill='tozeroy',
            line=dict(color='#667eea', width=3),
            mode='lines+markers',
            marker=dict(size=8),
            name='Patrimônio'
        ))
        fig.update_layout(
            height=300,
            margin=dict(t=20, b=0, l=0, r=0),
            xaxis_title="",
            yaxis_title="Valor (R$)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show()
