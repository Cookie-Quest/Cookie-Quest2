from flask import Flask, render_template, jsonify, send_file, request
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
from utils.perform_scan import  perform_scan
from utils.website_manager import add_website_to_scan
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import datetime, sched
import time
import csv
import pandas as pd
from colorama import Fore, Style, Back, init

init()

app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

website_urls = []

@app.route('/')
def index():
    return render_template('index.html')

def add_website_to_scan(website_url):
    website_urls.append(website_url)

def get_website_list():
    return website_urls

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/add_website', methods=['POST'])
def add_website():
    data = request.get_json()
    if 'url' in data:
        new_url = data['url']
        add_website_to_scan(new_url)  # Add the new URL to the list
        print("Added website:", new_url)  # Print the added website for debugging
        return jsonify({"message": "Website added successfully"})
    else:
        return jsonify({"error": "URL not provided"}), 400


@app.route('/scan_cookies', methods=['GET', 'POST'])
def scan_cookies():
    website_urls = get_website_list()
    print("Websites to scan:", website_urls)  # Print the list of websites to scan for debugging

    banner_identifiers = [
        ("ID", "truste-consent-track"),
        ("CLASS_NAME", "osano-cm-dialog__buttons"),
        ("ID", "osano-cm-buttons")
        # Add more banner identifiers if needed
    ]

    cookie_data = []

    for url in website_urls:
        print("Scanning website:", url)  # Print the currently scanned website for debugging
        cookies = scan_website(url, banner_identifiers)
        cookie_data.extend(cookies)
        
    # website_urls = [
    #     # 'https://ironwoodins.com/',
    #     # 'https://www.aga-us.com/'
    #     # Add more website URLs here
    # ]

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


# Add the scan function to the scheduler to run every 150 seconds
# scheduler.add_job(perform_scan, 'interval', seconds=10)  # Adjust the interval as needed

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
