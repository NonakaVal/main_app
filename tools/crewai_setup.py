import os
import sys
import time
import re
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool, WebsiteSearchTool
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.crewai_browser_tools import BrowserTools
from tools.crewai_search_tools import SearchTools


# def create_crewai_setup(product_code, llm):
#     """
#     Configura a equipe para análise de produto.
#     """
#     max_iter = 70
#     duckduckgo_search = DuckDuckGoSearchRun()

#     # Definição dos Agentes
#     product_info_collector = Agent(
#         role='Coletor de Informações do Produto',
#         goal=f'Coletar todas as informações relevantes sobre o produto usando o código universal {product_code}.',
#         backstory='Especialista em coleta de dados, este agente é capaz de buscar informações detalhadas sobre produtos a partir de códigos universais.',
#         llm=llm,
#         max_iter=max_iter,
#         allow_delegation=True,
#         tools=[duckduckgo_search],
#         verbose=False
#     )
    
#     product_specification_researcher = Agent(
#         role='Pesquisador de Especificações do Produto',
#         goal=f'Pesquisar todas as especificações técnicas, variações e edições do produto com o código {product_code}.',
#         backstory='Com vasta experiência na criação de relatórios descritivos, este agente pesquisa e compila especificações detalhadas dos produtos.',
#         llm=llm,
#         max_iter=max_iter,
#         allow_delegation=False,
#         tools=[duckduckgo_search],
#         verbose=False
#     )

#     product_data_analyzer = Agent(
#         role='Analista de Dados do Produto',
#         goal='Analisar as informações coletadas e estruturar para um relatório, incluindo valores médios de venda e preços baseados em condições e edições do produto.',
#         backstory='Experiente em análise de dados, este agente interpreta as informações do produto e organiza em um formato claro e estruturado.',
#         llm=llm,
#         max_iter=max_iter,
#         allow_delegation=False,
#         tools=[duckduckgo_search],
#         verbose=False
#     )

#     technology_expert_writer = Agent(
#         role="Escritor Sênior de Relatórios Estruturados",
#         goal=f"Compilar todas as informações detalhadas sobre o produto com o código {product_code}, incluindo título, categoria, fabricante, editora, idiomas disponíveis, imagem, descrição, conteúdo da edição, acessórios incluídos, e valores médios de venda.",
#         backstory="""O agente é um escritor experiente especializado na elaboração de relatórios detalhados e estruturados. 
#         Com uma habilidade refinada para compilar e organizar informações complexas de forma clara e concisa, ele é capaz de gerar relatórios abrangentes que atendem às necessidades de negócios, regulamentações e planejamento estratégico. 
#         Seus relatórios são conhecidos por sua precisão, profundidade analítica e capacidade de fornecer informações valiosas para a tomada de decisões informadas.""",
#         llm=llm,
#         max_iter=max_iter,
#         allow_delegation=False,
#         verbose=False
#     )

#     # Definição das Tarefas
#     product_info_collection_task = Task(
#         description=f"""
#         Coletar todas as informações relevantes sobre o produto com o código universal {product_code}. As informações devem incluir:
#         1. **Título**: Nome completo e descrição detalhada do produto.
#         2. **Categoria**: Tipo específico de produto (ex: videogame, console, acessório).
#         3. **Fabricante**: Nome da empresa que fabricou o produto.
#         4. **Editora**: Nome da empresa responsável pela publicação do produto, se aplicável.
#         5. **Idiomas Disponíveis**: Idiomas em que o produto está disponível (ex: global, pt-br, en-US, Jp).
#         6. **Imagem**: Link ou descrição da imagem do produto.
#         7. **Descrição**: Descrição completa e detalhada do produto.
#         """,
#         expected_output=f"Informações básicas detalhadas coletadas sobre o produto com código {product_code}.",
#         agent=product_info_collector
#     )

#     product_specification_task = Task(
#         description=f"""
#         Coletar e listar todas as especificações técnicas e detalhes adicionais do produto, incluindo:
#         - **Conteúdo da Edição**: Detalhes sobre o que está incluído em cada edição do produto (ex: itens exclusivos, manual).
#         - **Acessórios Incluídos**: Lista de todos os acessórios que acompanham o produto (ex: cabos, estojos).
#         - **Valores de Venda**: Preços médios, mínimos e máximos de venda do produto em diferentes condições e edições.
#         """,
#         expected_output=f"Especificações técnicas e variações do produto coletadas e documentadas.",
#         agent=product_specification_researcher
#     )

