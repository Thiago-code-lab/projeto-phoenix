import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Diário - Meu LifeOS",
    page_icon="📔"
)

st.title("📔 Meu Diário")
st.write("Registre seus pensamentos e reflexões diárias.")

# Formulário para nova entrada
with st.form("diario_form"):
    st.subheader("Nova Entrada")
    
    # Campos do formulário
    data = st.date_input("Data", datetime.now())
    titulo = st.text_input("Título")
    conteudo = st.text_area("Conteúdo", 
                          placeholder="Como foi seu dia? O que aprendeu?")
    
    # Botão para salvar
    submitted = st.form_submit_button("Salvar")
    if submitted:
        if titulo or conteudo:
            st.success("Entrada salva com sucesso!")
        else:
            st.warning("Adicione um título ou conteúdo para salvar.")

# Seção de entradas
st.subheader("Entradas")
st.info("Nenhuma entrada encontrada. Comece adicionando sua primeira entrada acima.")
