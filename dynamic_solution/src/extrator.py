import sys
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class Extrator:
    def __init__(self):
        self.driver = None
        self.standard_selectors = {
            'button': 'button',
            'input': 'input:not([type="hidden"])',
            'select': 'select',
            'textarea': 'textarea',
            'radio': '.ant-radio-button-wrapper',
            'a': 'a[href]'
        }
        
        self.antd_selectors = {
            'button': '.ant-btn',
            'input': '.ant-input',
            'select': '.ant-select, .ant-select-selector',
            'checkbox': '.ant-checkbox-wrapper',
            'radio': '.ant-radio-wrapper',
            'switch': '.ant-switch',
            'dropdown': '.ant-dropdown-trigger',
            'datepicker': '.ant-picker'
        }

    def extract_elements(self, driver):
        self.driver = driver
        interactive_elements = []
        
        standard_elements = self._find_standard_elements()
        antd_elements = self._find_antd_elements()
        
        interactive_elements.extend(standard_elements)
        interactive_elements.extend(antd_elements)
        
        filtered_elements = [
            element for element in interactive_elements
            if element.identifiers['name'] is not None 
            and len(element.identifiers['name']) > 3 
            and element.identifiers['name'] != "Page Size"
        ]
        
        self.print_elements(filtered_elements)
        return filtered_elements

    def get_dropdown_options(self, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            
            # Try to identify which type of dropdown is open
            dropdown_containers = [
                ".ant-select-dropdown:not(.ant-select-dropdown-hidden)",
                ".ant-select-tree-list-holder-inner",
                ".ant-select-dropdown .ant-select-tree"
            ]
            
            dropdown = None
            for selector in dropdown_containers:
                try:
                    dropdown = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"Found dropdown with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not dropdown:
                print(f"No dropdown container found within {timeout} seconds")
                return {}
            
            # Based on which container was found, use appropriate option selectors
            options = []
            option_selectors = [
                ".ant-select-item.ant-select-item-option",
                ".ant-select-tree-node-content-wrapper",
                ".ant-select-tree-treenode .ant-select-tree-node-content-wrapper"
            ]
            
            for selector in option_selectors:
                options = dropdown.find_elements(By.CSS_SELECTOR, selector)
                if options:
                    print(f"Found {len(options)} options with selector: {selector}")
                    break
            
            options_dict = {}
            for option in options:
                label = None
                for attr in ['aria-label', 'title']:
                    label = option.get_attribute(attr)
                    if label:
                        break
                
                if not label:
                    label = option.text
                
                if label:
                    xpath = self._get_dropdown_option_xpath(option)
                    options_dict[label] = xpath
            
            print(f"Collected {len(options_dict)} options")
            return options_dict
                
        except TimeoutException:
            print(f"Dropdown did not appear within {timeout} seconds")
            return {}
        except Exception as e:
            print(f"Error getting dropdown options: {str(e)}")
            return {}

    def _find_standard_elements(self):
        elements = []
        
        for element_type, selector in self.standard_selectors.items():
            web_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            
            for web_element in web_elements:
                element = None
                if element_type == 'button':
                    element = self._create_button_element(web_element)
                elif element_type == 'input':
                    element = self._create_input_element(web_element)
                elif element_type == 'select':
                    element = self._create_dropdown_element(web_element)
                elif element_type == 'radio':
                    element = self._create_radio_element(web_element) 
                elif element_type == 'textarea':
                    # element = self._create_input_element(web_element)
                    print("skip")
                elif element_type == 'a':
                    element = self._create_button_element(web_element)
                
                if element:
                    elements.append(element)
        
        return elements

    def _find_antd_elements(self):
        elements = []
        elements = []
        
        for element_type, selector in self.antd_selectors.items():
            web_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            
            for web_element in web_elements:
                if element_type in ['button', 'switch', 'dropdown']:
                    element = self._create_button_element(web_element)
                elif element_type in ['input', 'datepicker']:
                    element = self._create_input_element(web_element)
                elif element_type == 'select':
                    element = self._create_dropdown_element(web_element)
                elif element_type == 'checkbox':
                    element = self._create_checkbox_element(web_element)
                
                if element:
                    elements.append(element)
        
        return elements

    def _create_button_element(self, web_element):
        """Create ButtonElement instance from WebElement"""
        from element_types import Button
        
        button = Button()
        
        button.identifiers = {
            'id': web_element.get_attribute('id'),
            'class': web_element.get_attribute('class'),
            'name': web_element.get_attribute('name'),
            'xpath': self._get_element_xpath(web_element),
            'tag': web_element.tag_name
        }
        
        button.attributes = {
            'text': web_element.text,
            'visible': web_element.is_displayed(),
            'enabled': web_element.is_enabled()
        }
        
        return button

    def _create_input_element(self, web_element):
        """Create InputElement instance from WebElement"""
        from element_types import Input
        
        input_elem = Input()
        
        input_elem.identifiers = {
            'id': web_element.get_attribute('id'),
            'class': web_element.get_attribute('class'),
            'name': web_element.get_attribute('aria-label'),
            'xpath': self._get_element_xpath(web_element),
            'tag': web_element.tag_name
        }
        
        input_elem.attributes = {
            'text': web_element.get_attribute('placeholder'),
            'visible': web_element.is_displayed(),
            'enabled': web_element.is_enabled()
        }
        
        input_elem.input_type = web_element.get_attribute('type')
        input_elem.current_value = web_element.get_attribute('value')
        input_elem.placeholder = web_element.get_attribute('placeholder')
        
        return input_elem

    def _create_dropdown_element(self, web_element):
        """Create DropdownElement instance from WebElement"""
        from element_types import Dropdown
        
        dropdown = Dropdown()
        
        dropdown.identifiers = {
            'id': web_element.get_attribute('id'),
            'class': web_element.get_attribute('class'),
            'name': web_element.get_attribute('name'),
            'xpath': self._get_element_xpath(web_element),
            'tag': web_element.tag_name
        }
        
        dropdown.attributes = {
            'text': web_element.text,
            'visible': web_element.is_displayed(),
            'enabled': web_element.is_enabled()
        }
        
        dropdown.current_value = web_element.get_attribute('value')
        dropdown.placeholder = web_element.get_attribute('placeholder')
        
        if web_element.tag_name == 'select':
            options = web_element.find_elements(By.TAG_NAME, 'option')
            dropdown.available_options = [option.text for option in options]
        elif 'ant-select' in (web_element.get_attribute('class') or ''):
            dropdown.available_options = []
            
        return dropdown

    def _create_checkbox_element(self, web_element):
        """Create CheckboxElement instance from WebElement"""
        from element_types import Checkbox
        
        checkbox = Checkbox()
        
        checkbox.identifiers = {
            'id': web_element.get_attribute('id'),
            'class': web_element.get_attribute('class'),
            'name': web_element.get_attribute('name'),
            'xpath': self._get_element_xpath(web_element),
            'tag': web_element.tag_name
        }
        
        checkbox.attributes = {
            'text': web_element.text,
            'visible': web_element.is_displayed(),
            'enabled': web_element.is_enabled()
        }
        
        checkbox.checked = web_element.is_selected()
        checkbox.group_name = web_element.get_attribute('name')
        
        return checkbox

    def _create_radio_element(self, web_element):
        """Create RadioElement instance from WebElement"""
        from element_types import Radio  
        
        radio = Radio()
        
        input_element = web_element.find_element(By.CSS_SELECTOR, "input[type='radio']")
        
        radio.identifiers = {
            'id': input_element.get_attribute('id'),
            'class': input_element.get_attribute('class'),
            'name': input_element.get_attribute('name'),
            'xpath': self._get_element_xpath(web_element),
            'tag': 'radio'
        }
        
        text_span = web_element.find_element(By.CSS_SELECTOR, "span > span")
        
        radio.attributes = {
            'text': text_span.get_attribute('title') or text_span.text,
            'visible': web_element.is_displayed(),
            'enabled': input_element.is_enabled(),
            'checked': input_element.is_selected()
        }
        
        radio.value = input_element.get_attribute('value')
        radio.label_text = text_span.text
        
        return radio

    def print_elements(self, elements):
        print("\n=== ELEMENTOS ENCONTRADOS ===\n")
        for element in elements:
            self._print_element_details(element)
    
    def _print_element_details(self, element):
        print("\nElement:")
        print(f"  Tipo: {type(element).__name__}")
        print("  Identifiers:")
        for key, value in element.identifiers.items():
            if value:  
                print(f"    {key}: {value}")
        print("  Attributes:")
        for key, value in element.attributes.items():
            if value: 
                print(f"    {key}: {value}")

    def _get_element_xpath(self, web_element):
        
        if web_element.get_attribute('id'):
            return f"//*[@id='{web_element.get_attribute('id')}']"
        
        try:
            script = """
            function getElementXPath(element) {
                if (element.id !== '')
                    return "//*[@id='" + element.id + "']";
                    
                if (element === document.body)
                    return '/html/body';
                    
                var ix = 0;
                var siblings = element.parentNode.childNodes;
                
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    
                    if (sibling === element)
                        return getElementXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                        ix++;
                }
            }
            return getElementXPath(arguments[0]);
            """
            
            xpath = self.driver.execute_script(script, web_element)
            return xpath
            
        except Exception as e:
            tag_name = web_element.tag_name
            class_name = web_element.get_attribute('class')
            if class_name:
                return f"//{tag_name}[@class='{class_name}']"
            return f"//{tag_name}"
        
    def _get_dropdown_option_xpath(self, option_element):
        if option_element.get_attribute('id'):
            return f"//*[@id='{option_element.get_attribute('id')}']"
        
        script = """
        function getElementXPath(element) {
            if (element.id !== '')
                return "//*[@id='" + element.id + "']";
                
            if (element === document.body)
                return '/html/body';
                
            var ix = 0;
            var siblings = element.parentNode.childNodes;
            
            for (var i = 0; i < siblings.length; i++) {
                var sibling = siblings[i];
                
                if (sibling === element)
                    return getElementXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                    ix++;
            }
        }
        return getElementXPath(arguments[0]);
        """
        
        xpath = self.driver.execute_script(script, option_element)
        return xpath