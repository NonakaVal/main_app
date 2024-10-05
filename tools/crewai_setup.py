from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool, WebsiteSearchTool
from tools.crewai_search_tools import SearchTools
from tools.crewai_browser_tools import BrowserTools

def create_price_comparison_team(product_name, llm):

    max_iter = 70

    # Definir Agentes
    price_scraper = Agent(
        role="Especialista em Busca de Preços",
        goal=f"""Realizar buscas em sites de e-commerce e marketplaces para coletar preços de {product_name}.""",
        backstory=f"""Especialista em coleta de dados online, focado em encontrar o maior número de preços disponíveis em diversas plataformas.""",
        verbose=True,
        allow_delegation=True,
        tools=[SearchTools.search_internet, BrowserTools.scrape_and_summarize_website, ScrapeWebsiteTool(), WebsiteSearchTool()],
        llm=llm,
        max_iter=max_iter
    )

    specification_analyzer = Agent(
        role="Especialista em Análise de Especificações",
        goal=f"""Analisar as especificações técnicas e variações de {product_name} nos diferentes sites para garantir a compatibilidade e consistência das ofertas.""",
        backstory=f"""Especialista em análise de especificações de produtos, com foco em verificar as diferenças e similaridades entre ofertas.""",
        verbose=True,
        allow_delegation=True,
        tools=[SearchTools.search_internet, BrowserTools.scrape_and_summarize_website, ScrapeWebsiteTool(), WebsiteSearchTool()],
        llm=llm,
        max_iter=max_iter
    )

    price_analyzer = Agent(
        role="Analista de Preços",
        goal=f"""Comparar os preços coletados para determinar o menor, o maior e a média de preços para {product_name}, incluindo uma análise das variações e descontos.""",
        backstory=f"""Especialista em análise de preços, com experiência em identificar variações de preços, descontos e padrões de flutuação.""",
        verbose=True,
        allow_delegation=True,
        tools=[SearchTools.search_internet, BrowserTools.scrape_and_summarize_website, ScrapeWebsiteTool(), WebsiteSearchTool()],
        llm=llm,
        max_iter=max_iter
    )

    review_analyzer = Agent(
        role="Especialista em Análise de Avaliações de Produtos",
        goal=f"""Analisar avaliações e classificações de clientes para {product_name}, identificando padrões de satisfação e insatisfação entre as ofertas.""",
        backstory=f"""Especialista em análise de feedback de clientes, focado em entender a qualidade percebida e os principais pontos positivos e negativos.""",
        verbose=True,
        allow_delegation=True,
        tools=[SearchTools.search_internet, BrowserTools.scrape_and_summarize_website, ScrapeWebsiteTool(), WebsiteSearchTool()],
        llm=llm,
        max_iter=max_iter
    )

    # Definir Tarefas
    task1 = Task(
        description=f"""Buscar e coletar os preços de {product_name} em diversos sites de e-commerce e marketplaces.""",
        expected_output="Lista de preços coletados com links para cada oferta.",
        agent=price_scraper
    )

    task2 = Task(
        description=f"""Analisar as especificações técnicas dos produtos encontrados para verificar se são compatíveis ou se há variações significativas.""",
        expected_output="Relatório de compatibilidade de especificações com observações sobre variações encontradas.",
        agent=specification_analyzer
    )

    task3 = Task(
        description=f"""Comparar os preços coletados, determinando o menor, o maior e a média de preços para {product_name}.""",
        expected_output="Relatório com análise de preço mínimo, máximo, e médio, com observações sobre descontos e variações.",
        agent=price_analyzer
    )

    task4 = Task(
        description=f"""Analisar as avaliações e classificações de clientes para identificar padrões de satisfação ou problemas comuns com o {product_name}.""",
        expected_output="Relatório de análise de feedback com insights sobre a qualidade percebida e problemas recorrentes.",
        agent=review_analyzer
    )

    # Criar e Executar a Equipe
    price_comparison_crew = Crew(
        agents=[price_scraper, specification_analyzer, price_analyzer, review_analyzer],
        tasks=[task1, task2, task3, task4],
        verbose=True,
        process=Process.concurrent,  # Altere para Process.concurrent
        manager_llm=llm
    )

    crew_result = price_comparison_crew.kickoff()
    return crew_result
