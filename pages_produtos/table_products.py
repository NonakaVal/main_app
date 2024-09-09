import streamlit as st
import pandas as pd
import mysql.connector
from tools.load_from_db import load_ids, exibir_tipos_cadastrados
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

# Função para carregar dados de uma tabela
def load_data(tabela):
    try:
        mycursor.execute(f"SELECT * FROM {tabela}")
        colunas = [desc[0] for desc in mycursor.description]
        dados = mycursor.fetchall()
        df = pd.DataFrame(dados, columns=colunas)

        # Ajustar os valores conforme necessário
        for coluna in ['preco_custo', 'preco_venda', 'estoque']:
            if coluna in df.columns:
                df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

        return df
    except mysql.connector.Error as err:
        st.error(f"Erro ao carregar dados: {err}")
        return pd.DataFrame()

# Selecionar tabela na sidebar
tabela_selecionada = st.sidebar.selectbox(
    "Escolha a Tabela",
    ["produtos", "anuncio", "vendas", "ficha_tecnica_do_produto", "inventario"]
)

# Carregar dados da tabela selecionada
df = load_data(tabela_selecionada)
st.dataframe(df)  

# Verificação se `df` é carregado com sucesso
if df.empty:
    st.warning("Nenhum dado encontrado na tabela selecionada.")
else:
    st.info("Dados carregados com sucesso.")

    # Formulário para filtro de dados na sidebar
    with st.sidebar.form("filter_form"):
        submit_button = st.form_submit_button("Buscar")

        nome_produto = st.text_input("Buscar por Nome do Produto")
        condicao_produto = st.selectbox("Buscar por Condição", ['Todos', 'Novo', 'ComoNovo', 'MuitoBom', 'Bom', 'Aceitável', 'Ruim'])
        
        # Carregar IDs dos fabricantes e categorias se necessário
        if tabela_selecionada in ["produtos", "anuncio"]:
            fabricantes = load_ids("fabricante", "id_fabricante", "nome")
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
                "Buscar por ID do Fabricante",
                id_fabricante_opcoes
            )
            id_fabricante_produto = id_fabricante_produto.split(' ')[0] if id_fabricante_produto != 'Todos' else None

        produto_anunciado = st.radio("Buscar está Anunciado", ['Todos', 'Sim', 'Não'])
    
    if submit_button:
        query = f"SELECT * FROM {tabela_selecionada} WHERE 1=1"
        params = []

        if nome_produto:
            query += " AND titulo LIKE %s"
            params.append(f"%{nome_produto}%")
        if condicao_produto != 'Todos':
            query += " AND condicao = %s"
            params.append(condicao_produto)
        if tabela_selecionada in ["produtos", "anuncio"] and id_fabricante_produto:
            query += " AND id_fabricante = %s"
            params.append(id_fabricante_produto)
        if tabela_selecionada in ["produtos", "anuncio"] and id_categoria_produto:
            query += " AND id_categoria = %s"
            params.append(id_categoria_produto)
        if tabela_selecionada in ["produtos", "anuncio"] and id_editoras_produto:
            query += " AND id_editora = %s"
            params.append(id_editoras_produto)
        if produto_anunciado != 'Todos':
            query += " AND anunciado = %s"
            params.append(1 if produto_anunciado == 'Sim' else 0)

        try:
            mycursor.execute(query, tuple(params))
            dados = mycursor.fetchall()
            colunas = [desc[0] for desc in mycursor.description]

            if dados:
                df = pd.DataFrame(dados, columns=colunas)

                # Mostrar tabela na página principal
                st.markdown("### Tabela da Pesquisa")
                st.dataframe(df)
            else:
                st.write("Nenhum dado encontrado com os critérios selecionados.")
        except mysql.connector.Error as err:
            st.error(f"Erro ao consultar dados: {err}")

    if tabela_selecionada in ["produtos", "anuncio", "vendas"]:
        exibir_tipos_cadastrados(mycursor)
