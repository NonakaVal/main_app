import os
import streamlit as st
import mysql.connector
import random
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from tools.app_config import conectar_banco_dados
from tools.crewai_setup import crew_Search
from tools.load_from_db import load_ids
from tools.insert_to_bd import registrar_historico

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
def fechar_conexao(mydb, mycursor):
    if mycursor:
        mycursor.close()
    if mydb:
        mydb.close()

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

def display_menu_cadastro():
    tab1, tab2, tab3, tab4 = st.tabs(["Produto", "Categorias", "Editoras", "Fabricantes"])

    with tab1:
        with st.expander("Pesquisar Número Universal"):
            crew_Search()
            st.divider()

        with st.form("product_form"):
            titulo_produto = st.text_input("Título do Produto")
            condicao_produto = st.selectbox("Condição", ('Novo', 'ComoNovo', 'MuitoBom', 'Bom', 'Aceitável', 'Ruim'))
            completo_produto = st.checkbox("Completo")
            manual_instrucoes_produto = st.checkbox("Manual de Instruções")
            serial_number_produto = st.text_input("Número de Série")
            serial_caixa_produto = st.text_input("Número de Série da Caixa")
            idiomas_disponiveis_produto = st.selectbox("Idiomas Disponíveis", ('Global', 'pt-BR', 'en-US', 'ja-JP'))
            
            # Carregar IDs e nomes
            fabricantes = load_ids("fabricante", "id_fabricante", "nome")
            id_fabricante_dict = {f[1]: f[0] for f in fabricantes}
            nome_fabricante = st.selectbox("Nome do Fabricante", list(id_fabricante_dict.keys()))
            id_fabricante = id_fabricante_dict.get(nome_fabricante)

            categorias = load_ids("categoria", "id_categoria", "nome")
            id_categoria_dict = {c[1]: c[0] for c in categorias}
            nome_categoria = st.selectbox("Nome da Categoria", list(id_categoria_dict.keys()))
            id_categoria_produto = id_categoria_dict.get(nome_categoria)
            
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



            if st.form_submit_button("Registrar Produto"):
                if not titulo_produto or not serial_number_produto:
                    st.error("Título do produto e número de série são obrigatórios.")
                elif product_exists(titulo_produto, serial_number_produto):
                    st.error("Produto com este título e número de série já existe.")
                elif id_fabricante is None or id_categoria_produto is None or id_editora_produto is None:
                    st.error("Um ou mais IDs selecionados são inválidos.")
                else:
                    sku = generate_sku(id_categoria_produto)  # Gera um novo SKU para o produto
                    barcode_buffer = generate_barcode(sku)  # Gera o código de barras
                    barcode_path = os.path.join('bar_codes', f'{sku}.png')
                    
                    # Certificar-se de que o diretório existe
                    if not os.path.exists('bar_codes'):
                        os.makedirs('bar_codes')
                    
                    try:
                        # Salvar a imagem do código de barras
                        with open(barcode_path, 'wb') as f:
                            f.write(barcode_buffer.getvalue())

                        # Preparar a consulta SQL
                        sql = """
                            INSERT INTO produtos (
                                id_produto, titulo, id_categoria, id_fabricante, id_editora, condicao, completo, manual_instrucoes, 
                                serial_number, serial_caixa, idiomas_disponiveis, imagem, descricao, conteudo_edicao, 
                                acessorios_incluidos, raridade, estoque, data_recebimento, preco_custo, preco_venda, id_embalagem, 
                                codigo_barras, codigo_universal, anunciado, ITEM_ID
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """
                        values = (
                            sku, titulo_produto, id_categoria_produto, id_fabricante, id_editora_produto,
                            condicao_produto, int(completo_produto), int(manual_instrucoes_produto),
                            serial_number_produto, serial_caixa_produto, idiomas_disponiveis_produto, imagem_produto,
                            descricao_produto, conteudo_edicao_produto, acessorios_incluidos_produto, raridade_produto,
                            estoque_produto, data_recebimento_produto, preco_custo_produto, preco_venda_produto,
                            id_embalagem_produto, barcode_path, codigo_universal_produto, int(anunciado_produto), id_anuncio
                        )

                        # Conectar ao banco de dados e executar a inserção
                        mydb = None
                        mycursor = None
                        try:
                            mydb, mycursor = conectar_banco_dados()
                            mycursor.execute(sql, values)
                            mydb.commit()
                            detalhes = f"Produto '{titulo_produto}' com SKU {sku} registrado com sucesso."
                            registrar_historico("Registro", "produtos", detalhes)
                            st.success("Produto registrado com sucesso!")

                            # Recuperar e exibir detalhes do produto registrado
                            produto = get_product_details(titulo_produto, serial_number_produto)
                            if produto:
                                st.write("Detalhes do Produto Registrado:")
                                st.json({
                                    "ID do Produto": produto[0],            # id_produto
                                    "Título": produto[1],                   # titulo
                                    "ID da Categoria": produto[2],          # id_categoria
                                    "ID do Fabricante": produto[3],         # id_fabricante
                                    "ID da Editora": produto[4],            # id_editora
                                    "Condição": produto[5],                 # condicao
                                    "Completo": produto[6],                 # completo
                                    "Manual de Instruções": produto[7],     # manual_instrucoes
                                    "Número de Série": produto[8],          # serial_number
                                    "Número de Série da Caixa": produto[9], # serial_caixa
                                    "Idiomas Disponíveis": produto[10],     # idiomas_disponiveis
                                    "Imagem": produto[11],                 # imagem
                                    "Descrição": produto[12],              # descricao
                                    "Conteúdo da Edição": produto[13],      # conteudo_edicao
                                    "Acessórios Incluídos": produto[14],    # acessorios_incluidos
                                    "Raridade": produto[15],                # raridade
                                    "Estoque": produto[16],                # estoque
                                    "Data de Recebimento": produto[17],     # data_recebimento
                                    "Preço de Custo": produto[18],          # preco_custo
                                    "Preço de Venda": produto[19],          # preco_venda
                                    "ID da Embalagem": produto[20],         # id_embalagem
                                    "Código de Barras": produto[21],        # codigo_barras
                                    "Código Universal": produto[22],       # codigo_universal
                                    "Anunciado": produto[23]   ,
                                    "id_anuncio": produto[24]            # anunciado
                                })
                        except Exception as e:
                            st.error(f"Erro ao conectar ao banco de dados ou ao registrar o produto: {e}")
                            st.error("Ocorreu um erro ao tentar registrar o produto.")
                        finally:
                            # Garantir que o banco de dados seja fechado corretamente
                            if mydb is not None:
                                mydb.close()
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
                        except Error as e:
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
            except Error as e:
                st.error(f"Erro ao buscar categorias: {e}")
            finally:
                fechar_conexao(mydb, mycursor)

    with tab3:
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

    with tab4:
        with st.form("manufacturer_form"):
            nome_fabricante = st.text_input("Nome do Fabricante")

            if st.form_submit_button("Registrar Fabricante"):
                if not nome_fabricante:
                    st.error("Nome do fabricante é obrigatório.")
                else:
                    mydb, mycursor = conectar_banco_dados()
                    if mydb and mycursor:
                        try:
                            # Verificar se o fabricante já existe
                            mycursor.execute("SELECT COUNT(*) FROM fabricante WHERE nome = %s", (nome_fabricante,))
                            existe_fabricante = mycursor.fetchone()[0]

                            if existe_fabricante > 0:
                                st.error("Fabricante com esse nome já existe.")
                            else:
                                # Obter o maior ID existente
                                mycursor.execute("SELECT id_fabricante FROM fabricante WHERE id_fabricante REGEXP '^F[0-9]{3}$' ORDER BY id_fabricante DESC LIMIT 1")
                                max_id_result = mycursor.fetchone()

                                if max_id_result:
                                    max_id = max_id_result[0]
                                    max_numero = int(max_id[1:])  # Remove o prefixo 'F' e converte para inteiro
                                    next_id = f"F{str(max_numero + 1).zfill(3)}"
                                else:
                                    next_id = 'F001'  # Se não houver ID válido, começa do 'F001'

                                # Inserir novo fabricante com o ID gerado
                                sql = "INSERT INTO fabricante (id_fabricante, nome) VALUES (%s, %s)"
                                mycursor.execute(sql, (next_id, nome_fabricante))
                                mydb.commit()

                                # Registrar no histórico
                                detalhes = f"Fabricante '{nome_fabricante}' com ID {next_id} registrado com sucesso."
                                registrar_historico("Registro", "fabricantes", detalhes)

                                st.success("Fabricante Registrado com Sucesso!!!")
                        except Error as e:
                            st.error(f"Erro ao operar no banco de dados: {e}")
                        finally:
                            fechar_conexao(mydb, mycursor)
        
        st.text("Fabricantes Cadastrados")
        mydb, mycursor = conectar_banco_dados()
        if mydb and mycursor:
            try:
                mycursor.execute("SELECT * FROM fabricante")
                fabricantes = mycursor.fetchall()
                if fabricantes:
                    for fabricante in fabricantes:
                        st.write(f"**ID:** {fabricante[0]} - {fabricante[1]}")
                else:
                    st.write("Nenhum fabricante cadastrado.")
            except Error as e:
                st.error(f"Erro ao buscar fabricantes: {e}")
            finally:
                fechar_conexao(mydb, mycursor)