##################################################################################################################
##################################################################################################################
## Pagina pesquisa de tabelas de produtos
##################################################################################################################
##################################################################################################################

import streamlit as st
import pandas as pd
import mysql.connector
from tools.load_from_db import load_ids, exibir_tipos_cadastrados, load_data
from tools.app_config import conectar_banco_dados


# Carregar segredos do Streamlit
db_host = st.secrets["DB_HOST"]
db_user = st.secrets["DB_USER"]
db_password = st.secrets["DB_PASSWORD"]
db_database = st.secrets["DB_DATABASE"]
openai_api_key = st.secrets["OPENAI_API_KEY"]


# Conectar ao banco de dados
mydb, mycursor = conectar_banco_dados()
if mydb and mycursor:
    # Realize suas operações com mydb e mycursor aqui
    pass




option = st.sidebar.selectbox("Escolha uma opção", ["Produtos", 'Tabelas mercado livre'])
# Verificação se `df` é carregado com sucesso

if option == "Produtos":
    # Carregar dados
    df = load_data("produtos")
    st.dataframe(df)  

    if df.empty:
        st.warning("Nenhum dado encontrado na tabela de produtos.")
    else:
        st.info("Dados carregados com sucesso.")

        # Formulário para filtro de produtos na sidebar
        with st.sidebar.form("filter_form"):
            submit_button = st.form_submit_button("Buscar")


            nome_produto = st.text_input("Buscar por Nome do Produto")
            
            condicao_produto = st.selectbox("Buscar por Condição", ['Todos', 'N', 'S', 'A','B+', 'B', 'C', 'D', 'E', 'J', 'Z', 'G'])
            
            # Carregar IDs dos fabricantes e categorias
            fabricantes = load_ids("marca", "id_marca", "nome")
            categorias = load_ids("categoria", "id_categoria", "nome")
            editoras = load_ids("editora", "id_editora", 'nome')




            id_categoria_opcoes = ['Todos'] + [f"{c[0]} - {c[1]}" for c in categorias]
            id_categoria_produto = st.selectbox(
                "Buscar por ID da Categoria",
                id_categoria_opcoes
            )
            id_categoria_produto = id_categoria_produto.split(' ')[0] if id_categoria_produto != 'Todos' else None




            id_editoras_opcoes = ['Todos'] + [f"{c[0]} - {c[1]}" for c in editoras]
            id_editoras_produto = st.selectbox(
                "Buscar por ID da editora",
                id_editoras_opcoes
            )
            id_editoras_produto = id_editoras_produto.split(' ')[0] if id_editoras_produto != 'Todos' else None



            # Criação do menu de seleção múltipla com limite de itens visíveis
            id_fabricante_opcoes = ['Todos'] + [f"{f[0]} - {f[1]}" for f in fabricantes]
            id_fabricante_produto = st.selectbox(
                "Buscar por ID da Marca",
                id_fabricante_opcoes
            )
            id_fabricante_produto = id_fabricante_produto.split(' ')[0] if id_fabricante_produto != 'Todos' else None
            produto_anunciado = st.radio("Buscar está Anunciado", ['Todos', 'Sim', 'Não'])
        if submit_button:
            query = "SELECT * FROM produtos WHERE 1=1"
            params = []

            if nome_produto:
                query += " AND titulo LIKE %s"
                params.append(f"%{nome_produto}%")
            if condicao_produto != 'Todos':
                query += " AND id_condicao = %s"
                params.append(condicao_produto)
            if id_fabricante_produto:
                query += " AND id_fabricante = %s"
                params.append(id_fabricante_produto)
            if id_categoria_produto:
                query += " AND id_categoria = %s"
                params.append(id_categoria_produto)
            if id_editoras_produto:
                query += " AND id_editora = %s"
                params.append(id_editoras_produto)
            if produto_anunciado != 'Todos':
                query += " AND anunciado = %s"
                params.append(1 if produto_anunciado == 'Sim' else 0)

            try:
                mycursor.execute(query, tuple(params))
                produtos = mycursor.fetchall()
                colunas = [desc[0] for desc in mycursor.description]

                if produtos:
                    df = pd.DataFrame(produtos, columns=colunas)

                    # colunas_exibir = st.multiselect(
                    #     "Selecionar colunas para exibição", 
                    #     options=colunas, 
                    #     default=colunas,
                    #     key='colunas_exibir'
                    # )
                    # df = df[colunas_exibir]

                    # Mostrar tabela na página principal
                    st.markdown("### Tabela da Pesquisa")
                    st.dataframe(df)
                else:
                    st.write("Nenhum produto encontrado com os critérios selecionados.")
            except mysql.connector.Error as err:
                st.error(f"Erro ao consultar produtos: {err}")

        exibir_tipos_cadastrados(mycursor)
        



        # tab1, tab2, tab3 = st.tabs(["Fabricantes", "Categorias", "Editoras"])

        # with tab1:
        #     st.markdown("##### Fabricantes Cadastrados")
        #     mycursor.execute("SELECT * FROM fabricante")
        #     fabricantes = mycursor.fetchall()
        #     if fabricantes:
        #         for fabricante in fabricantes:
        #             st.write(f"**ID:** {fabricante[0]} - {fabricante[1]}")
        #     else:
        #         st.write("Nenhum fabricante cadastrado.")
        # with tab2:
        #     st.markdown("##### Categorias Cadastradas")
        #     mycursor.execute("SELECT * FROM categoria")
        #     categorias = mycursor.fetchall()
        #     if categorias:
        #         for categoria in categorias:
        #             st.write(f"**ID:** {categoria[0]} - {categoria[1]}")
        #     else:
        #         st.write("Nenhuma categoria cadastrada.")
        # with tab3:
        #             # Exibir lista de editoras existentes
        #     st.markdown("##### Editoras Cadastradas")
        #     mycursor.execute("SELECT * FROM editora")
        #     editoras = mycursor.fetchall()
        #     if editoras:
        #         for editora in editoras:
        #             st.write(f"**ID:** {editora[0]} - {editora[1]}")
        #     else:
        #         st.write("Nenhuma editora cadastrada.")


        
elif option == "Tabelas mercado livre":

    tabela_selecionada = st.sidebar.selectbox(
        "Escolha a tabela:",
        ["anuncio", "ficha_tecnica_do_produto", "vendas"]
    )

    df = load_data(tabela_selecionada)

    if df.empty:
        st.warning("Nenhum dado encontrado na tabela selecionada.")
    else:
        st.info("Dados carregados com sucesso.")
        
        # Se a tabela selecionada for 'anuncio', oferecer a opção de filtro por STATUS
        if tabela_selecionada == "anuncio":
            status_opcao = st.sidebar.radio(
                "Filtrar por status:",
                ["Todos", "Ativos", "Inativos"]
            )
            
            # Aplicar o filtro baseado na opção selecionada
            if status_opcao == "Ativos":
                df = df[df['STATUS'] == 'Ativo']
            elif status_opcao == "Inativos":
                df = df[df['STATUS'] == 'Inativo']

        st.dataframe(df)  # Exibir o DataFrame filtrado