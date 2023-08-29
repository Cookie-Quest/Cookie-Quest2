from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import datetime

app = Flask(__name__)

def format_expiry(expiry_timestamp):
    if expiry_timestamp:
        expiry_datetime = datetime.datetime.fromtimestamp(expiry_timestamp)
        return expiry_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return "N/A"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan_cookies')
def scan_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service('./driver/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    website_url = ['https://ironwoodins.com/','https://icip.marshpm.com/FedExWeb/login.action']
    driver.get(website_url)

    cookie_names = [
        'osano_consentmanager',
        'osano_consentmanager_uuid',
        'TrustArc'
    ]

    cookies = driver.get_cookies()
    scanned_cookies = []

    for cookie in cookies:
        if cookie['name'] in cookie_names:
            scanned_cookies.append({
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie['domain'],
                'path': cookie['path'],
                'expiry': format_expiry(cookie['expiry']),
                'secure': cookie['secure']
            })

    driver.quit()
    return jsonify({'cookies': scanned_cookies})

if __name__ == '__main__':
    app.run()
