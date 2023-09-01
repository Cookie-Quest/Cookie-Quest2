from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import datetime

def format_expiry(expiry_timestamp):
    if expiry_timestamp:
        expiry_datetime = datetime.datetime.fromtimestamp(expiry_timestamp)
        return expiry_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return "N/A"



def check_and_report_banner(driver):
    banner_ids = ["truste-consent-track", "osano-cm-manage osano-cm-buttons__button osano-cm-button osano-co-button --type_manage", 
                  "osano-cm-window__dialog osano-cm-dialog osano-cm-dialog--position_bottom osano-cm-dialog--type_bar"]
    
    # class_ids = ["osano-cm-dialog__content osano-cm-content"]

    for banner_id in banner_ids:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, banner_id)))
            consent_banner_div = driver.find_element(By.ID, banner_id)
            buttons = consent_banner_div.find_elements(By.TAG_NAME, "button")
            div_elements = consent_banner_div.find_elements(By.CSS_SELECTOR, 'osano-cm-dialog__content osano-cm-content')


            # class_name = consent_banner_div.find_elements(By.CLASS_NAME, "osano-cm-dialog__content osano-cm-content")
            
            if buttons:
                print(f"Consent banner with ID '{banner_id}' is present on the page:")
                print(f"Number of buttons: {len(buttons)}")
                for idx, button in enumerate(buttons, start=1):
                    print(f"Button {idx} text: {button.text}")

            if div_elements:
                print(f"div elements found with banner '{banner_id}':")
                for idx, div_elements in enumerate(div_elements, start=1):
                    print(f"Div element {idx} text: {div_elements.text}")
               
                
            else:
                print(f"No buttons found in the consent banner with ID '{banner_id}'.")
            return True
        except TimeoutException:
            continue
    return False

def scan_website(website_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service('./driver/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print(f"Scanned website: {website_url}")
    driver.get(website_url)
    print("Page title:", driver.title)

    cookie_names = [
        'osano_consentmanager',
        'osano_consentmanager_uuid',
        'TrustArc',
        'JSESSIONID'
    ]

    cookies = driver.get_cookies()

    for cookie in cookies:
        if cookie['name'] in cookie_names:
            print(f"Cookie Name: {cookie['name']}")
            print(f"Domain: {cookie['domain']}")
            print(f"Expires: {format_expiry(cookie['expiry'])}")
            print(f"Secure: {cookie['secure']}")
            print("-----")

    # Check for consent banners
    banner_present = check_and_report_banner(driver)
    if not banner_present:
        print("No consent banners found on the page.")

    driver.quit()

def main():
    website_urls = [
        'https://ironwoodins.com/',
        'https://www.linqbymarsh.com/linq/auth/login'
        'https://icip.marshpm.com/FedExWeb/',
        'https://www.marshmanagement.com/',
        'https://www.linqbymarsh.com/blueicyber/',
        'https://services.marshspecialty.com/msp-web/register?division=MSP&client=SF',
        'https://www.dovetailexchange.com/Account/Login',
        'https://www.victorinsurance.it/',
        'https://www.sanint.it/',
        'https://www.victorinsurance.nl/',
        'https://www.marshunderwritingsubmissioncenter.com',
        'https://nordicportal.marsh.com/dk/crm/crm_internet.nsf',
        'https://victorinsurance.nl/versekeraars/'


    ]

    print("Starting the script")
    for url in website_urls:
        scan_website(url)
    print("Script execution finished")

if __name__ == "__main__":
    main()
