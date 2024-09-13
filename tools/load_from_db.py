##################################################################################################################
##################################################################################################################
## Funções Querys do banco de dados
##################################################################################################################
##################################################################################################################

import streamlit as st
import pandas as pd
import mysql.connector
import mysql.connector
from tools.app_config import conectar_banco_dados
from datetime import datetime, timedelta

# Exemplo de uso da função
mydb, mycursor = conectar_banco_dados()
if mydb and mycursor:
    # Realize suas operações com mydb e mycursor aqui
    pass

def get_product_details(titulo, serial_number):

    try:
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute("""
            SELECT * FROM produtos WHERE titulo = %s AND serial_number = %s
        """, (titulo, serial_number))
        return mycursor.fetchone()
    except mysql.connector.Error as err:
        st.error(f"Erro ao buscar detalhes do produto: {err}")
        return None

def product_exists(titulo, serial_number):
    try:
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute("""
            SELECT COUNT(*) FROM produtos 
            WHERE titulo = %s AND serial_number = %s
        """, (titulo, serial_number))
        return mycursor.fetchone()[0] > 0
    except mysql.connector.Error as err:
        st.error(f"Erro ao verificar existência do produto: {err}")
        return False

# Função auxiliar para carregar IDs
def load_ids(table_name, id_column, name_column):
    mydb, mycursor = conectar_banco_dados()
    query = f"SELECT {id_column}, {name_column} FROM {table_name}"
    mycursor.execute(query)
    ids = mycursor.fetchall()
    mydb.close()
    return ids

@st.cache_data(ttl="2h")
def load_data(table_name):
    try:
        query = f"SELECT * FROM {table_name}"
        mycursor.execute(query)
        colunas = [desc[0] for desc in mycursor.description]
        dados = mycursor.fetchall()
        df = pd.DataFrame(dados, columns=colunas)

        # Ajustar os valores conforme necessário
        for coluna in ['preco_custo', 'preco_venda', 'estoque']:
            if coluna in df.columns:
                df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

        return df
    except mysql.connector.Error as err:
        st.error(f"Erro ao carregar dados da tabela {table_name}: {err}")
        return pd.DataFrame()
  
    
def obter_nome_e_imagem_produto(id_produto):
    mycursor.execute("SELECT titulo, imagem FROM produtos WHERE id_produto = %s", (id_produto,))
    resultado = mycursor.fetchone()
    return resultado if resultado else (None, None)

def obter_nome_e_preco_produto(id_produto):
    mycursor.execute("SELECT titulo, preco_venda FROM produtos WHERE id_produto = %s", (id_produto,))
    resultado = mycursor.fetchone()
    return resultado if resultado else (None, None)

def obter_nome_e_quantidade_produto(id_produto):
    mycursor.execute("SELECT titulo, estoque FROM produtos WHERE id_produto = %s", (id_produto,))
    resultado = mycursor.fetchone()
    return resultado if resultado else (None, None)

    

def view_embalagens():
    # Função para carregar e exibir a tabela de embalagens
    def load_embalagens():
        try:
            mydb, mycursor = conectar_banco_dados()
            mycursor.execute("SELECT * FROM inventario")
            result = mycursor.fetchall()
            columns = [i[0] for i in mycursor.description]  # Obter os nomes das colunas
            if result:
                df = pd.DataFrame(result, columns=columns)  # Criar um DataFrame
                return df
            else:
                return pd.DataFrame(columns=["Nenhuma embalagem encontrada."])  # DataFrame vazio com uma mensagem
        except Exception as e:
            st.error(f"Erro ao carregar embalagens: {e}")
            return pd.DataFrame(columns=["Erro ao carregar dados."])
        finally:
            if mycursor:
                mycursor.close()
            if mydb:
                mydb.close()

    # Exibir o botão para atualizar a tabela
    if st.button("Atualizar Tabela de Embalagens"):
        df = load_embalagens()
        st.write("### Tabela de Embalagens")
        st.dataframe(df)  # Mostrar o DataFrame

def exibir_df(tabela, colunas=None):
    """
    Exibe os itens cadastrados na tabela especificada com colunas específicas.

    Args:
        tabela (str): Nome da tabela para buscar os itens.
        colunas (list, optional): Lista de colunas a serem exibidas. Se None, todas as colunas são exibidas.
    """
    try:
        if colunas:
            colunas_str = ", ".join(colunas)
        else:
            colunas_str = "*"
        
        query = f"""
            SELECT {colunas_str}
            FROM {tabela}
        """
        
        # Executa a consulta
        mycursor.execute(query)
        itens = mycursor.fetchall()
        
        # Obtém os nomes das colunas
        if colunas is None:
            columns = [i[0] for i in mycursor.description]
        else:
            columns = colunas
        
        # Cria o DataFrame com os resultados
        if itens:
            df = pd.DataFrame(itens, columns=columns)
            st.dataframe(df)  # Mostra o DataFrame
        else:
            st.write("Nenhum item encontrado.")
    
    except mysql.connector.Error as err:
        st.error(f"Erro ao buscar os itens cadastrados: {err}")
import streamlit as st

