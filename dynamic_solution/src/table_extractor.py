import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TableExtractor:
    def __init__(self, driver):
        self.driver = driver
        
    def extract_table_data(self, timeout=30):
        try:
            print("Waiting for table to load...")
            table_container = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table-wrapper, .data-table"))
            )
            
            time.sleep(2)
            
            headers = self._extract_table_headers()
            
            rows_data = self._extract_table_rows()
            
            if rows_data and headers:
                df = pd.DataFrame(rows_data, columns=headers)
                print(f"Successfully extracted table with {len(df)} rows and {len(headers)} columns")
                return df
            else:
                print("Table appears to be empty or couldn't be properly extracted")
                return pd.DataFrame()
            
        except TimeoutException:
            print(f"Table did not load within {timeout} seconds")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error extracting table data: {str(e)}")
            return pd.DataFrame()
    
    def _extract_table_headers(self):
        try:
            header_selectors = [
                ".ant-table-thead th", 
                ".table-header",
                ".header-cell"
            ]
            
            headers = []
            for selector in header_selectors:
                header_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if header_elements:
                    headers = [header.text.strip() for header in header_elements if header.text.strip()]
                    print(f"Found {len(headers)} headers with selector: {selector}")
                    break
            
            return headers
        except Exception as e:
            print(f"Error extracting headers: {str(e)}")
            return []
    
    def _extract_table_rows(self):
        try:
            row_selectors = [
                ".ant-table-tbody tr",
                ".table-row",
                ".data-row"
            ]
            
            rows = []
            row_elements = []
            
            for selector in row_selectors:
                row_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if row_elements:
                    print(f"Found {len(row_elements)} rows with selector: {selector}")
                    break
            
            for row_element in row_elements:
                cell_selectors = [
                    "td",
                    ".ant-table-cell",
                    ".cell"
                ]
                
                row_data = []
                for selector in cell_selectors:
                    cell_elements = row_element.find_elements(By.CSS_SELECTOR, selector)
                    if cell_elements:
                        row_data = [cell.text.strip() for cell in cell_elements]
                        break
                
                if row_data:
                    rows.append(row_data)
            
            return rows
        except Exception as e:
            print(f"Error extracting rows: {str(e)}")
            return []
    
    def save_to_csv(self, dataframe, filename="gbd_results.csv"):
        if not dataframe.empty:
            dataframe.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data saved to {filename}")
        else:
            print("No data to save")
    
    def detect_table_structure(self):
        print("\n=== DETECTING TABLE STRUCTURE ===\n")
        
        try:
            table_selectors = [
                ".ant-table", 
                ".ant-table-wrapper", 
                "table", 
                ".data-table",
                ".visualization-container table"
            ]
            
            for selector in table_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found potential table with selector '{selector}'")
                    
                    if len(elements) > 0:
                        html_structure = elements[0].get_attribute("outerHTML")
                        print(f"Sample HTML structure (first 300 chars):\n{html_structure[:300]}...\n")
                        
                        children = elements[0].find_elements(By.XPATH, "./*")
                        print(f"First-level children: {len(children)}")
                        for i, child in enumerate(children[:3]):
                            tag = child.tag_name
                            classes = child.get_attribute("class")
                            print(f"  Child {i+1}: <{tag}> with classes '{classes}'")
                        
                        if len(children) > 3:
                            print(f"  ... and {len(children) - 3} more children")
            
            viz_selectors = [
                "[data-testid='visualization']",
                ".vizHub-visualization",
                ".chart-container",
                ".table-visualization"
            ]
            
            for selector in viz_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found potential visualization container with selector '{selector}'")
        
        except Exception as e:
            print(f"Error detecting table structure: {str(e)}")