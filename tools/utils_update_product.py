##################################################################################################################
##################################################################################################################
## Funções para Alteração de produtos
##################################################################################################################
##################################################################################################################

import streamlit as st
import mysql.connector
from tools.load_from_db import conectar_banco_dados, buscar_produtos_por_nome
from tools.insert_to_bd import registrar_historico

# Conectar ao banco de dados
mydb, mycursor = conectar_banco_dados()

def editar_produto():
    st.subheader("Editar Produto")
    
    with st.form("editar_produto_form"):
        id_produto = st.text_input("ID do Produto")
        codigo_anuncio = st.text_input("Código de Anúncio")  # Campo para o código de anúncio
        # Campos que podem ser atualizados
        nova_quantidade = st.number_input("Nova Quantidade", min_value=0, value=None)
        novo_preco = st.number_input("Novo Preço", min_value=0.0, format="%.2f", value=None)
        novo_anunciado = st.radio("Anunciado", [True, False], index=1)
        nova_imagem = st.text_input("Nova URL da Imagem")
        
        submit_button = st.form_submit_button("Atualizar Produto")

        if submit_button:
            if not id_produto:
                st.error("O ID do produto é obrigatório.")
            else:
                try:
                    # Verificar se o produto existe
                    mycursor.execute(
                        "SELECT * FROM produtos WHERE id_produto = %s",
                        (id_produto,)
                    )
                    produto = mycursor.fetchone()

                    if not produto:
                        st.error("Produto não encontrado.")
                    else:
                        nome_produto = produto[1]  
                        qtd_estoque = produto[16] 
                        preco_atual = produto[19]  
                        imagem_atual = produto[11]  

                        # Atualizar somente os campos que foram preenchidos
                        sql_update = "UPDATE produtos SET "
                        params = []
                        if nova_quantidade is not None:
                            sql_update += "estoque = %s, "
                            params.append(nova_quantidade)
                        if novo_anunciado is not None:
                            sql_update += "anunciado = %s, "
                            params.append(novo_anunciado)
                        if novo_preco is not None:
                            sql_update += "preco_venda = %s, "
                            params.append(novo_preco)
                        if nova_imagem:
                            sql_update += "imagem = %s, "
                            params.append(nova_imagem)

                        # Atualizar a coluna ITEM_ID se o código de anúncio for fornecido
                        if codigo_anuncio:
                            sql_update += "ITEM_ID = %s, "
                            params.append(codigo_anuncio)

                        # Remover a última vírgula e adicionar a cláusula WHERE
                        sql_update = sql_update.rstrip(", ") + " WHERE id_produto = %s"
                        params.append(id_produto)

                        if len(params) > 1:  # Verificar se há parâmetros para atualizar
                            mycursor.execute(sql_update, tuple(params))
                            mydb.commit()

                            # Exibir mensagem de sucesso
                            st.success(f"Produto {nome_produto} atualizado com sucesso!")

                            # Registrar histórico das alterações
                            detalhes = f"Produto com ID {id_produto}: "
                            if nova_quantidade is not None and qtd_estoque != nova_quantidade:
                                detalhes += f"Quantidade alterada de {qtd_estoque} para {nova_quantidade}. "
                            if novo_preco is not None and preco_atual != novo_preco:
                                detalhes += f"Preço alterado de R$ {preco_atual:.2f} para R$ {novo_preco:.2f}. "
                            if nova_imagem and imagem_atual != nova_imagem:
                                detalhes += f"Imagem alterada de {imagem_atual} para {nova_imagem}. "
                            if novo_anunciado is not None:
                                detalhes += f"Anunciado alterado para {novo_anunciado}. "
                            if codigo_anuncio:
                                detalhes += f"ITEM_ID alterado para {codigo_anuncio}. "

                            registrar_historico("Atualização", "produtos", detalhes)

                        else:
                            st.warning("Nenhuma alteração detectada. Nenhum dado foi atualizado.")

                except mysql.connector.Error as err:
                    st.error(f"Erro ao atualizar o produto: {err}")

    with st.sidebar.form("query_form"):
        nome_produto = st.text_input("Buscar por Nome do Produto")
        submit_button = st.form_submit_button("Buscar")

        if submit_button:
            buscar_produtos_por_nome(nome_produto)
