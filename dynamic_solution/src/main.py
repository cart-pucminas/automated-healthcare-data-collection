import time
from extrator import Extrator
from src.util import *

def run_gbd_workflow(url, inspect_time=20, max_attempts=3):
    extractor = Extrator()
    driver = setup_selenium()
    
    try:
        driver.get(url)
        time.sleep(1)
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        elements = extractor.extract_elements(driver)
        
        elements = explore_dropdowns(driver, extractor, elements)
        
        formatted_data = format_dropdown_data(elements)
        print(f"{formatted_data}")
        selected_filters = select_filters(elements)
        print(selected_filters)

        search_successful = False
        attempts = 0
        
        while not search_successful and attempts < max_attempts:
            attempts += 1
            print(f"\nAttempt {attempts} of {max_attempts} to configure filters and execute search...")
            
            time.sleep(3)
            configure_filters(elements, selected_filters, driver)
            time.sleep(5)
            
            search_successful = execute_search(driver)
            
            if not search_successful:
                print(f"Search button not found on attempt {attempts}. Retrying filter configuration...")
                time.sleep(2)

                if attempts < max_attempts:
                    try:
                        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(1)
                    except:
                        pass
        
        if not search_successful:
            print(f"Failed to execute search after {max_attempts} attempts")
            return None
        
        results_df = extract_and_save_results(driver)
        
        print(f"\nKeeping browser open for {inspect_time} seconds for inspection...")
        time.sleep(inspect_time)
        
        return results_df
        
    except Exception as e:
        print(f"Error in GBD workflow: {str(e)}")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    url = 'https://vizhub.healthdata.org/gbd-results/'
    run_gbd_workflow(url)