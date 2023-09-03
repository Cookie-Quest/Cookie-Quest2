from flask import Flask, render_template, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.format_expiry import format_expiry
from utils.check_and_report_banner import check_and_report_banner
from utils.check_trustarc import check_trustarc
from utils.find_element_with_multiple_xpaths import find_element_with_multiple_xpaths
from utils.detect_manage_cookies_link import detect_manage_cookies_link
from utils.get_footer_details import get_footer_details
from utils.scan_website import scan_website
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import datetime, sched
import time
import csv
import pandas as pd
from colorama import Fore, Style, Back, init

init()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan_cookies')
def scan_cookies():
    website_urls = [
        'https://ironwoodins.com/',
        'https://www.aga-us.com/'
        # Add more website URLs here
    ]

    banner_identifiers = [
        ("ID", "truste-consent-track"),
        ("CLASS_NAME", "osano-cm-dialog__buttons"),
        ("ID", "osano-cm-buttons")
        # Add more banner identifiers if needed
    ]

    cookie_data = []

    for url in website_urls:
        cookies = scan_website(url, banner_identifiers)
        cookie_data.extend(cookies)

    # Create a CSV file and write the data
    csv_filename = "cookie_data.csv"
    with open(csv_filename, mode='w', newline='') as csv_file:
        fieldnames = ["name", "domain", "expiry", "secure", "ccmImplemented", "consentBanner", "provider", "popUpWorking", "buttonType", "manageCookiesLink", "Duration"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for cookie in cookie_data:
            writer.writerow(cookie)

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_filename)

    # Convert the DataFrame to an Excel file
    excel_filename = "cookie_data.xlsx"
    df.to_excel(excel_filename, index=False)

    return jsonify({"cookies": cookie_data, "csv_filename": csv_filename, "excel_filename": excel_filename})


@app.route('/download_excel')
def download_excel():
    try:
        # Replace with the actual path to your Excel file
        excel_file_path = "cookie_data.xlsx"
        return send_file(excel_file_path, as_attachment=True, download_name="cookie_data.xlsx")
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
    
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

def perform_scan():
    try:
        # Schedule the scan_cookies_route every 150 seconds (2.5 minutes)
        app.app_context().push()
        with app.test_request_context():
            response = requests.get('http://127.0.0.1:5000/scan_cookies')  # Update the port if needed
            if response.status_code == 200:
                cookies = response.json()['cookies']
                # Process the cookies data as needed
                print(f'Scanned at {time.ctime()} - Cookies: {cookies}')
            else:
                print(f"An error occurred: {response.status_code}", response.status_code)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Add the scan function to the scheduler to run every 150 seconds
scheduler.add_job(perform_scan, 'interval', seconds=150)  # Adjust the interval as needed

if __name__ == "__main__":
    app.run(debug=True)

# You can schedule scans here if needed
# s = sched.scheduler(time.time, time.sleep)
# def run_script(sc):
#     # print("Running scheduled scan...")
#     s.enter(150, 1, run_script, (sc,))
# if __name__ == "__main__":
#     s.enter(0, 1, run_script, (s,))
#     s.run()
