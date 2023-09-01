from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time, sched, csv, datetime
import schedule
import threading


# ... (all your previous imports and functions)

def job():
    website_urls = [
        # Your URLs
    ]

    cookie_data = []

    for url in website_urls:
        cookies = scan_website(url)
        cookie_data.extend(cookies)

    print(f"Scheduled scan complete. Cookie data: {cookie_data}")


# Schedule the job to run at intervals (for example, every day at 5pm)
schedule.every().day.at("17:00").do(job)


# Function to run the pending scheduled tasks in a separate thread
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Initialize the Flask application
app = Flask(__name__)


# Flask routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scan_cookies')
def scan_cookies():
    website_urls = [
        # Your URLs
    ]

    cookie_data = []

    for url in website_urls:
        cookies = scan_website(url)
        cookie_data.extend(cookies)

    return jsonify({"cookies": cookie_data})


# Run the schedule in a separate thread
t = threading.Thread(target=run_schedule)
t.start()

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
