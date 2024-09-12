import streamlit as st

from tools.app_config import conectar_banco_dados

from tools.utils_new_product import display_menu_cadastro
from tools.crewai_setup import crew_Search
from tools.utils_update_product import editar_produto
from tools.load_from_db import buscar_produtos_por_nome
# Conectar ao banco de dados
mydb, mycursor = conectar_banco_dados()
if mydb and mycursor:
    # Realize suas operações com mydb e mycursor aqui
    pass

# Menu lateral para seleção de opções
option = st.sidebar.selectbox("Escolha uma opção", ["Registrar Produto", 'Atualilzar Produto'])

llm = st.secrets["OPENAI_API_KEY"]


if option == "Registrar Produto":
    crew_Search()
        
    display_menu_cadastro()    
    
elif option == "Atualilzar Produto":

        # Chamando a função no Streamlit
        if mydb and mycursor:

            editar_produto()


# with st.sidebar.form("query_form"):
#     nome_produto = st.text_input("Busca Rapida")
#     submit_button = st.form_submit_button("Buscar")

#     if submit_button:
#         buscar_produtos_por_nome(nome_produto) 