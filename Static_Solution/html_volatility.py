import requests
from bs4 import BeautifulSoup
import re
import time
import json
from openai import OpenAI

file = open("API_key.txt", "r")
chave = file.read()
file.close()

def avaliar_estaticidade(url):
    client = OpenAI()
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
    
    try:
        req = requests.get(url, headers=HEADERS)
        req.raise_for_status()
        site = BeautifulSoup(req.text, "html.parser")
        siteT = site.prettify()[:16384]
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
            {"role": "system", "content": """Você é um especialista em análise de páginas web. Sua tarefa é classificar o conteúdo HTML fornecido como 'Estático' ou 'Dinâmico'.

                Definições:
                - Um site **Estático** apresenta principalmente blocos grandes de texto corrido sobre um assunto específico. Costuma ter estrutura simples, poucos scripts dinâmicos e geralmente não muda com frequência. Exemplo: artigos informativos, páginas de órgãos públicos com conteúdo textual.
                - Um site **Dinâmico** exibe conteúdo que muda frequentemente ou que é gerado dinamicamente. Costuma ter muitos scripts, seções com pouco texto contínuo, muitos links e imagens em destaque, atualizações ao vivo, ou foco em notícias, vídeos, redes sociais ou dashboards.

                Critérios de avaliação:
                - O HTML tem muito texto contínuo com subtítulos e parágrafos organizados? → Estático
                - O HTML tem pouca densidade de texto e muitos blocos visuais, menus interativos, carrosséis, áreas de login, ou feeds? → Dinâmico

                Responda **apenas** com uma das palavras: `Estático` ou `Dinâmico`. Nenhuma explicação adicional."""}

            ]""
        )
        resultado = completion.choices[0].message.content
        return resultado
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return None
def main():
    urls = [
        "https://bvsms.saude.gov.br/malaria-5/",
        "https://revistapesquisa.fapesp.br/o-mapa-das-hepatites/",
        "https://pt.wikipedia.org/wiki/Desfloresta%C3%A7%C3%A3o#:~:text=Desfloresta%C3%A7%C3%A3o%2C%20desflorestamento%2C%20desmate%20ou%20desmatamento,ou%20fun%C3%A7%C3%A3o%20de%20uma%20floresta.",
        "https://www.saude.pr.gov.br/Pagina/Febre-Maculosa",
        "https://bvsms.saude.gov.br/febre-amarela/",
        "https://bvsms.saude.gov.br/hiv-e-aids/",
        "https://bvsms.saude.gov.br/meningite/",
        "https://pt.wikipedia.org/wiki/Protestos_estudantis_indon%C3%A9sios_de_2025",
        "https://bvsms.saude.gov.br/infeccao-pelo-virus-zika/",
        "https://bvsms.saude.gov.br/febre-de-chikungunya/",
        "https://bvsms.saude.gov.br/hipertensao-18/",
        "https://pt.wikipedia.org/wiki/Intelig%C3%AAncia_artificial",
        "https://bvsms.saude.gov.br/diabetes/",
        "https://pt.wikipedia.org/wiki/C%C3%A1lculo_diferencial",
        "https://g1.globo.com/",
        "https://revistapesquisa.fapesp.br/violencia-escolar-aumenta-nos-ultimos-10-anos-no-brasil/",
        "https://revistapesquisa.fapesp.br/linamara-rizzo-battistella-2/",
        "https://www.who.int/pt/about",
        "https://www.paho.org/en/governance",
        "https://www.paho.org/en/bermuda",
        "https://www.gov.br/saude/pt-br",
        "https://data.worldbank.org/topic/health",
        "https://portaldatransparencia.gov.br/",
        "https://fapesp.br/",
        "https://news.google.com/home?hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://www.news-medical.net/",
        "https://www.discoveryplus.com/br/shows",
        "https://education.nationalgeographic.org/",
        "https://www.medscape.com/",
        
    ]

    for url in urls:
        resultado = avaliar_estaticidade(url)
        print(f"URL: {url} -> {resultado}")
        
if __name__ == "__main__":
    main()