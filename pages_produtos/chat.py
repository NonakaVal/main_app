from langchain.agents import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
import streamlit as st
import pandas as pd
import os

openai_key = st.secrets["OPENAI_API_KEY"]

file_formats = {
    "csv": pd.read_csv,
    "xls": pd.read_excel,
    "xlsx": pd.read_excel,
    "xlsm": pd.read_excel,
    "xlsb": pd.read_excel,
}


def clear_submit():
    """
    Limpar o estado do botão de envio
    Retornos:

    """
    st.session_state["submit"] = False


@st.cache_data(ttl="2h")
def load_data(uploaded_file):
    try:
        ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    except:
        ext = uploaded_file.split(".")[-1]
    if ext in file_formats:
        return file_formats[ext](uploaded_file)
    else:
        st.error(f"Formato de arquivo não suportado: {ext}")
        return None


st.set_page_config(page_title="LangChain: Converse com pandas DataFrame", page_icon="🦜")
st.title("🦜 LangChain: Converse com pandas DataFrame")

uploaded_file = st.file_uploader(
    "Carregue um arquivo de dados",
    type=list(file_formats.keys()),
    help="Vários formatos de arquivo são suportados",
    on_change=clear_submit,
)

if not uploaded_file:
    st.warning(
        "Este aplicativo usa o `PythonAstREPLTool` do LangChain, que é vulnerável à execução arbitrária de código. Use com cautela ao implantar e compartilhar este aplicativo."
    )

if uploaded_file:
    df = load_data(uploaded_file)

openai_api_key = openai_key
if "messages" not in st.session_state or st.sidebar.button("Limpar histórico de conversas"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Como posso ajudar você?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Sobre o que é este dado?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Por favor, adicione sua chave de API OpenAI para continuar.")
        st.stop()

    llm = ChatOpenAI(
        temperature=0, model="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True
    )

    pandas_df_agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        handle_parsing_errors=True,
        allow_dangerous_code=True  # Adicione esta linha
    )

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = pandas_df_agent.run(st.session_state.messages, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
