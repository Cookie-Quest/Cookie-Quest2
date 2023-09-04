# utils/scan_website.py
from colorama import Fore, Style, Back, init
from utils.format_expiry import format_expiry
from utils.get_cookie_expiry import get_cookie_expiry
from utils.calculate_cookie_duration import calculate_cookie_duration
from utils.check_and_report_banner import check_and_report_banner
from utils.check_trustarc import check_trustarc
from utils.find_element_with_multiple_xpaths import find_element_with_multiple_xpaths
from utils.detect_manage_cookies_link import detect_manage_cookies_link
from utils.get_footer_details import get_footer_details

from flask import Flask, render_template, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import datetime
import sched
import time
import csv
import pandas as pd

def scan_website(website_url, banner_identifiers):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service('./driver/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print(f"{Fore.GREEN}Scanned website:{Style.RESET_ALL}{Fore.CYAN}{website_url}{Style.RESET_ALL}")
    driver.get(website_url)
    print(f"{Fore.GREEN}Page title:{Style.RESET_ALL}{Fore.CYAN}{driver.title}{Style.RESET_ALL}")

    trustarc_present = check_trustarc(driver)
    osano_present = check_and_report_banner(driver)

    manage_cookies_button = False
    ok_button = False
    button_type = "None"
        
    manage_cookies_link = get_footer_details(driver)

    if trustarc_present or osano_present:
        consent_banner_div = None

        for identifier_type, identifier_value in banner_identifiers:
            try:
                wait = WebDriverWait(driver, 5)

                if identifier_type == "ID":
                    wait.until(EC.presence_of_element_located((By.ID, identifier_value)))
                elif identifier_type == "CLASS_NAME":
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, identifier_value)))

                consent_banner_div = driver.find_element(getattr(By, identifier_type), identifier_value)
                buttons = consent_banner_div.find_elements(By.TAG_NAME, "button")
                if buttons:
                    print(f"{Fore.GREEN}Consent banner present on the page:{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Number of buttons: {Style.RESET_ALL}{Fore.CYAN}{len(buttons)}{Style.RESET_ALL}")

                    button_texts = [button.text for button in buttons]

                    if "Manage Cookies" in button_texts:
                        button_type = "Type1 (Manage Cookies)"
                    if "OK" in button_texts or "Okay" in button_texts:
                        if button_type == "Type1 (Manage Cookies)":
                            button_type = "Type2 (Both)"
                        else:
                            button_type = "Type1 (Okay)"

                break

            except TimeoutException:
                continue

    cookie_names = [
        'osano_consentmanager',
        'osano_consentmanager_uuid',
        'visitor_id395202-hash',
        's_cc',
        'notice_behavior',
        'mbox',
        'ln_or',
        'linq_auth_redirect_addr',
        'at_check',
        '_gid',
        '_gcl_au',
        '_ga',
        'AWSALBCORS',
        'AWSALB',
        'AMCV_7205F0F5559E57A87F000101%40AdobeOrg',
        'JSESSIONID',
        'oktaStateToken',
        'DT',
        'g_state',
        'G_ENABLED_IDPS'
    ]

    cookies = driver.get_cookies()
    cookie_data = []       

    for cookie in cookies:
        if cookie['name'] in cookie_names:
            print(f"{Fore.GREEN}Cookie Name: {Style.RESET_ALL}{Fore.CYAN}{cookie['name']}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Domain: {Style.RESET_ALL}{Fore.CYAN}{cookie['domain']}{Style.RESET_ALL}")
            expiry_timestamp = get_cookie_expiry(cookie)
            expiry_formatted = format_expiry(expiry_timestamp)
            print(f"{Fore.GREEN}Expires: {Style.RESET_ALL}{Fore.CYAN}{expiry_formatted}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Secure: {Style.RESET_ALL}{Fore.CYAN}{cookie['secure']}{Style.RESET_ALL}")

            banner_present = check_and_report_banner(driver)

            ccm_implemented = "Yes" if trustarc_present or osano_present else "No"
            num_buttons = len(buttons) if banner_present else 0
            consent_banner = "Yes" if banner_present else "No"
            provider = "TrustArc" if trustarc_present else "Osano" if osano_present else "None"
            pop_up_working = "Yes" if trustarc_present or osano_present else "No"

            duration = calculate_cookie_duration(expiry_timestamp)
            if duration is not None:
                duration_str = str(duration)
                print(f"{Fore.GREEN}Time until expiry: {Style.RESET_ALL}{Fore.CYAN}{duration_str}{Style.RESET_ALL}")

                cookie_data.append({
                    "name": cookie['name'],
                    "domain": cookie['domain'],
                    "expiry": expiry_formatted,
                    "secure": cookie['secure'],
                    "ccmImplemented": ccm_implemented,
                    "consentBanner": consent_banner,
                    "provider": provider,
                    "popUpWorking": pop_up_working,
                    "buttonType": button_type,
                    "manageCookiesLink": manage_cookies_link,
                    "Duration": duration if duration is not None else "Session Cookie (no explicit expiry)"
                })

    driver.quit()

    return cookie_data
