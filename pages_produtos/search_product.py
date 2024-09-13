##################################################################################################################
##################################################################################################################
## Pagina pesquisa de produtos
##################################################################################################################
##################################################################################################################

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
    id_produto = st.text_input("Buscar por ID do Produto")
    descricao_produto = st.text_area("Buscar por Descrição")
    produto_anunciado = st.radio("Buscar está Anunciado", ['Todos', 'Sim', 'Não'])
    completo_produto = st.radio("Buscar por Completo", ['Todos', 'Sim', 'Não'])
    
    id_condicao_produto = st.selectbox("Buscar por ID da Condição", ['Todos'] + [f"{f[0]} - {f[1]}" for f in load_ids("condicao", "id_condicao", "nome")])
    id_condicao_produto = (id_condicao_produto.split(' ')[0]) if id_condicao_produto != 'Todos' else None
    
    id_fabricante_produto = st.selectbox("Buscar por ID do Fabricante", ['Todos'] + [f"{f[0]} - {f[1]}" for f in load_ids("marca", "id_marca", "nome")])
    id_fabricante_produto = (id_fabricante_produto.split(' ')[0]) if id_fabricante_produto != 'Todos' else None

    id_categoria_produto = st.selectbox("Buscar por ID da Categoria", ['Todos'] + [f"{c[0]} - {c[1]}" for c in load_ids("categoria", "id_categoria", "nome")])
    id_categoria_produto = (id_categoria_produto.split(' ')[0]) if id_categoria_produto != 'Todos' else None

    min_valor = st.number_input("Valor Mínimo", min_value=0.0, format="%.2f")
    max_valor = st.number_input("Valor Máximo", min_value=0.0, format="%.2f")

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
    if id_condicao_produto is not None:
        query += " AND condicao = %s"
        params.append(id_condicao_produto)
    if completo_produto != 'Todos':
        query += " AND completo = %s"
        params.append(1 if completo_produto == 'Sim' else 0)
    
    if id_fabricante_produto is not None:
        query += " AND id_marca = %s"
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
                st.write(f"**ID do Produto:** {row[0]}")
                st.write(f"**Título:** {row[1]}")
                st.write(f"**ID da Categoria:** {row[2]}")
                st.write(f"**ID da Edição:** {row[3]}")
                st.write(f"**ID do Fabricante:** {row[4]}")
                st.write(f"**ID da Editora:** {row[5]}")
                st.write(f"**Condição:** {row[6]}")
                st.write(f"**Completo:** {'Sim' if row[7] else 'Não'}")
                st.write(f"**Manual de Instruções:** {'Sim' if row[8] else 'Não'}")
                st.write(f"**Número de Série:** {row[9]}")
                st.write(f"**Número de Série da Caixa:** {row[10]}")
                st.write(f"**Idiomas Disponíveis:** {row[11]}")
                
                # Exibe a imagem do produto
                try:
                    if row[12]:
                        st.image(row[12], width=500, caption=f"Imagem do Produto {row[1]}")
                    else:
                        st.write("Imagem não disponível.")
                except Exception as e:
                    st.write("Erro ao carregar a imagem. Verifique o link da imagem.")

                st.write(f"**Descrição:** {row[13]}")
                st.write(f"**Conteúdo da Edição:** {row[14]}")
                st.write(f"**Acessórios Incluídos:** {row[15]}")
                st.write(f"**Raridade:** {row[16]}")
                st.write(f"**Estoque:** {row[17]}")
                st.write(f"**Data de Recebimento:** {row[18]}")
                st.write(f"**Preço de Custo:** {row[19]}")
                st.write(f"**Preço de Venda:** {row[20]}")
                st.write(f"**ID da Embalagem:** {row[21]}")
                st.write(f"**Código Universal:** {row[23]}")
                st.write(f"**Anunciado:** {'Sim' if row[24] else 'Não'}")
                st.write(f"**ID do Anúncio:** {row[25]}")

                # Exibe a imagem do código de barras
                try:
                    if row[22]:
                        st.image(row[22], width=200, caption=f"Código de Barras - Produto {row[1]}")
                    else:
                        st.write("Código de barras não disponível.")
                except Exception as e:
                    st.write("Erro ao carregar o código de barras. Verifique o link.")

                try:
                    if row[26]:
                        st.image(row[26], width=200, caption=f"Código de Barras - Produto {row[1]}")
                    else:
                        st.write("Código de barras não disponível.")
                except Exception as e:
                    st.write("Erro ao carregar o código de barras. Verifique o link.")

                st.write("---")
    else:
        st.write("Nenhum produto encontrado com os critérios selecionados.")
