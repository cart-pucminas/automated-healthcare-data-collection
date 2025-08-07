from src.util import *

from selenium.webdriver.common.by import By

#Definicao de subclasses para classificação de elementos a partir da classe base ElementoInterativo

class ElementoInterativo:
    def __init__(self):
        self.identifiers = {
            'id': None,
            'class': None,
            'name': None,
            'xpath': None,
            'tag': None
        }
        self.attributes = {
            'text': None,
            'visible': None,
            'enabled': None
        }
        self.associated_options = {}

    def click_xpath(self, xpath, driver):
        try:
            if not self.dropdown_opened and self.identifiers['xpath'] is not None:
                dropdown_element = driver.find_element(By.XPATH, self.identifiers['xpath'])
                dropdown_element.click()
                self.dropdown_opened = True
                
            option_element = driver.find_element(By.XPATH, xpath)
            option_element.click()
            
        except Exception as e:
            print(f"Erro ao clicar no elemento com XPath {xpath}: {str(e)}")

            
        except Exception as e:
            print(f"Erro ao clicar no elemento com XPath {xpath}: {str(e)}")

class Input(ElementoInterativo):
    def __init__(self):
        super().__init__()
        self.input_type = None
        self.current_value = None
        self.placeholder = None

class Dropdown(ElementoInterativo):
    def __init__(self):
        super().__init__()
        self.current_value = None
        self.available_options = []
        self.placeholder = None

class Button(ElementoInterativo):
    def __init__(self):
        super().__init__()
        self.clickable = True
        self.type = None

class Checkbox(ElementoInterativo):
    def __init__(self):
        super().__init__()
        self.checked = False
        self.group_name = None
        
class Radio(ElementoInterativo):
    def __init__(self):
        super().__init__()
        self.checked = False
        self.group_name = None
        self.value = None
        self.label_text = None
        self.associated_options = {}