#     product_report_task = Task(
#         description=f"""
#         Analisar todas as informações coletadas e criar um relatório detalhado e estruturado que inclua:
#         1. **Título**: Nome completo e descrição do produto.
#         2. **Categoria**: Tipo específico de produto.
#         3. **Fabricante e Editora**: Nome e IDs das empresas associadas ao produto.
#         4. **Idiomas Disponíveis**: Idiomas em que o produto está disponível.
#         5. **Descrição**: Descrição do produto.
#         6. **Conteúdo da Edição**: Lista de itens incluídos na edição.
#         7. **Acessórios Incluídos**: Lista de acessórios fornecidos com o produto.
#         8. **Valores de Venda**: Preços médios e variações em diferentes condições e edições.
#         """,
#         expected_output=f"Relatório completo e estruturado sobre o produto com código {product_code}.",
#         agent=technology_expert_writer,
#         context=[product_info_collection_task, product_specification_task]
#     )

#     # Configuração da Equipe (Crew)
#     crew = Crew(
#         agents=[product_info_collector, product_specification_researcher, product_data_analyzer, technology_expert_writer],
#         tasks=[product_info_collection_task, product_specification_task, product_report_task],
#         process=Process.sequential,  # Processo sequencial para execução das tarefas
#         manager_llm=llm,  # Modelo LLM para gerenciar a equipe
#         verbose=False
#     )

