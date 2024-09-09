import streamlit as st
import pandas as pd
import mysql.connector
import uuid
from tools.app_config import conectar_banco_dados
from tools.load_from_db import load_ids
# Exemplo de uso da função
mydb, mycursor = conectar_banco_dados()
if mydb and mycursor:
    # Realize suas operações com mydb e mycursor aqui
    pass

# def generate_product_id():
#     # Gerar um ID único baseado em UUID e formatá-lo como um EAN-13
#     new_id = str(uuid.uuid4().int)[:13]
#     return new_id

def create_new_record(table_name, column_name, value):
    try:
        sql = f"INSERT INTO {table_name} ({column_name}) VALUES (%s)"
        mycursor.execute(sql, (value,))
        mydb.commit()
        st.success(f"{table_name.capitalize()} '{value}' criada com sucesso!")
    except mysql.connector.Error as err:
        st.error(f"Erro ao criar nova {table_name}: {err}")

def create_new_embalagem():

    with st.form("embalagem_form"):
        tipo_embalagem = st.selectbox("Tipo de Embalagem", ('caixa', 'plástico', 'proteção', 'outros'))
        dimensoes_embalagem = st.text_input("Dimensões")
        material_embalagem = st.text_input("Material")
        id_fornecedor_embalagem = st.selectbox("ID do Fornecedor", [f"{f[0]} - {f[1]}" for f in load_ids("fornecedores", "id_fornecedor", "nome")])
        id_fornecedor_embalagem = id_fornecedor_embalagem.split(' ')[0]
        quantidade_embalagem = st.number_input("Quantidade", min_value=0)
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not tipo_embalagem or not dimensoes_embalagem or not material_embalagem:
                st.error("Todos os campos obrigatórios devem ser preenchidos.")
            else:
                # Verificar se já existe uma embalagem com as mesmas características
                sql_check = """
                    SELECT COUNT(*) FROM inventario
                    WHERE tipo = %s AND dimensoes = %s AND material = %s AND id_fornecedor = %s
                """
                mycursor.execute(sql_check, (tipo_embalagem, dimensoes_embalagem, material_embalagem, id_fornecedor_embalagem))
                count = mycursor.fetchone()[0]
                
                if count > 0:
                    st.error("Já existe uma embalagem com as mesmas características.")
                else:
                    sql_insert = """
                        INSERT INTO inventario (
                            id_embalagam ,tipo, dimensoes, material, id_fornecedor, quantidade
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    values = (
                        tipo_embalagem, dimensoes_embalagem, material_embalagem,
                        id_fornecedor_embalagem, quantidade_embalagem
                    )
                    try:
                        mycursor.execute(sql_insert, values)
                        mydb.commit()
                        st.success("Embalagem cadastrada com sucesso!")
                    except mysql.connector.Error as err:
                        st.error(f"Erro ao cadastrar a embalagem: {err}")

def registrar_historico(tipo_operacao, tabela_afetada, detalhes):
    try:
        sql = "INSERT INTO historico (tipo_operacao, tabela_afetada, detalhes) VALUES (%s, %s, %s)"
        val = (tipo_operacao, tabela_afetada, detalhes)
        mycursor.execute(sql, val)
        mydb.commit()
    except mysql.connector.Error as err:
        st.error(f"Erro ao registrar histórico: {err}")

