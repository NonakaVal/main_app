import streamlit as st
from tools.app_config import conectar_banco_dados
from tools.insert_to_bd import  registrar_historico
from tools.load_from_db import view_embalagens, load_ids, exibir_tipos_cadastrados
from tools.utils_inventario import gerar_novo_id,  view_links_por_ids_fornecedores, atualizar_quantidade, create_new_embalagem


# Menu principal do Streamlit
option = st.sidebar.radio("Escolha a Opção", [
    "Gerenciar Embalagens", 
    "Alterar Quantidade",
    "Registrar Fornecedor",
    # "Consultar Links",

    "Links dos Fornecedores"
])

if option == "Gerenciar Embalagens":
    with st.form("embalagem_form"):
        tipo = st.selectbox("Tipo de Embalagem", ['caixa', 'plástico', 'proteção', 'outros'])
        dimensoes = st.text_input("Dimensões")
        material = st.text_input("Material")

        fornecedores = load_ids("fornecedores", "id_fornecedor", "nome")
        fornecedores_opcoes = [f"{f[1]} (ID: {f[0]})" for f in fornecedores]
        fornecedor_selecionado = st.selectbox("Fornecedor", ["Selecione um fornecedor"] + fornecedores_opcoes)
        if fornecedor_selecionado != "Selecione um fornecedor":
            id_fornecedor = fornecedor_selecionado.split(" (ID: ")[1][:-1]
        else:
            id_fornecedor = None

        quantidade = st.number_input("Quantidade", min_value=0, value=0)
        links = st.text_area("Links (separados por vírgula)")

        if st.form_submit_button("Cadastrar Embalagem"):
            if id_fornecedor is None:
                st.error("Selecione um ID de fornecedor válido.")
            else:
                novo_id_embalagem = gerar_novo_id("inventario", "id_embalagem", "X")
                create_new_embalagem(novo_id_embalagem, tipo, dimensoes, material, id_fornecedor, quantidade, links)

    with st.expander("Tabela Embalagens"):
        view_embalagens()
        


# elif option == "Consultar Links":
#     with st.form("links_form"):
#         ids_fornecedores = st.text_input("IDs dos Fornecedores (separados por vírgula)")
#         ids_fornecedores = [x.strip() for x in ids_fornecedores.split(",") if x.strip()]

#         if st.form_submit_button("Consultar Links"):
#             if not ids_fornecedores:
#                 st.error("Digite pelo menos um ID de fornecedor.")
#             else:
#                 links = view_links_por_ids_fornecedores(ids_fornecedores)
#                 st.write("### Links por Fornecedor")
#                 for id_fornecedor, link in links.items():
#                     st.write(f"**ID Fornecedor:** {id_fornecedor} - **Links:** {link}")

#     with st.expander("Lista de Fornecedores Cadastrados"):
#         mydb, mycursor = conectar_banco_dados()
#         mycursor.execute("SELECT DISTINCT id_fornecedor, nome FROM fornecedores")
#         fornecedores = mycursor.fetchall()
#         if fornecedores:
#             st.write("### Lista de Fornecedores")
#             for fornecedor in fornecedores:
#                 st.write(f"**ID:** {fornecedor[0]} - {fornecedor[1]}")
#         else:
#             st.write("Nenhum fornecedor cadastrado.")
elif option == "Alterar Quantidade":
    with st.form("alterar_quantidade_form"):
        id_embalagem = st.text_input("ID da Embalagem")
        diminuir_quantidade = st.form_submit_button("Diminuir Quantidade em 1")
        quantidade_atual = st.number_input("Quantidade Atual", min_value=0, value=0)

        # Botão para diminuir a quantidade em 1

        atualizar_quantidade_btn = st.form_submit_button("Atualizar Quantidade")

        if diminuir_quantidade:
            if id_embalagem:
                nova_quantidade = quantidade_atual - 1
                if nova_quantidade < 0:
                    st.error("A quantidade não pode ser negativa.")
                else:
                    atualizar_quantidade(id_embalagem, nova_quantidade)
            else:
                st.error("Digite um ID de embalagem válido.")

        if atualizar_quantidade_btn:
            if not id_embalagem:
                st.error("Digite um ID de embalagem válido.")
            else:
                atualizar_quantidade(id_embalagem, quantidade_atual)
    view_embalagens()   
    with st.expander("Lista de Fornecedores Cadastrados"):
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute("SELECT DISTINCT id_fornecedor, nome FROM fornecedores")
        fornecedores = mycursor.fetchall()
        if fornecedores:
            st.write("### Lista de Fornecedores")
            for fornecedor in fornecedores:
                st.write(f"**ID:** {fornecedor[0]} - {fornecedor[1]}")
        else:
            st.write("Nenhum fornecedor cadastrado.")    


