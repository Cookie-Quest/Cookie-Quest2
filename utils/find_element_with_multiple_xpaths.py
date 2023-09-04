# utils/find_element_with_multiple_xpaths.py
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def find_element_with_multiple_xpaths(driver, xpaths):
    for xpath in xpaths:
        try:
            element = driver.find_element(By.XPATH, xpath)
            return element
        except NoSuchElementException:
            continue
    return None
