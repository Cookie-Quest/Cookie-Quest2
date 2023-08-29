import sched
import time
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
    banner_identifiers = [
        ("ID", "truste-consent-track"),
        ("CLASS_NAME", "osano-cm-dialog__buttons osano-cm-buttons"),
        ("ID", "c0d8f56f-f1e4-448c-ae61-0afc444db179")  # ID for the second banner
    ]
    
    for identifier_type, identifier_value in banner_identifiers:
        try:
            if identifier_type == "ID":
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, identifier_value)))
            elif identifier_type == "CLASS_NAME":
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, identifier_value)))
            
            consent_banner_div = driver.find_element(getattr(By, identifier_type), identifier_value)
            buttons = consent_banner_div.find_elements(By.TAG_NAME, "button")
            if buttons:
                print(f"Consent banner with {identifier_type} '{identifier_value}' is present on the page:")
                print(f"Number of buttons: {len(buttons)}")
                for idx, button in enumerate(buttons, start=1):
                    print(f"Button {idx} text: {button.text}")
            else:
                print(f"No buttons found in the consent banner with {identifier_type} '{identifier_value}'.")
            
            # Special handling for second banner
            if identifier_value == "c0d8f56f-f1e4-448c-ae61-0afc444db179":
                second_banner_button_div = consent_banner_div.find_element(By.CLASS_NAME, "osano-cm-dialog__buttons")
                second_banner_button = second_banner_button_div.find_element(By.CLASS_NAME, "osano-cm-manage")
                print(f"Button within second banner: {second_banner_button.text}")
            
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

        'https://ironwoodins.com/',
        'https://www.linqbymarsh.com/linq/auth/login',
        'https://icip.marshpm.com/FedExWeb/login.action',
        'https://www.marsh.com/us/home.html',
        'https://www.marsh.com/us/insights/risk-in-context.html',
        'https://www.dovetailexchange.com/Account/Login'
        'https://www.victorinsurance.com/us/en.html',
        'https://www.victorinsurance.it'
        'https://wwww.victorinsurance.nl'
        'https://www.marshunderwritingsubmissioncenter.com',
        'https://victorinsurance.nl/verzekeraars'
    ]

    print("Starting the script")
    for url in website_urls:
        scan_website(url)
    print("Script execution finished")

s = sched.scheduler(time.time, time.sleep)

def run_script(sc):
    main()
    s.enter(150, 1, run_script, (sc,))

if __name__ == "__main__":

    s.enter(0, 1, run_script, (s,))
    s.run()
