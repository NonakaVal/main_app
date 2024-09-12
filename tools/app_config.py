
import streamlit as st
import mysql.connector
##################################################################################################################
##################################################################################################################
## Funções de configurações gerais de conexão e segurança
##################################################################################################################
##################################################################################################################


def conectar_banco_dados():
    '''Conectar ao banco de dados configurado em .secrets
    Return: mydb, mycursor = conectar_banco_dados()
    '''
    # Carregar segredos do Streamlit
    db_host = st.secrets["DB_HOST"]
    db_user = st.secrets["DB_USER"]
    db_password = st.secrets["DB_PASSWORD"]
    db_database = st.secrets["DB_DATABASE"]

    try:
        # Estabelecer uma conexão com o servidor MySQL
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_database
        )
        mycursor = mydb.cursor()

        return mydb, mycursor
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")
        return None, None

def fechar_conexao(mydb, mycursor):
    if mycursor:
        mycursor.close()
    if mydb:
        mydb.close()

##################################################################################################################
# Conectar ao banco de dados
mydb, mycursor = conectar_banco_dados()
if mydb and mycursor:
    # Realize suas operações com mydb e mycursor aqui
    pass
##################################################################################################################
## Autenticação e login
##################################################################################################################
def login():
    with st.form("login_form"):
        username = st.text_input("Nome de Usuário")
        password = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.success("Login Bem-Sucedido!")
            else:
                st.error("Nome de usuário ou senha inválidos")

# Função de logout
def logout():
    st.session_state.logged_in = False
    st.rerun()


def authenticate(username, password):
    try:
        mycursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        return mycursor.fetchone()
    except mysql.connector.Error as err:
        st.error(f"Erro ao autenticar: {err}")
        return None
    