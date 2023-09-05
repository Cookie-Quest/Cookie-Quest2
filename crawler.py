from flask import Flask, render_template, jsonify, send_file, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
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
from utils.store_websites_in_excel import store_websites_in_excel
from selenium.common.exceptions import InvalidArgumentException
from openpyxl import load_workbook
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import datetime, sched
import time
import csv
import pandas as pd
from colorama import Fore, Style, Back, init

init()

app = Flask(__name__)

# Define the upload folder where files will be stored
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}  # Set allowed file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global list to store website URLs
website_urls = [
    'https://www.afsdealerinsurance.com',
    'https://ironwoodins.com/'
]

# Function to add a website URL to the list
def add_website_to_scan(website_url):
    website_urls.append(website_url)

# Function to get the current list of website URLs
def get_website_list():
    return website_urls

# Route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html')

# Route to add a new website URL to the list
@app.route('/add_website', methods=['POST'])
def add_website():
    data = request.get_json()
    if 'url' in data:
        new_url = data['url']
        add_website_to_scan(new_url)  # Add the new URL to the list
        print("Added website:", new_url)  # Print the added website for debugging

        # Store the updated websites list in an Excel sheet
        excel_filename = store_websites_in_excel(website_urls)

        return jsonify({"message": "Website added successfully", "excel_filename": excel_filename})
    else:
        return jsonify({"error": "URL not provided"}), 400

# Route to scan cookies on websites
@app.route('/scan_cookies', methods=['GET', 'POST'])
def scan_cookies():
    global website_urls  # Use the global website_urls list

    # Rest of your code...

    banner_identifiers = [
        ("ID", "truste-consent-track"),
        ("CLASS_NAME", "osano-cm-dialog__buttons"),
        ("ID", "osano-cm-buttons")
        # Add more banner identifiers if needed
    ]

    cookie_data = []

    for url in website_urls:
        try:
            print("Scanning website:", url)  # Print the currently scanned website for debugging
            cookies = scan_website(url, banner_identifiers)
            cookie_data.extend(cookies)
        except Exception as e:
            # Log the error and continue with the next website scanning task
            print(f"Error scanning website {url}: {str(e)}")
            continue  # Continue with the next website scanning task

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

# Error handler for InvalidArgumentException
@app.errorhandler(InvalidArgumentException)
def handle_invalid_argument_exception(error):
    # You can customize the error message and response as needed
    error_message = "Invalid argument: Please check the URL you provided."
    return render_template("error.html", error_message=error_message), 500  # Use status code 500 for internal server error

# Route to download the Excel file
@app.route('/download_excel')
def download_excel():
    try:
        # Replace with the actual path to your Excel file
        excel_file_path = "cookie_data.xlsx"

        # Adjust column widths before sending the file
        workbook = load_workbook(excel_file_path)
        sheet = workbook.active

        # Iterate through all columns and adjust their width based on the content
        for column in sheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column[0].column_letter].width = adjusted_width

        # Save the adjusted Excel file
        workbook.save(excel_file_path)

        # Send the adjusted Excel file as an attachment
        return send_file(excel_file_path, as_attachment=True, download_name="cookie_data.xlsx")
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Initialize the background scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

# Add the scan function to the scheduler to run every 6 days
scheduler.add_job(perform_scan, 'interval', days=6)  # Adjust the interval as needed

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to upload an Excel file containing a list of websites
# Route to upload a file
@app.route('/upload', methods=['POST'])
def upload_file():
    global website_urls  
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Ensure that the directory exists before saving the file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save the uploaded file
            file.save(file_path)

            df = pd.read_excel(file_path)
            new_urls = df['Website'].tolist()

            # Update the website_urls list
            website_urls.extend(new_urls)

            print(f"New website_urls: {website_urls}")  # Debugging

            # Store the updated websites list in an Excel sheet (You should implement this function)
            # excel_filename = store_websites_in_excel(website_urls)

 # Store the updated websites list in an Excel sheet
            excel_filename = store_websites_in_excel(website_urls)
            
            return jsonify({"message": "File uploaded successfully"})
        else:
            return jsonify({"error": "Invalid file format. Please upload an .xlsx file"}), 400

    return '''
    <!doctype html>
    <title>Upload an Excel File</title>
    <h1>Upload an Excel file</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
