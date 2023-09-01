from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import datetime

app = Flask(__name__)

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
    
    banner_info = []
    
    for identifier_type, identifier_value in banner_identifiers:
        try:
            if identifier_type == "ID":
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, identifier_value)))
            elif identifier_type == "CLASS_NAME":
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, identifier_value)))
            
            consent_banner_div = driver.find_element(getattr(By, identifier_type), identifier_value)
            buttons = consent_banner_div.find_elements(By.TAG_NAME, "button")
            banner_info.append({
                "identifier_type": identifier_type,
                "identifier_value": identifier_value,
                "button_count": len(buttons),
                "buttons_text": [button.text for button in buttons]
            })
        except TimeoutException:
            pass
    
    return banner_info

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/scan_cookies')
def scan_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service('./driver/chromedriver.exe')  # Update this path to your chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    website_urls = ['https://ironwoodins.com/', 'https://icip.marshpm.com/FedExWeb/login.action']
    
    scanned_cookies = []

    for website_url in website_urls:
        driver.get(website_url)
        
        cookie_names = [
            'osano_consentmanager',
            'osano_consentmanager_uuid',
            'TrustArc'
        ]

        cookies = driver.get_cookies()

        for cookie in cookies:
            if cookie['name'] in cookie_names:
                scanned_cookies.append({
                    'name': cookie['name'],
                    # 'value': cookie['value'],
                    'domain': cookie['domain'],
                    # 'path': cookie['path'],
                    'expiry': format_expiry(cookie['expiry']),
                    'secure': cookie['secure']
                })

        # Check for consent banners and add banner info
        banner_info = check_and_report_banner(driver)
        if banner_info:
            scanned_cookies[-1]['banner_info'] = banner_info

    driver.quit()
    return jsonify({'cookies': scanned_cookies})

if __name__ == '__main__':
    app.run()

