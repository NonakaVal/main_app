##################################################################################################################
##################################################################################################################
## Funções para Controle de materiais de envio
##################################################################################################################
##################################################################################################################

import streamlit as st
from tools.app_config import conectar_banco_dados
from tools.insert_to_bd import registrar_historico

def atualizar_quantidade(id_embalagem, nova_quantidade):
    query = """
    UPDATE inventario
    SET quantidade = %s
    WHERE id_embalagem = %s
    """
    try:
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute(query, (nova_quantidade, id_embalagem))
        mydb.commit()

        detalhes = f"Quantidade da embalagem com ID '{id_embalagem}' atualizada para {nova_quantidade}."
        registrar_historico("Atualização", "inventario", detalhes)
        st.success("Quantidade Atualizada com Sucesso!!!")
    except Exception as e:
        st.error(f"Erro ao atualizar quantidade: {e}")
    finally:
        if mycursor:
            mycursor.close()
        if mydb:
            mydb.close()

# Função para consultar links por IDs de fornecedores
def view_links_por_ids_fornecedores(ids_fornecedores):
    query = """
    SELECT id_fornecedor, links
    FROM fornecedores
    WHERE id_fornecedor IN (%s)
    """
    ids_placeholder = ','.join(['%s'] * len(ids_fornecedores))
    query = query % ids_placeholder

    try:
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute(query, ids_fornecedores)
        resultados = mycursor.fetchall()

        links = {result[0]: result[1] for result in resultados}
        ids_nao_encontrados = set(ids_fornecedores) - set(links.keys())
        for id_nao_encontrado in ids_nao_encontrados:
            links[id_nao_encontrado] = "Nenhum link encontrado para o ID fornecido."

        return links
    except Exception as e:
        st.error(f"Erro ao buscar links: {e}")
        return {"Erro": "Erro ao buscar links."}
    finally:
        if mycursor:
            mycursor.close()
        if mydb:
            mydb.close()

# Função para atualizar os links de um fornecedor, mantendo os links antigos
def atualizar_links_fornecedor(id_fornecedor, novos_links):
    query = "SELECT links FROM fornecedores WHERE id_fornecedor = %s"
    try:
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute(query, (id_fornecedor,))
        resultado = mycursor.fetchone()

        if resultado:
            links_antigos = resultado[0]
            if links_antigos:
                links_antigos_lista = links_antigos.split(",")
            else:
                links_antigos_lista = []

            # Adiciona novos links, removendo duplicatas
            novos_links_lista = novos_links.split(",")
            todos_os_links = set(links_antigos_lista + novos_links_lista)

            # Atualiza os links no banco de dados
            novos_links_unidos = ",".join(todos_os_links)
            query_update = """
            UPDATE fornecedores
            SET links = %s
            WHERE id_fornecedor = %s
            """
            mycursor.execute(query_update, (novos_links_unidos, id_fornecedor))
            mydb.commit()

            detalhes = f"Links do fornecedor com ID '{id_fornecedor}' atualizados para '{novos_links_unidos}'."
            registrar_historico("Atualização", "fornecedores", detalhes)
        else:
            st.error(f"Fornecedor com ID '{id_fornecedor}' não encontrado.")

    except Exception as e:
        st.error(f"Erro ao atualizar links do fornecedor: {e}")
    finally:
        if mycursor:
            mycursor.close()
        if mydb:
            mydb.close()

# Função para cadastrar uma nova embalagem
def create_new_embalagem(id_embalagem, tipo, dimensoes, material, id_fornecedor, quantidade, links):
    query = """
    INSERT INTO inventario (id_embalagem, tipo, dimensoes, material, id_fornecedor, quantidade)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute(query, (id_embalagem, tipo, dimensoes, material, id_fornecedor, quantidade))
        mydb.commit()

        detalhes = f"Embalagem do tipo '{tipo}' registrada com sucesso."
        registrar_historico("Registro", "inventario", detalhes)

        # Atualiza os links do fornecedor
        if links:
            atualizar_links_fornecedor(id_fornecedor, links)

        st.success("Embalagem Registrada com Sucesso!!!")
    except Exception as e:
        st.error(f"Erro ao cadastrar embalagem: {e}")
    finally:
        if mycursor:
            mycursor.close()
        if mydb:
            mydb.close()

def gerar_novo_id(tabela, coluna, prefixo):
    if len(prefixo) >= 4:
        st.error("O prefixo é muito longo. Deve ter menos de 4 caracteres.")
        return None

    # Calcular o comprimento máximo do número sequencial
    comprimento_numero = 4 - len(prefixo)
    
    query = f"""
    SELECT {coluna} FROM {tabela} WHERE {coluna} REGEXP '^{prefixo}[0-9]+$' ORDER BY {coluna} DESC LIMIT 1
    """
    try:
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute(query)
        resultado = mycursor.fetchone()

        if resultado:
            ultimo_id = resultado[0]
            numero = int(ultimo_id[len(prefixo):]) + 1
            novo_id = f"{prefixo}{str(numero).zfill(comprimento_numero)}"
        else:
            novo_id = f"{prefixo}".zfill(comprimento_numero)  # Inicia com o menor número válido

        return novo_id
    except Exception as e:
        st.error(f"Erro ao gerar novo ID: {e}")
        return None
    finally:
        if mycursor:
            mycursor.close()
        if mydb:
            mydb.close()
