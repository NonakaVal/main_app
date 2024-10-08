##################################################################################################################
##################################################################################################################
## Funções para Cadastro de produtos
##################################################################################################################
##################################################################################################################

import os
import streamlit as st
from mysql.connector import Error
import random
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from tools.app_config import conectar_banco_dados, fechar_conexao
from tools.load_from_db import load_ids, product_exists, get_product_details
from tools.insert_to_bd import registrar_historico
import qrcode
from io import BytesIO
from qrcode.image.pure import PyPNGImage





# Conectar ao banco de dados
mydb, mycursor = conectar_banco_dados()
if mydb and mycursor:
    # Realize suas operações com mydb e mycursor aqui
    pass

# def generate_sku(category_id, additional_prefix="CGS"):
#     # Garantir que category_id tem o formato correto
#     if len(category_id) != 4 or not category_id[1:].isdigit():
#         raise ValueError("ID da categoria deve ter o formato correto (uma letra seguida por três números).")

#     # Extrair apenas os números do ID da categoria
#     category_number = category_id[1:]  # Remove a letra e mantém apenas os números

#     # Criar o prefixo do SKU
#     prefix = f"{additional_prefix}-{category_number}"  # Prefixo adicional + números da categoria

#     # Gerar um código aleatório maior (por exemplo, 6 dígitos)
#     product_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # Gera um código aleatório de 6 dígitos

#     # Formatar e retornar o SKU
#     return f"{prefix}-{product_code}"

##################################################################################################################
## Geradores de códigos e afin
##################################################################################################################

def generate_sku(category_id):
    # Garantir que category_id tem o formato correto
    if len(category_id) != 4 or not category_id[1:].isdigit():
        raise ValueError("ID da categoria deve ter o formato correto (uma letra seguida por três números).")

    # Extrair apenas os números do ID da categoria
    category_number = category_id[1:]  # Remove a letra e mantém apenas os números

    prefix = category_number  # O prefixo será os três números
    product_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # Gera um código aleatório de 4 dígitos
    return f"{prefix}-{product_code}"

def generate_barcode(code_text):
    # Gerar o código de barras Code128
    code = Code128(code_text, writer=ImageWriter())
    buffer = BytesIO()
    code.write(buffer)
    buffer.seek(0)
    return buffer


def generate_qr_code(link):
    """
    Gera um QR code a partir de um link e retorna a imagem em um buffer (BytesIO).
    
    Args:
        link (str): O link a ser embutido no QR code.
    
    Returns:
        BytesIO: Um objeto de buffer contendo a imagem do QR code.
    """
    # Gerar o QR code usando a biblioteca qrcode
    img = qrcode.make(link, image_factory=PyPNGImage)
    
    # Salvar a imagem em um buffer de memória
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)  # Retornar ao início do buffer para leitura
    
    return buffer

##################################################################################################################
## Formulário de Cadastro
##################################################################################################################