#     return crew
def create_crewai_setup(product_code, llm):
    """
    Configura a equipe para análise de produto.
    """
    max_iter = 70

    duckduckgo_search = [DuckDuckGoSearchRun()]
    Search_tools = [SearchTools.search_internet, BrowserTools.scrape_and_summarize_website, ScrapeWebsiteTool(), WebsiteSearchTool()]
    
    # Definição dos Agentes
    product_info_collector = Agent(
        role='Coletor de Informações do Produto',
        goal=f'Coletar todas as informações relevantes sobre o produto usando o código universal {product_code}.',
        backstory='Especialista em coleta de dados, este agente é capaz de buscar informações detalhadas sobre produtos a partir de códigos universais.',
        llm=llm,
        max_iter=max_iter,
        allow_delegation=True,
        tools=duckduckgo_search,
        verbose=False
    )
    
    product_specification_researcher = Agent(
        role='Pesquisador de Especificações do Produto',
        goal=f'Pesquisar todas as especificações técnicas, variações e edições do produto com o código {product_code}.',
        backstory='Com vasta experiência na criação de relatórios descritivos, este agente pesquisa e compila especificações detalhadas dos produtos.',
        llm=llm,
        max_iter=max_iter,
        allow_delegation=False,
        tools=duckduckgo_search,
        verbose=False
    )

    product_data_analyzer = Agent(
        role='Analista de Dados do Produto',
        goal='Analisar as informações coletadas e estruturar para um relatório, incluindo valores médios de venda e preços baseados em condições e edições do produto.',
        backstory='Experiente em análise de dados, este agente interpreta as informações do produto e organiza em um formato claro e estruturado.',
        llm=llm,
        max_iter=max_iter,
        allow_delegation=False,
        tools=duckduckgo_search,
        verbose=False
    )

    product_description_writer = Agent(
        role='Escritor de Descrição do Produto',
        goal='Desenvolver uma descrição detalhada do produto com base nas informações coletadas e analisadas. A descrição deve ser clara, informativa e atraente para potenciais clientes.',
        backstory="""Especialista em criação de conteúdo, este agente transforma dados e informações brutas em descrições envolventes e 
        informativas para produtos, usando uma abordagem orientada ao cliente.""",
        llm=llm,
        max_iter=max_iter,
        allow_delegation=False,
        tools=Search_tools,
        verbose=False
    )

    technology_expert_writer = Agent(
        role="Escritor Senior de Relatórios Estruturados",
        goal=f"Compilar todas as informações detalhadas sobre o {product_code}, incluindo título, categoria, fabricante, editora, idiomas disponíveis, imagem, descrição, conteúdo da edição, acessórios incluídos, e valores médios de venda.",
        backstory="""O agente é um escritor experiente especializado na elaboração de relatórios detalhados e estruturados. 
        Com uma habilidade refinada para compilar e organizar informações complexas de forma clara e concisa, ele é capaz de gerar relatórios abrangentes que atendem às necessidades de negócios, regulamentações e planejamento estratégico. 
        Seus relatórios são conhecidos por sua precisão, profundidade analítica e capacidade de fornecer informações valiosas para a tomada de decisões informadas.""",
        llm=llm,
        max_iter=max_iter,
        allow_delegation=False,
        verbose=False
    )

    # Definição das Tarefas
    product_info_collection_task = Task(
        description=f"""
        Coletar todas as informações relevantes sobre o produto com o código universal {product_code}. As informações devem incluir:
        1. **Título**: Nome completo e descrição detalhada.
        2. **Categoria**: Tipo de produto.
        3. **Fabricante e Editora**: Empresas responsáveis pela fabricação e publicação.
        4. **Idiomas Disponíveis**: Idiomas em que o produto está disponível (ex: global, pt-br, en-US, Jp).
        """,
        expected_output=f"Informações básicas coletadas sobre o produto com código {product_code}.",
        agent=product_info_collector
    )

    product_specification_task = Task(
        description=f"""
        Coletar e listar todas as especificações do produto, incluindo:
        - Conteúdo da Edição: Detalhes de tudo que compõe a edição do produto.
        - Acessórios Incluídos: Lista de acessórios que acompanham o produto.
        - Valores de Venda: Mínimo, máximo e médio de vendas do produto.
        """,
        expected_output=f"Especificações detalhadas e variações do produto coletadas.",
        agent=product_specification_researcher
    )

    product_data_analysis_task = Task(
        description=f"""
        Analisar as informações coletadas sobre o produto e identificar padrões, valores médios de venda, e preços baseados nas condições e edições do produto. Preparar os dados para a criação do relatório.
        """,
        expected_output=f"Análise de dados concluída e pronta para a elaboração do relatório.",
        agent=product_data_analyzer,
        context=[product_info_collection_task, product_specification_task]
    )

    product_description_task = Task(
        description=f"""
        Elaborar uma descrição detalhada e envolvente do produto com base nas informações coletadas e analisadas. A descrição deve destacar características importantes e atrativos para o público-alvo, utilizando uma linguagem clara e persuasiva.
        """,
        expected_output=f"Descrição do produto escrita e refinada.",
        agent=product_description_writer,
        context=[product_info_collection_task, product_specification_task, product_data_analysis_task]
    )

    product_report_task = Task(
        description=f"""
        Analisar as informações coletadas e criar um relatório detalhado que inclui:
        1. **Título**: Nome completo e descrição.
        2. **Categoria**: Tipo de produto.
        3. **Fabricante e Editora**: IDs de fabricante e editora associados ao produto.
        4. **Idiomas Disponíveis**: Idiomas em que o produto está disponível.
        5. **Descrição**: Descrição do produto.
        6. **Conteúdo da Edição**: Lista do que está incluído em cada edição.
        7. **Acessórios Incluídos**: lista de acessórios fornecidos com o produto.
        """,
        expected_output=f"Relatório estruturado sobre o produto com código {product_code}.",
        agent=technology_expert_writer,
        context=[product_info_collection_task, product_specification_task, product_description_task]
    )

    # Configuração da Equipe (Crew)
    crew = Crew(
        agents=[product_info_collector, product_specification_researcher, product_data_analyzer, product_description_writer, technology_expert_writer],
        tasks=[product_info_collection_task, product_specification_task, product_data_analysis_task, product_description_task, product_report_task],
        process=Process.sequential,  # Processo sequencial para execução das tarefas
        manager_llm=llm,  # Modelo LLM para gerenciar a equipe
        verbose=False,
        # memory=True
    )

    return crew