def exibir_tipos_cadastrados(mycursor):
    """
    Exibe os dados das tabelas 'marca', 'categoria' e 'editora' em abas no Streamlit.
    """
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Marcas", "Categorias", "Editoras", "Edições", "Condição"])

    with tab1:
        st.markdown("##### Marcas Cadastradas")
        mycursor.execute("SELECT * FROM marca")
        marcas = mycursor.fetchall()
        if marcas:
            for marca in marcas:
                st.write(f"**ID:** {marca[0]} - {marca[1]}")
        else:
            st.write("Nenhuma marca cadastrada.")
    
    with tab2:
        st.markdown("##### Categorias Cadastradas")
        mycursor.execute("SELECT * FROM categoria")
        categorias = mycursor.fetchall()
        if categorias:
            for categoria in categorias:
                st.write(f"**ID:** {categoria[0]} - {categoria[1]}")
        else:
            st.write("Nenhuma categoria cadastrada.")
    
    with tab3:
        st.markdown("##### Editoras Cadastradas")
        mycursor.execute("SELECT * FROM editora")
        editoras = mycursor.fetchall()
        if editoras:
            for editora in editoras:
                st.write(f"**ID:** {editora[0]} - {editora[1]}")
        else:
            st.write("Nenhuma editora cadastrada.")
    with tab4:
        st.markdown("##### Editoras Cadastradas")
        mycursor.execute("SELECT * FROM edicao")
        editoras = mycursor.fetchall()
        if editoras:
            for editora in editoras:
                st.write(f"**ID:** {editora[0]} - {editora[1]}")
        else:
            st.write("Nenhuma editora cadastrada.")
    with tab5:
        st.markdown("##### condicao Cadastradas")
        mycursor.execute("SELECT * FROM condicao")
        editoras = mycursor.fetchall()
        if editoras:
            for editora in editoras:
                st.write(f"{editora[0]} - {editora[1]} - {editora[2]}")
        else:
            st.write("Nenhuma ondicao cadastrada.")

def buscar_produtos_por_nome(nome_produto):
    # Conectar ao banco de dados
    mydb, mycursor = conectar_banco_dados()

    if not mydb or not mycursor:
        st.write("Erro ao conectar ao banco de dados.")
        return
    
    if not nome_produto:
        # Caso o nome_produto esteja vazio, buscar todos os produtos
        query = "SELECT * FROM produtos"
        params = []
    else:
        # Preparar query e parâmetros para busca específica
        query = "SELECT * FROM produtos WHERE titulo LIKE %s"
        params = [f"%{nome_produto}%"]
    
    # Executar a consulta
    mycursor.execute(query, tuple(params))
    result = mycursor.fetchall()
    
    if result:
        for row in result:
            with st.expander(f"{row[1]}"):
                id_ = f"{row[0]}"
                st.markdown(f"""
                            ```copiar
                            {id_}
                            ```
                            """)
                # st.write(f"**Descrição:** {row[12]}")
                # st.write(f"**Condição:** {row[5]}")
                # st.write(f"**Completo:** {'Sim' if row[6] else 'Não'}")
                # st.write(f"**Número de Série:** {row[7]}")
                # st.write(f"**Número de Série da Caixa:** {row[8]}")
                st.write(f"**Quantidade em Estoque:** {row[16]}")
                
                
                # # Exibe a imagem com tamanho padrão e verifica possíveis erros
                # try:
                #     st.image(row[11], width=180, caption=f"Imagem do Produto {row[11]}")
                # except:
                #     st.write("Erro ao carregar a imagem. Verifique o link da imagem.")
                
                st.write(f"**Valor:** {row[19]}")
                # st.write(f"**ID do Fabricante:** {row[3]}")
                # st.write(f"**ID da Categoria:** {row[2]}")
                # st.write(f"**ID da Editora:** {row[4]}")
                # st.write(f"**ID da Embalagem:** {row[20]}")
                st.write(f"**Status Anúncio:** {'Sim' if row[23] == 1 else 'Não'}")
                id_anc = f"{row[24]}"
                st.markdown(f"""
                            ```copiar
                            {id_anc}
                            ```
                            """)

                st.write("---")
    else:
        st.write("Nenhum produto encontrado com o nome fornecido.")

# Função para consultar o histórico de atualizações
def consultar_historico():


    # Definir intervalo de datas padrão (ontem e hoje)
    data_fim = datetime.now().date()
    data_inicio = data_fim - timedelta(days=1)

    # Seleção de intervalo de datas com chaves exclusivas
    data_inicio = st.sidebar.date_input("Data Inicial", value=data_inicio, key='data_inicio')
    data_fim = st.sidebar.date_input("Data Final", value=data_fim, key='data_fim')

    if data_inicio > data_fim:
        st.error("A Data Inicial deve ser anterior à Data Final.")
        return

    # Consulta SQL com intervalo de datas
    query = """
    SELECT * FROM historico 
    WHERE data_operacao BETWEEN %s AND %s 
    ORDER BY data_operacao DESC
    """
    params = (data_inicio, data_fim)

    try:
        mycursor.execute(query, params)
        historico = mycursor.fetchall()

        if historico:
            for operacao in historico:
                with st.expander(f"ID: {operacao[0]} - {operacao[1]} - {operacao[4]}"):
                    st.write(f"**Tipo de Operação:** {operacao[1]}")
                    st.write(f"**Tabela Afetada:** {operacao[2]}")
                    st.write(f"**Detalhes:** {operacao[3]}")
                    st.write(f"**Data da Operação:** {operacao[4]}")
                    st.write("---")
        else:
            st.write("Nenhuma operação encontrada para o intervalo selecionado.")
    except mysql.connector.Error as err:
        st.error(f"Erro ao consultar histórico: {err}")


