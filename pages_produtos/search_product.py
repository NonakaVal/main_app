import streamlit as st
from tools.load_from_db import load_ids
from tools.app_config import conectar_banco_dados

# Conectar ao banco de dados
mydb, mycursor = conectar_banco_dados()
if mydb and mycursor:
    # Realize suas operações com mydb e mycursor aqui
    pass
# Carregar IDs e nomes das categorias




with st.form("query_form"):
    nome_produto = st.text_input("Buscar por Nome do Produto")
    submitted = st.form_submit_button("Buscar")

with st.sidebar:
    descricao_produto = st.text_area("Buscar por Descrição")
    produto_anunciado = st.radio("Buscar está Anunciado", ['Todos', 'Sim', 'Não'])
    completo_produto = st.radio("Buscar por Completo", ['Todos', 'Sim', 'Não'])
    condicao_produto = st.selectbox("Buscar por Condição", ['Todos', 'Novo', 'ComoNovo', 'MuitoBom', 'Bom', 'Aceitável', 'Ruim'])

    # Carrega e exibe IDs de Fabricante e Categoria
    id_fabricante_produto = st.selectbox("Buscar por ID do Fabricante", ['Todos'] + [f"{f[0]} - {f[1]}" for f in load_ids("fabricante", "id_fabricante", "nome")])
    id_fabricante_produto = (id_fabricante_produto.split(' ')[0]) if id_fabricante_produto != 'Todos' else None

    id_categoria_produto = st.selectbox("Buscar por ID da Categoria", ['Todos'] + [f"{c[0]} - {c[1]}" for c in load_ids("categoria", "id_categoria", "nome")])
    id_categoria_produto = (id_categoria_produto.split(' ')[0]) if id_categoria_produto != 'Todos' else None

    min_valor = st.number_input("Valor Mínimo", min_value=0.0, format="%.2f")
    max_valor = st.number_input("Valor Máximo", min_value=0.0, format="%.2f")
    id_produto = st.text_input("Buscar por ID do Produto")


if submitted:
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []

    if id_produto:
        query += " AND id_produto = %s"
        params.append(id_produto)
    if nome_produto:
        query += " AND titulo LIKE %s"
        params.append(f"%{nome_produto}%")
    if descricao_produto:
        query += " AND descricao LIKE %s"
        params.append(f"%{descricao_produto}%")
    if condicao_produto != 'Todos':
        query += " AND condicao = %s"
        params.append(condicao_produto)
    if completo_produto != 'Todos':
        query += " AND completo = %s"
        params.append(1 if completo_produto == 'Sim' else 0)
    
    if id_fabricante_produto is not None:
        query += " AND id_fabricante = %s"
        params.append(id_fabricante_produto)
    if id_categoria_produto is not None:
        query += " AND id_categoria = %s"
        params.append(id_categoria_produto)
    if min_valor > 0:
        query += " AND preco_venda >= %s"
        params.append(min_valor)
    if max_valor > 0:
        query += " AND preco_venda <= %s"
        params.append(max_valor)
    if produto_anunciado != 'Todos':
        query += " AND anunciado = %s"
        params.append(1 if produto_anunciado == 'Sim' else 0)

    mycursor.execute(query, tuple(params))
    result = mycursor.fetchall()
    
    if result:
        for row in result:
            with st.expander(f"{row[1]} - {row[0]}"):
                st.write(f"**Nome:** {row[1]}")
                st.write(f"**Descrição:** {row[12]}")
                st.write(f"**Condição:** {row[5]}")
                st.write(f"**Completo:** {'Sim' if row[6] else 'Não'}")
                st.write(f"**Número de Série:** {row[8]}")
                st.write(f"**Número de Série da Caixa:** {row[9]}")
                st.write(f"**Quantidade em Estoque:** {row[16]}")
                st.write(f"**Idioma:** {row[10]}")

                # Exibe a imagem do produto
                try:
                    if row[11]:
                        st.image(row[11], width=500, caption=f"Imagem do Produto {row[1]}")
                    else:
                        st.write("Imagem não disponível.")
                except Exception as e:
                    st.write("Erro ao carregar a imagem. Verifique o link da imagem.")

                st.write(f"**Raridade:** {row[15]}")
                st.write(f"**Conteúdo da Edição:** {row[13]}")
                st.write(f"**Acessórios Incluídos:** {row[14]}")
                st.write(f"**Valor:** {row[19]:.2f}")
                st.write(f"**Data de Recebimento:** {row[17]}")

                
                categorias = load_ids("categoria", "id_categoria", "nome")
                id_categoria_dict = {c[0]: c[1] for c in categorias} 
                id_categoria = row[2]
                nome_categoria = id_categoria_dict.get(id_categoria, "Nome da Categoria não encontrado")
                st.write(f"**ID da Categoria:** {id_categoria} - {nome_categoria}")
                
                    # Carregar IDs e nomes
                # Carregar IDs e nomes
                fabricantes = load_ids("fabricante", "id_fabricante", "nome")
                id_fabricante_dict = {f[0]: f[1] for f in fabricantes}  # Mapeia ID para nome
                # Busca o nome do fabricante usando o ID
                id_fabricante = row[3]
                nome_fabricante = id_fabricante_dict.get(id_fabricante, "Nome do Fabricante não encontrado")
                st.write(f"**ID do Fabricante:** {id_fabricante} - {nome_fabricante}")


                editoras = load_ids("editora", "id_editora", "nome")
                id_editora_dict = {e[0]: e[1] for e in editoras}  # Mapeia ID para nome
                id_editora = row[4]
                nome_editora = id_editora_dict.get(id_editora, "Nome da Editora não encontrado")
                st.write(f"**ID da Editora:** {id_editora} - {nome_editora}")




                st.write(f"**ID da Embalagem:** {row[20]}")
                st.write(f"**codigo universal** {row[22]}")
                st.write(f"**Esta anunciado** {row[23]}")
    
                # Exibe a imagem do código de barras
                try:
                    if row[21]:
                        st.image(row[21], width=200, caption=f"Código de Barras - Produto {row[1]}")
                    else:
                        st.write("Código de barras não disponível.")
                except Exception as e:
                    st.write("Erro ao carregar o código de barras. Verifique o link.")

                st.write("---")
    else:
        st.write("Nenhum produto encontrado com os critérios selecionados.")