def run_crewai_app(crew, expander_type):
    """
    Função para executar o aplicativo Streamlit para análise de mercado e estratégia de negócios de um produto.
    """

    # Botão para iniciar a análise
    if st.button("Executar Pesquisa"):
        # Placeholder para o cronômetro
        stopwatch_placeholder = st.empty()
        
        # Início do cronômetro
        start_time = time.time()
        
        with st.expander("Processando..."):
            sys.stdout = expander_type  # Redireciona a saída padrão para o expander
            with st.spinner("Gerando Resultados..."):
                crew_result = crew.kickoff()  # Executa o processo da equipe
            
        # Fim do cronômetro
        end_time = time.time()
        total_time = end_time - start_time
        stopwatch_placeholder.text(f"Tempo total decorrido: {total_time:.2f} segundos")

        # Exibição dos resultados
        st.markdown("### Resultados:")
        st.markdown(crew_result)

class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']  # Define a list of colors
        self.color_index = 0  # Initialize color index
        self.ignoring = False  # Flag to indicate if we are in ignore mode

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        if self.ignoring:
            if "Finished chain." in cleaned_data:
                self.ignoring = False
                # Append the remaining cleaned data after ignoring
                self.buffer.append(cleaned_data.split("Finished chain.", 1)[1])
            return

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(self.colors)  # Increment color index and wrap around if necessary

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")
            self.ignoring = True

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []


class StreamToExpander_detailed:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']  # Define a list of colors
        self.color_index = 0  # Initialize color index
        self.ignoring = False  # Flag to indicate if we are in ignore mode

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        if self.ignoring:
            if "Finished chain." in cleaned_data:
                self.ignoring = False
                # Append the remaining cleaned data after ignoring
                self.buffer.append(cleaned_data.split("Finished chain.", 1)[1])
            return

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(self.colors)  # Increment color index and wrap around if necessary

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")
            self.ignoring = True

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []
    def main():
        # Configuração do tipo de expander
        expander_type_choice = st.sidebar.radio(
            "Escolha o tipo de saída",
            ["StreamToExpander", "StreamToExpander_detailed"]
        )

        # Configuração do expander com base na escolha do usuário
        if expander_type_choice == "StreamToExpander":
            expdr_config = StreamToExpander(st)
        else:
            expdr_config = StreamToExpander_detailed(st)
        
        # Obter a chave da API do OpenAI
        openai_api_key = st.secrets["OPENAI_API_KEY"]

        if openai_api_key:
            try:
                # Criar uma instância do modelo ChatOpenAI
                llm = ChatOpenAI(
                    model='gpt-3.5-turbo',
                    api_key=openai_api_key
                )
                st.success("A chave da API do OpenAI está configurada e o LLM está pronto para usar!")    
                
                # Input para o código do produto
                product_code = st.text_input("Digite o código do produto para busca.")
                
                # Configuração da equipe (Crew) e execução
                if product_code:
                    crew = create_crewai_setup(product_code, llm)
                    run_crewai_app(crew, expdr_config)
            except Exception as e:
                st.error(f"Ocorreu um erro ao configurar o LLM: {e}")
        else:
            st.warning("Por favor, insira uma chave de API do OpenAI válida para continuar.")


def crew_Search():
    
    # Configuração do tipo de expander
    expdr_config = StreamToExpander(st)

    # # Configuração do expander com base na escolha do usuário
    # if expander_type_choice == "StreamToExpander":
    #     expdr_config = StreamToExpander(st)
    # else:
    #     expdr_config = StreamToExpander_detailed(st)
    
    # Obter a chave da API do OpenAI
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    

    if openai_api_key:
        try:
            # Criar uma instância do modelo ChatOpenAI
            llm = ChatOpenAI(
                model='gpt-3.5-turbo',
                api_key=openai_api_key
            )
            st.success("A chave da API do OpenAI está configurada e o LLM está pronto para usar!")    
            
            # Input para o código do produto
            product_code = st.text_input("Digite o código original do produto para pesquisar")
            
            # Configuração da equipe (Crew) e execução
            if product_code:
                crew = create_crewai_setup(product_code, llm)
                run_crewai_app(crew, expdr_config)
        except Exception as e:
            st.error(f"Ocorreu um erro ao configurar o LLM: {e}")
    else:
        st.warning("Por favor, insira uma chave de API do OpenAI válida para continuar.")