def display_menu_cadastro():
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Produto", "Categorias","Edições", "Editoras", "Fabricantes"])

    with tab1:


        with st.form("product_form", clear_on_submit=True):
            titulo_produto = st.text_input("Título do Produto")

            
            completo_produto = st.checkbox("Completo")
            manual_instrucoes_produto = st.checkbox("Manual de Instruções")
            serial_number_produto = st.text_input("Número de Série")
            serial_caixa_produto = st.text_input("Número de Série da Caixa")
            idiomas_disponiveis_produto = st.selectbox("Idiomas Disponíveis", ('Global', 'pt-BR', 'en-US', 'ja-JP'))
            
            conditions = load_ids("condicao", "id_condicao", "nome")
            id_conditions_dict = {f"{f[1]} ({f[0]})": f[0] for f in conditions}
            nome_condition = st.selectbox("condição", list(id_conditions_dict.keys()))
            id_condition = id_conditions_dict.get(nome_condition)


            categorias = load_ids("categoria", "id_categoria", "nome")
            id_categoria_dict = {c[1]: c[0] for c in categorias}
            nome_categoria = st.selectbox("Nome da Categoria", list(id_categoria_dict.keys()))
            id_categoria_produto = id_categoria_dict.get(nome_categoria)
                     # Carregar IDs e nomes

            edicoes = load_ids("edicao", "id_edicao", "nome")
            id_edicao_dict = {f[1]: f[0] for f in edicoes}
            nome_edicao = st.selectbox("Nome da edição", list(id_edicao_dict.keys()))
            id_edicao = id_edicao_dict.get(nome_edicao)


            # Carregar IDs e nomes
            marcas = load_ids("marca", "id_marca", "nome")
            id_marca_dict = {f[1]: f[0] for f in marcas}
            nome_marca = st.selectbox("Nome do Marca", list(id_marca_dict.keys()))
            id_marca = id_marca_dict.get(nome_marca)

            
            editoras = load_ids("editora", "id_editora", "nome")
            id_editora_dict = {e[1]: e[0] for e in editoras}
            nome_editora = st.selectbox("Nome da Editora", list(id_editora_dict.keys()))
            id_editora_produto = id_editora_dict.get(nome_editora)

            # Carregar imagens e IDs
            imagem_produto = st.text_input("Link da Imagem")
            descricao_produto = st.text_area("Descrição")
            conteudo_edicao_produto = st.text_area("Conteúdo da Edição")
            acessorios_incluidos_produto = st.text_area("Acessórios Incluídos")
            raridade_produto = st.slider("Raridade", min_value=1, max_value=10, value=1)
            estoque_produto = st.number_input("Estoque", min_value=0)
            data_recebimento_produto = st.date_input("Data de Recebimento")
            preco_custo_produto = st.number_input("Preço de Custo", min_value=0.00, format="%.2f")
            preco_venda_produto = st.number_input("Preço de Venda", min_value=0.00, format="%.2f")

            embalagens = load_ids("inventario", "id_embalagem", 'dimensoes')
            id_embalagens_dict = {e[1]: e[0] for e in embalagens}
            nome_embalagem = st.selectbox("Embalagem", list(id_embalagens_dict.keys()))
            id_embalagem_produto = id_embalagens_dict.get(nome_embalagem)
            codigo_universal_produto = st.text_input("Código Universal")
            anunciado_produto = st.checkbox("Anunciado")
            id_anuncio = st.text_input("Código id_anuncio")
            link = st.text_input("Link Anúncio")
   


            if st.form_submit_button("Registrar Produto"):
                print("Formulário enviado")
                if not titulo_produto or not serial_number_produto:
                    st.error("Título do produto e número de série são obrigatórios.")
                elif product_exists(titulo_produto, serial_number_produto):
                    st.error("Produto com este título e número de série já existe.")
                elif id_marca is None or id_categoria_produto is None or id_editora_produto is None:
                    st.error("Um ou mais IDs selecionados são inválidos.")
                else:
                    try:
                        sku = generate_sku(id_categoria_produto)
                        print(f"SKU gerado: {sku}")
                        barcode_buffer = generate_barcode(sku)
                        qr_code_buffer = generate_qr_code(link)
                        print("Códigos gerados")
                        
                        barcode_path = os.path.join('bar_codes', f'{sku}_barcode.png')
                        qr_code_path = os.path.join('bar_codes', f'{sku}_qr_code.png')

                        os.makedirs('bar_codes', exist_ok=True)
                        with open(barcode_path, 'wb') as f:
                            f.write(barcode_buffer.getvalue())
                        with open(qr_code_path, 'wb') as f:
                            f.write(qr_code_buffer.getvalue())

                        sql = """
                            INSERT INTO produtos (
                                id_produto, titulo, id_categoria, id_edicao, id_marca, id_editora, id_condicao, completo, manual_instrucoes,
                                serial_number, serial_caixa, idiomas_disponiveis, imagem, descricao, conteudo_edicao,
                                acessorios_incluidos, raridade, estoque, data_recebimento, preco_custo, preco_venda, id_embalagem,
                                codigo_barras, codigo_universal, anunciado, ITEM_ID, ad_link
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s
                            )
                        """
                        values = (
                            sku, titulo_produto, id_categoria_produto, id_edicao, id_marca, id_editora_produto,
                            id_condition, int(completo_produto), int(manual_instrucoes_produto),
                            serial_number_produto, serial_caixa_produto, idiomas_disponiveis_produto, imagem_produto,
                            descricao_produto, conteudo_edicao_produto, acessorios_incluidos_produto, raridade_produto,
                            estoque_produto, data_recebimento_produto, preco_custo_produto, preco_venda_produto,
                            id_embalagem_produto, barcode_path, codigo_universal_produto, int(anunciado_produto), id_anuncio, qr_code_path
                        )

                        mydb, mycursor = conectar_banco_dados()
                        mycursor.execute(sql, values)
                        mydb.commit()
                        st.success("Produto registrado com sucesso!")

                        produto = get_product_details(titulo_produto, serial_number_produto)
                        if produto:
                            st.write("Detalhes do Produto Registrado:")
                            st.json({
                                "ID do Produto": produto[0],
                                "Título": produto[1],
                                "ID da Categoria": produto[2],
                                "ID do edicao": produto[3],
                                "ID do marca": produto[4],
                                "ID da Editora": produto[5],
                                "Condição": produto[6],
                                "Completo": produto[7],
                                "Manual de Instruções": produto[8],
                                "Número de Série": produto[9],
                                "Número de Série da Caixa": produto[10],
                                "Idiomas Disponíveis": produto[11],
                                "Imagem": produto[12],
                                "Descrição": produto[13],
                                "Conteúdo da Edição": produto[14],
                                "Acessórios Incluídos": produto[15],
                                "Raridade": produto[16],
                                "Estoque": produto[17],
                                "Data de Recebimento": produto[18],
                                "Preço de Custo": produto[19],
                                "Preço de Venda": produto[20],
                                "ID da Embalagem": produto[21],
                                "Código de Barras": produto[22],
                                "Código Universal": produto[23],
                                "Anunciado": produto[24],
                                "id_anuncio": produto[25],
                                "link": produto[26]
                            })
                    except Exception as e:
                        st.error(f"Erro ao gerar ou salvar o código de barras: {e}")
    with tab2:
        with st.form("category_form"):
            nome_categoria = st.text_input("Nome da Categoria")

            if st.form_submit_button("Registrar Categoria"):
                if not nome_categoria:
                    st.error("Nome da categoria é obrigatório.")
                else:
                    mydb, mycursor = conectar_banco_dados()
                    if mydb and mycursor:
                        try:
                            # Verificar se a categoria já existe
                            mycursor.execute("SELECT COUNT(*) FROM categoria WHERE nome = %s", (nome_categoria,))
                            existe_categoria = mycursor.fetchone()[0]

                            if existe_categoria > 0:
                                st.error("Categoria com esse nome já existe.")
                            else:
                                # Obter o maior ID existente
                                mycursor.execute("SELECT id_categoria FROM categoria WHERE id_categoria REGEXP '^C[0-9]{3}$' ORDER BY id_categoria DESC LIMIT 1")
                                max_id_result = mycursor.fetchone()

                                if max_id_result:
                                    max_id = max_id_result[0]
                                    max_numero = int(max_id[1:])  # Remove o prefixo 'C' e converte para inteiro
                                    next_id = f"C{str(max_numero + 1).zfill(3)}"
                                else:
                                    next_id = 'C001'  # Se não houver ID válido, começa do 'C001'

                                # Inserir nova categoria com o ID gerado
                                sql = "INSERT INTO categoria (id_categoria, nome) VALUES (%s, %s)"
                                mycursor.execute(sql, (next_id, nome_categoria))
                                mydb.commit()

                                # Registrar no histórico
                                detalhes = f"Categoria '{nome_categoria}' com ID {next_id} registrada com sucesso."
                                registrar_historico("Registro", "categorias", detalhes)

                                st.success("Categoria Registrada com Sucesso!!!")
                        except:
                            st.error(f"Erro ao operar no banco de dados: {e}")
                        finally:
                            fechar_conexao(mydb, mycursor)
        
        st.divider()
        st.text("Categorias Cadastradas")
        mydb, mycursor = conectar_banco_dados()
        if mydb and mycursor:
            try:
                mycursor.execute("SELECT * FROM categoria")
                categorias = mycursor.fetchall()
                if categorias:
                    for categoria in categorias:
                        st.write(f"**ID:** {categoria[0]} - {categoria[1]}")
                else:
                    st.write("Nenhuma categoria cadastrada.")
            except:
                st.error(f"Erro ao buscar categorias: {e}")
            finally:
                fechar_conexao(mydb, mycursor)

    with tab3:
        with st.form("edicaoform"):
                edicao_name = st.text_input("Nome da Edição")

                if st.form_submit_button("Registrar Edição"):
                    if not edicao_name:
                        st.error("Nome do Edição é obrigatório.")
                    else:
                        mydb, mycursor = conectar_banco_dados()
                        if mydb and mycursor:
                            try:
                                # Verificar se o fabricante já existe
                                mycursor.execute("SELECT COUNT(*) FROM edicao WHERE nome = %s", (edicao_name,))
                                existe_fabricante = mycursor.fetchone()[0]

                                if existe_fabricante > 0:
                                    st.error("edicao com esse nome já existe.")
                                else:
                                    # Obter o maior ID existente
                                    mycursor.execute("SELECT id_edicao FROM edicao WHERE id_edicao REGEXP '^D[0-9]{3}$' ORDER BY id_edicao DESC LIMIT 1")
                                    max_id_result = mycursor.fetchone()

                                    if max_id_result:
                                        max_id = max_id_result[0]
                                        max_numero = int(max_id[1:])  # Remove o prefixo 'F' e converte para inteiro
                                        next_id = f"D{str(max_numero + 1).zfill(3)}"
                                    else:
                                        next_id = 'D001'  # Se não houver ID válido, começa do 'F001'

                                    # Inserir novo fabricante com o ID gerado
                                    sql = "INSERT INTO edicao (id_edicao, nome) VALUES (%s, %s)"
                                    mycursor.execute(sql, (next_id, edicao_name))
                                    mydb.commit()

                                    # Registrar no histórico
                                    detalhes = f"edicao '{edicao_name}' com ID {next_id} registrado com sucesso."
                                    registrar_historico("Registro", "edicaoform", detalhes)

                                    st.success("edicao_name Registrado com Sucesso!!!")
                            except Error as e:
                                st.error(f"Erro ao operar no banco de dados: {e}")
                            finally:
                                fechar_conexao(mydb, mycursor)
            
        st.text("edicao_name Cadastrados")
        mydb, mycursor = conectar_banco_dados()
        if mydb and mycursor:
            try:
                mycursor.execute("SELECT * FROM edicao")
                edicaos = mycursor.fetchall()
                if edicaos:
                    for edicao in edicaos:
                        st.write(f"**ID:** {edicao[0]} - {edicao[1]}")
                else:
                    st.write("Nenhum edicao cadastrado.")
            except Error as e:
                st.error(f"Erro ao buscar edicao: {e}")
            finally:
                fechar_conexao(mydb, mycursor)

    with tab4:
        with st.form("publisher_form"):
            nome_editora = st.text_input("Nome da Editora")

            if st.form_submit_button("Registrar Editora"):
                if not nome_editora:
                    st.error("Nome da editora é obrigatório.")
                else:
                    mydb, mycursor = conectar_banco_dados()
                    if mydb and mycursor:
                        try:
                            # Verificar se a editora já existe
                            mycursor.execute("SELECT COUNT(*) FROM editora WHERE nome = %s", (nome_editora,))
                            existe_editora = mycursor.fetchone()[0]

                            if existe_editora > 0:
                                st.error("Editora com esse nome já existe.")
                            else:
                                # Obter o maior ID existente
                                mycursor.execute("SELECT id_editora FROM editora WHERE id_editora REGEXP '^E[0-9]{3}$' ORDER BY id_editora DESC LIMIT 1")
                                max_id_result = mycursor.fetchone()

                                if max_id_result:
                                    max_id = max_id_result[0]
                                    max_numero = int(max_id[1:])  # Remove o prefixo 'E' e converte para inteiro
                                    next_id = f"E{str(max_numero + 1).zfill(3)}"
                                else:
                                    next_id = 'E001'  # Se não houver ID válido, começa do 'E001'

                                # Inserir nova editora com o ID gerado
                                sql = "INSERT INTO editora (id_editora, nome) VALUES (%s, %s)"
                                mycursor.execute(sql, (next_id, nome_editora))
                                mydb.commit()

                                # Registrar no histórico
                                detalhes = f"Editora '{nome_editora}' com ID {next_id} registrada com sucesso."
                                registrar_historico("Registro", "editoras", detalhes)

                                st.success("Editora Registrada com Sucesso!!!")
                        except Error as e:
                            st.error(f"Erro ao operar no banco de dados: {e}")
                        finally:
                            fechar_conexao(mydb, mycursor)
        
        st.text("Editoras Cadastradas")
        mydb, mycursor = conectar_banco_dados()
        if mydb and mycursor:
            try:
                mycursor.execute("SELECT * FROM editora")
                editoras = mycursor.fetchall()
                if editoras:
                    for editora in editoras:
                        st.write(f"**ID:** {editora[0]} - {editora[1]}")
                else:
                    st.write("Nenhuma editora cadastrada.")
            except Error as e:
                st.error(f"Erro ao buscar editoras: {e}")
            finally:
                fechar_conexao(mydb, mycursor)

    with tab5:
        with st.form("manufacturer_form"):
            nome_marca = st.text_input("Nome do id_marca")

            if st.form_submit_button("Registrar id_marca"):
                if not nome_marca:
                    st.error("Nome do id_marca é obrigatório.")
                else:
                    mydb, mycursor = conectar_banco_dados()
                    if mydb and mycursor:
                        try:
                            # Verificar se o fabricante já existe
                            mycursor.execute("SELECT COUNT(*) FROM marca WHERE nome = %s", (nome_marca,))
                            existe_fabricante = mycursor.fetchone()[0]

                            if existe_fabricante > 0:
                                st.error("nome_marca com esse nome já existe.")
                            else:
                                # Obter o maior ID existente
                                mycursor.execute("SELECT id_marca FROM marca WHERE id_marca REGEXP '^B[0-9]{3}$' ORDER BY id_marca DESC LIMIT 1")
                                max_id_result = mycursor.fetchone()

                                if max_id_result:
                                    max_id = max_id_result[0]
                                    max_numero = int(max_id[1:])  # Remove o prefixo 'F' e converte para inteiro
                                    next_id = f"B{str(max_numero + 1).zfill(3)}"
                                else:
                                    next_id = 'B001'  # Se não houver ID válido, começa do 'F001'

                                # Inserir novo fabricante com o ID gerado
                                sql = "INSERT INTO marca (id_marca, nome) VALUES (%s, %s)"
                                mycursor.execute(sql, (next_id, nome_marca))
                                mydb.commit()

                                # Registrar no histórico
                                detalhes = f"Fabricante '{nome_marca}' com ID {next_id} registrado com sucesso."
                                registrar_historico("Registro", "id_marca", detalhes)

                                st.success("nome_marca Registrado com Sucesso!!!")
                        except Error as e:
                            st.error(f"Erro ao operar no banco de dados: {e}")
                        finally:
                            fechar_conexao(mydb, mycursor)
        
        st.text("nome_marca Cadastrados")
        mydb, mycursor = conectar_banco_dados()
        if mydb and mycursor:
            try:
                mycursor.execute("SELECT * FROM marca")
                fabricantes = mycursor.fetchall()
                if fabricantes:
                    for fabricante in fabricantes:
                        st.write(f"**ID:** {fabricante[0]} - {fabricante[1]}")
                else:
                    st.write("Nenhum nome_marca cadastrado.")
            except Error as e:
                st.error(f"Erro ao buscar nome_marca: {e}")
            finally:
                fechar_conexao(mydb, mycursor)



##################################################################################################################
##################################################################################################################
##################################################################################################################
##################################################################################################################