elif option == "Registrar Fornecedor":
    with st.form("fornecedor_form"):
        nome_fornecedor = st.text_input("Nome do Fornecedor")

        if st.form_submit_button("Registrar Fornecedor"):
            if not nome_fornecedor:
                st.error("Nome do fornecedor é obrigatório.")
            else:
                try:
                    mydb, mycursor = conectar_banco_dados()
                    
                    mycursor.execute("SELECT COUNT(*) FROM fornecedores WHERE nome = %s", (nome_fornecedor,))
                    fornecedor_existente = mycursor.fetchone()[0]

                    if fornecedor_existente > 0:
                        st.error("Fornecedor com esse nome já está cadastrado.")
                    else:
                        novo_id = gerar_novo_id("fornecedores", "id_fornecedor", "S")
                        query = "INSERT INTO fornecedores (id_fornecedor, nome) VALUES (%s, %s)"
                        mycursor.execute(query, (novo_id, nome_fornecedor))
                        mydb.commit()

                        detalhes = f"Fornecedor '{nome_fornecedor}' com ID {novo_id} registrado com sucesso."
                        registrar_historico("Registro", "fornecedores", detalhes)

                        st.success("Fornecedor Registrado com Sucesso!!!")
                except Exception as e:
                    st.error(f"Erro ao registrar fornecedor: {e}")
                finally:
                    if mycursor:
                        mycursor.close()
                    if mydb:
                        mydb.close()

    with st.expander("Lista de Fornecedores Cadastrados"):
        mydb, mycursor = conectar_banco_dados()
        mycursor.execute("SELECT DISTINCT id_fornecedor, nome FROM fornecedores")
        fornecedores = mycursor.fetchall()
        if fornecedores:
            for fornecedor in fornecedores:
                st.write(f"**ID:** {fornecedor[0]} - {fornecedor[1]}")
        else:
            st.write("Nenhum fornecedor cadastrado.")
elif option == "Links dos Fornecedores":
    st.header("Alterar Links dos Fornecedores")

    # Selecionar Fornecedor
    fornecedores = load_ids("fornecedores", "id_fornecedor", "nome")
    id_fornecedor_dict = {c[1]: c[0] for c in fornecedores}
    nome_fornecedor = st.selectbox("Nome do Fornecedor", list(id_fornecedor_dict.keys()))
    id_fornecedor = id_fornecedor_dict.get(nome_fornecedor)

    if id_fornecedor:
        # Consultar e exibir links do fornecedor selecionado
        links_existentes = view_links_por_ids_fornecedores([id_fornecedor])
        links_existentes = links_existentes.get(id_fornecedor, "")
        st.write(f"**Links Atuais para o Fornecedor {nome_fornecedor}:** {links_existentes}")

        # Adicionar Novo Link
        novo_link = st.text_area("Novos Link")

        if st.button("Adicionar Novo Link"):
            if not novo_link:
                st.error("Digite um novo link.")
            else:
                try:
                    mydb, mycursor = conectar_banco_dados()

                    # Buscar links existentes
                    mycursor.execute("SELECT links FROM fornecedores WHERE id_fornecedor = %s", (id_fornecedor,))
                    resultado = mycursor.fetchone()
                    
                    if resultado:
                        links_existentes = resultado[0].split(',') if resultado[0] else []

                        # Adicionar o novo link
                        if novo_link not in links_existentes:
                            links_existentes.append(novo_link)

                        # Converter lista de volta para string
                        novos_links = ','.join(links_existentes)

                        # Atualizar na base de dados
                        query = """
                        UPDATE fornecedores
                        SET links = %s
                        WHERE id_fornecedor = %s
                        """
                        mycursor.execute(query, (novos_links, id_fornecedor))
                        mydb.commit()

                        detalhes = f"Links do fornecedor com ID '{id_fornecedor}' atualizados para {novos_links}."
                        registrar_historico("Atualização", "fornecedores", detalhes)

                        st.success("Links Atualizados com Sucesso!!!")
                    else:
                        st.error("Fornecedor não encontrado.")
                        
                except Exception as e:
                    st.error(f"Erro ao atualizar links: {e}")
                finally:
                    if mycursor:
                        mycursor.close()
                    if mydb:
                        mydb.close()


