import requests
from bs4 import BeautifulSoup
import re
import time
import json
from openai import OpenAI

file = open("API_key.txt", "r")
chave = file.read()
file.close()


def obter_titulos(urls, prompt):
    client = OpenAI()
    all_titulos = []

    for url in urls:
        try:
            print(f"Acessando: {url}")
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            site = BeautifulSoup(response.text, "html.parser")
            titulo = site.title.string.strip() if site.title else "Sem título"
            print(f"Título encontrado: {titulo}")
            all_titulos.append(titulo)
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            all_titulos.append("Erro ao acessar")

    conteudo = "\n".join([f"{i}. {titulo}" for i, titulo in enumerate(all_titulos)])

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"""
Você receberá uma lista numerada de títulos de páginas da web. Seu trabalho é identificar **apenas os títulos que se relacionam diretamente** com o tema: \"{prompt}\".

Critérios:
- Um título é relevante **somente** se ele abordar diretamente o tema.
- Ignore qualquer título que trate de outro assunto, mesmo que remotamente relacionado.
- Responda apenas com os números das posições dos títulos pertinentes, separados por vírgula (ex: 2, 4).
- Se nenhum título for pertinente, responda apenas: NULL.
"""},
            {"role": "user", "content": conteudo}
        ]
    )

    resposta = completion.choices[0].message.content.strip()
    print("Resposta do modelo:", resposta)

    links_pertinentes = []
    if resposta != "NULL":
        try:
            posicoes = [int(pos.strip()) for pos in resposta.split(",") if pos.strip().isdigit()]
            for i in posicoes:
                if 0 <= i < len(urls):
                    links_pertinentes.append(urls[i])
        except ValueError:
            print("Erro ao processar as posições retornadas pelo GPT.")
    else:
        print("Sem links relevantes dado o prompt inicial.")
        return 0
    return links_pertinentes

def topicos_pagina(url, prompt):
    client = OpenAI()
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}

    try:
        req = requests.get(url, headers=HEADERS)
        req.raise_for_status()
        site = BeautifulSoup(req.text, "html.parser")
        siteT = site.prettify()[:550000]

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
"content": f"""
Você receberá o código HTML de um website. Sua tarefa é identificar e listar os principais tópicos diretamente relacionados ao seguinte tema: \"{prompt}\".

Formato da resposta:
- Cada tópico deve começar com o nome do tópico (sem introduções como 'tópico relevante').
- Após o nome do tópico, adicione dois pontos ':' e liste informações diretamente relacionadas, separadas por vírgulas.
- Termine cada linha com ponto e vírgula ';'.

Exemplo de estrutura:
Doenças infecciosas: febre, calafrios, mal-estar;
Prevenção: uso de repelente, vacinação, evitar água parada;

Importante:
- Foque apenas nos conteúdos que realmente tratam do tema solicitado.
- Ignore informações genéricas, propagandas ou itens não relacionados.
- Seja conciso, claro e direto nas informações.
"""},
                {"role": "user", "content": siteT}
            ]
        )
        topicos = completion.choices[0].message.content
        print(f"\nTópicos:\n")
        print(f"\n{topicos}\n")
        return topicos
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return None


def resumir_conteudo(url):
    client = OpenAI()
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}

    try:
        print(f"\nObtendo conteúdo de: {url}")
        req = requests.get(url, headers=HEADERS)
        req.raise_for_status()
        html = req.text
        site = BeautifulSoup(html, "html.parser")
        siteT = site.prettify()[:16384]

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
"content": """
Você receberá o código HTML de um website. Sua tarefa é gerar um resumo claro e objetivo do conteúdo principal da página.

Instruções:
- Foque no conteúdo informativo e relevante da página.
- Ignore elementos como menus, rodapés, anúncios e links externos.
- Se o conteúdo tratar de um tema específico (ex: saúde, educação, meio ambiente), destaque as principais ideias abordadas.
- O resumo deve ter no máximo 5 linhas, com frases concisas.

Se o conteúdo não for claro ou estiver incompleto, indique isso brevemente no final.
"""},
                {"role": "user", "content": siteT}
            ]
        )
        resumo = completion.choices[0].message.content
        print(f"Resumo do site {url}:\n{resumo}\n")
        return resumo
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return None, None

def main():
    prompt = input("Digite o prompt para a busca de pertinência dos links: ")

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
    ]

    links_pertinentes = obter_titulos(urls, prompt)
    if links_pertinentes != 0:
        print(f"\nLinks pertinentes identificados: {links_pertinentes}\n")

        resultados = {}

        for link in links_pertinentes:
            resumir_conteudo(link)
            topicos = topicos_pagina(link, prompt)
            if topicos:
                resultados[link] = {
                    "topicos": topicos
                }

        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()