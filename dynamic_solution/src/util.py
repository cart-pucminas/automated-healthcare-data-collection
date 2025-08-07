import os
import time

from dotenv import load_dotenv
import os
from table_extractor import TableExtractor

from openai import OpenAI

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from openai import OpenAI

load_dotenv()

def list_directory(path):
    for entry in os.listdir(path):
        print(entry)

def setup_selenium():
    options = Options()

    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    user_data_dir = os.path.join(os.environ["USERPROFILE"], 
                                "AppData", "Local", "Google", "Chrome", "User Data")
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument("profile-directory=Default")
    
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DRIVER_PATH = os.path.join(BASE_DIR, "selenium", "chromedriver.exe")
    service = Service(executable_path=DRIVER_PATH)

    driver = webdriver.Chrome(service=service, options=options)
    return driver

def format_dropdown_data(elements):
    formatted_text = "User Prompt: Search for information on the death rate and prevalence of HIV in women located in Central Asia, between 2010 and 2018. Available Filter Dropdowns:\n\n"
    count = 1
    
    for element in elements:
        if not element.associated_options:
            continue
            
        dropdown_info = f"Dropdown {count}:\n"
        if element.identifiers['name']:
            dropdown_info += f"Label: {element.identifiers['name']}\n"
            
        dropdown_info += "Available Options:\n"
        for label in element.associated_options.keys():
            dropdown_info += f"- {label}\n"
            
        formatted_text += dropdown_info + "\n"
        count += 1
    
    return formatted_text

def select_filters(elements):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    system_message = """You are a specialized filter combination analyzer for web-based applications. Your task is to evaluate multiple dropdown filters and determine the optimal combination of selections based on their labels.
Rules for Analysis:
1. Consider all provided dropdown menus as an interconnected filtering system
2. Evaluate available options based on user requirements
3. Prioritize combinations that provide the most relevant results
4. Each dropdown menu can have more than one available option selected

Output Format:
Return only a list of selected options in the following format:
["Dropdown 1 Label", "Available Option A", "Available Option B", "Available Option C"]
["Dropdown 2 Label", "Available Option D", "Available Option E", "Available Option F"]
["Dropdown 3 Label", "Available Option G", "Available Option H", "Available Option I"]
Where Dropdown Label represents the label of each dropdown menu and each list represents your chosen selection of available options from each dropdown menu. 
Ensure that all labels and options in the output match exactly as they appear in the input, preserving every punctuation mark, accent, and formatting detail without modification.
"""


    formatted_message = format_dropdown_data(elements)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": formatted_message},
        ]
    )
    resposta = completion.choices[0].message.content
    return parse_options(resposta)

def parse_options(input_str):
    input_str = input_str.replace('\n', ' ').strip()
    groups = input_str.strip('[]').split('] [')
    
    result = []
    for group in groups:
        items = [item.strip(' "') for item in group.split('",')]
        result.append({
            'label': items[0],
            'options': items[1:]
        })
    return result

def configure_filters(elements, selected_filters, driver):
    """
    a função percorre uma coleção de objetos ElementoIterativo e uma lista selected_filters,
    realizando cliques nos elementos quando seus identificadores e opções correspondem aos filtros selecionados.

    Para cada selected_filter na lista de entrada:
    - Pesquisar entre os objetos ElementoIterativo por uma chave 'name' em identifiers que corresponda ao label do filtro
        *Se nenhum 'name' corresponder ao label atual, passar para o próximo elemento
    - Quando encontrar um match, processa todas as opções especificadas nesse filtro:
        * Para cada opção na lista de opções do filtro, pegar seu xpath correspondente do 
        dicionário associated_options do elemento
        * Chamar click_xpath() com o valor do xpath recuperado
    - Continuar para o próximo filtro na lista

    elements (list[ElementoIterativo]): Lista de elementos interativos, cada um contendo:
        - identifiers: Dicionário com 'name' e outros identificadores do elemento
        - associated_options: Dicionário que mapeia rótulos de opções para seus xpaths
    selected_filters (list[dict]): Lista de seleções de filtro, cada uma contendo:
        - label: String correspondente ao 'name' de um ElementoIterativo
        - options: Lista de strings correspondentes às chaves em associated_options
    driver: driver selenium configurado e já aberto no código
    """
    print("""
Configurando filtros...
          """)
    for selected_filter in selected_filters:
        first_option = True
        filter_label = selected_filter['label']
        filter_options = selected_filter['options']
        
        matched_element = None
        for element in elements:
            if element.identifiers['name'] is not None and element.identifiers['name'] == filter_label:
                matched_element = element
                break
        
        if matched_element is None:
            continue
        
        matched_element.dropdown_opened = False
        
        for option in filter_options:
            if first_option:
                time.sleep(1)
                try:
                    xpath = matched_element.identifiers['xpath']
                    print(f"Trying to clear dropdown {matched_element.identifiers['name']}")
                    
                    clear_current_dropdown(driver, matched_element)
                    time.sleep(0.5)
                    first_option = False
                except Exception as e:
                    print(f"No clear button found for {filter_label} or error clearing: {str(e)}")
                    
            if option in matched_element.associated_options:
                xpath = matched_element.associated_options[option]

                print(f"Choosing option: '{option}' with XPath: {xpath}")
                time.sleep(0.5)
                matched_element.click_xpath(xpath, driver)
                time.sleep(0.5)
        
        try:
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.3) 
        except:
            pass

def clear_current_dropdown(driver, matched_element):
    try:
        element_name = matched_element.identifiers['name']
        
        select_element = driver.find_element(
            By.XPATH, 
            f"//div[contains(@class, 'ant-select') and @aria-label='{element_name}']"
        )
        
        clear_button = select_element.find_element(
            By.XPATH,
            ".//span[contains(@class, 'ant-select-clear')]/button"
        )
        
        clear_button.click()
        print(f"Successfully cleared dropdown: {element_name}")
        time.sleep(0.5)
        return True
        
    except Exception as e:
        print(f"Error clearing dropdown {element_name}: {str(e)}")
        return False

def explore_dropdowns(driver, extractor, elements):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    import time

    for target_element in elements:
        if target_element.identifiers['name'] in ["aaa"]: 
            continue
            
        xpath = target_element.identifiers.get('xpath')
        if not xpath:
            print(f"No xpath found for {target_element.identifiers['name']}")
            continue
            
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element.click()
            
            time.sleep(0.5)
            target_element.associated_options = extractor.get_dropdown_options()
            
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            
        except Exception as e:
            print(f"Error exploring dropdown {target_element.identifiers['name']}: {str(e)}")
            continue
    
    try:
        time.sleep(0.5)
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        clear_button = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, 
                "//button[@aria-label='Clear selection']"))
        )
        clear_button.click()
    except Exception as e:
        print(f"No clear button found or already empty: {str(e)}")
    
    return elements

def execute_search(driver, wait_time=20):
    try:
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.anticon.anticon-search[aria-label='search']"))
        )
        search_button.click()
        
        time.sleep(wait_time)
        return True
    except Exception as e:
        print(f"Error executing search: {str(e)}")
        return False


def extract_and_save_results(driver, filename_prefix="gbd_results"):
    table_extractor = TableExtractor(driver)
    table_extractor.detect_table_structure()
    
    results_df = table_extractor.extract_table_data()
    
    if not results_df.empty:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        table_extractor.save_to_csv(results_df, filename)
        
        print("\nSample of extracted data:")
        print(results_df.head())
        print(f"\nTotal rows: {len(results_df)}")
    else:
        print("Failed to extract table data")
    
    return results_df