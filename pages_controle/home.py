import streamlit as st

st.title("Sistema de Gestão de Produtos")
st.divider()
# Adicionar a imagem centralizada no início da página
st.markdown("""
<div style="text-align: center;">
    <img src="https://i.imgur.com/Ti4ILVw.png" style="width: 40%;"/>
</div>
            

""", unsafe_allow_html=True)

st.divider()
# Introdução
st.markdown("""

- **Consultar Produtos**: Busque e visualize informações detalhadas sobre os produtos no estoque.
- **Tabela de Produtos**: Visualize a lista completa dos produtos cadastrados.
- **Registrar e Atualizar Produtos**: Adicione novos produtos e atualize as informações existentes.
- **Gerenciar Inventário**: Monitore e atualize o inventário de itens conforme necessário.



Utilize o menu lateral para acessar as diferentes páginas do sistema:    
Cada página possui prórprias funções na sidebar:
            
""")

st.markdown("""
<div style="text-align: left;">
    <img src="https://i.imgur.com/g3iRAKb.png" style="width: 60%;"/>
</div>
            


           
""", unsafe_allow_html=True)

# # Links de navegação
# st.page_link("pages_produtos/search_product.py", label="Buscar Produtos Cadastrados", icon="🔍")
# st.page_link("pages_produtos/table_products.py", label="Acessar Tabela de Produtos", icon="🔍")
# st.page_link("pages_produtos/new_product.py", label="Cadastro e Atualização de Produtos", icon="🎮")
# st.page_link("pages_controle/historico.py", label="Gerenciar Inventário", icon="📦")

# Rodapé
st.markdown("""
---


""")
