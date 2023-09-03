from flask import Flask, render_template, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from colorama import Fore, Style, Back, init
import datetime, sched
import time
import csv
# Import website_urls from app.py
from app import website_urls

# Use website_urls for crawling websites


init()

app = Flask(__name__)

def format_expiry(expiry_timestamp):
    if expiry_timestamp is not None:
        expiry_datetime = datetime.datetime.fromtimestamp(expiry_timestamp)
        return expiry_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return "Session Cookie (no explicit expiry)"

def get_cookie_expiry(cookie):
    if 'expiry' in cookie:
        return cookie['expiry']
    elif 'expires' in cookie:
        return cookie['expires']
    elif 'max_age' in cookie:
        return time.time() + cookie['max_age']
    elif 'Expires / Max-Age' in cookie:
        expires_max_age = cookie['Expires / Max-Age']
        parts = expires_max_age.split('/')
        if len(parts) == 2:
            expires_date_str, max_age_str = parts
            expires_date = datetime.datetime.strptime(expires_date_str.strip(), '%a, %d-%b-%Y %H:%M:%S %Z')
            max_age = int(max_age_str.strip())
            return expires_date.timestamp() + max_age
    return None

def calculate_cookie_duration(expiry_timestamp):
    if expiry_timestamp is not None:
        expiry_datetime = datetime.datetime.fromtimestamp(expiry_timestamp)
        current_datetime = datetime.datetime.now()
        duration = expiry_datetime - current_datetime

        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        duration_formatted = f"{hours}h {minutes}m {seconds}s"
        return duration_formatted

    return "Session Cookie (no explicit expiry)"

def check_and_report_banner(driver):
    banner_identifiers = [
        ("ID", "truste-consent-track"),
        ("CLASS_NAME", "osano-cm-dialog__buttons"),
        ("ID", "osano-cm-buttons")  # ID for the second banner
    ]
    
    for identifier_type, identifier_value in banner_identifiers:
        try:
            wait = WebDriverWait(driver, 5)  # Reduced waiting time for efficiency
            
            if identifier_type == "ID":
                wait.until(EC.presence_of_element_located((By.ID, identifier_value)))
            elif identifier_type == "CLASS_NAME":
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, identifier_value)))
            
            consent_banner_div = driver.find_element(getattr(By, identifier_type), identifier_value)
            buttons = consent_banner_div.find_elements(By.TAG_NAME, "button")
            if buttons:
                print(f"{Fore.GREEN}Consent banner present on the page:{Style.RESET_ALL}")
                print(f"{Fore.GREEN}Number of buttons: {Style.RESET_ALL}{Fore.CYAN}{len(buttons)}{Style.RESET_ALL}")
                for idx, button in enumerate(buttons, start=1):
                    print(f"{Fore.GREEN}Button {idx} text: {Style.RESET_ALL}{Fore.CYAN}{button.text}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}No buttons found in the consent banner with {identifier_type} '{identifier_value}'.{Style.RESET_ALL}")
            
        except TimeoutException:
            continue

    return False

def check_trustarc(driver):
    html = driver.page_source
    return "truste" in html

# def check_manage_cookies_link(driver):
#         try:
#             manage_cookies_link_xpath = "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'manage cookies')]"

#             manage_cookies_link = driver.find_element(By.XPATH, manage_cookies_link_xpath)

#             if manage_cookies_link.is_enabled():
#                 print(f"{Fore.GREEN}{Back.WHITE}Manage Cookies link found and is clickable.{Style.RESET_ALL}")
#                 driver.execute_script("arguments[0].click();", manage_cookies_link)
#                 return True
#             else:
#                 print(f"{Fore.RED}{Back.WHITE}Manage Cookies link found but is not clickable.{Style.RESET_ALL}")

#         except NoSuchElementException:
#             print(f"{Fore.RED}{Back.WHITE}No 'Manage Cookies' link found.{Style.RESET_ALL}")

#         return False

# Define a custom function to find an element with multiple XPaths
def find_element_with_multiple_xpaths(driver, xpaths):
    for xpath in xpaths:
        try:
            element = driver.find_element(By.XPATH, xpath)
            return element
        except NoSuchElementException:
            continue
    return None
def detect_manage_cookies_link(footer_text):
    # Define a list of possible translations for "Manage Cookies" in different languages
    translations = [
        "Manage Cookies",
        "Beheer cookies",  # Dutch
        "Gérer les cookies",  # French
        "Gestione dei cookie",  # Italian
        "Gestión de cookies",  # Spanish
        "Verwalten von Cookies",  # German
        # Add more translations for other languages as needed
    ]

    for translation in translations:
        if translation in footer_text:
            return translation

    return None  # Return None if no translation is found


# Modify the get_footer_details function to use this custom function
def get_footer_details(driver):
    try:
        # Define multiple possible XPath expressions for the footer element
        xpaths_to_try = [
            '//footer[@id="footer"]',
            '/html/body/footer',
            '//html/body/app-root',
            '//html/body/div/div/div/div/footer',
            '//html/body/div/div/p/footer',
            '//html/body/div/div/p/footer',
            '//html/body',
            '//footer[@class="my-footer"]',
            '//html/body/app-root/div'
        ]

        footer_element = find_element_with_multiple_xpaths(driver, xpaths_to_try)

        if footer_element:
            footer_text = footer_element.text

            # Define translations for "Manage Cookies" in various languages
            translations = [
                "Manage Cookies",
                "Beheer cookies",  # Dutch
                "Gérer les cookies",  # French
                "Gestione dei cookie",  # Italian
                "Gestión de cookies",  # Spanish
                "Verwalten von Cookies",  # German
                # Add more translations for other languages as needed
            ]

            # Check if any translation is present in the footer text
            found_translation = False
            for translation in translations:
                if translation.lower() in footer_text.lower():
                    found_translation = True
                   # print(f"{Fore.GREEN}Manage Cookies link is present in the footer.{Style.RESET_ALL}")
                    break

            # Check if "Manage Cookies" link is clickable
            if found_translation:
                manage_cookies_link_xpath = "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'manage cookies')]"
                try:
                    manage_cookies_link = footer_element.find_element(By.XPATH, manage_cookies_link_xpath)
                    if manage_cookies_link.is_enabled():
                        print(f"{Fore.GREEN}{Back.WHITE}Manage Cookies link found and is clickable.{Style.RESET_ALL}")
                        return "Yes"  # Return "Yes" when the link is present and clickable
                    else:
                        print(f"{Fore.RED}{Back.WHITE}Manage Cookies link found but is not clickable.{Style.RESET_ALL}")
                except NoSuchElementException:
                    print(f"{Fore.RED}{Back.WHITE}Manage Cookies link not found in the footer.{Style.RESET_ALL}")

            else:
                print(f"{Fore.RED}Manage Cookies link not found in the footer.{Style.RESET_ALL}")

        else:
            print(f"{Fore.RED}Footer element not found using any of the provided XPath expressions.{Style.RESET_ALL}")

    except NoSuchElementException:
        print(f"{Fore.RED}No footer found on the page.{Style.RESET_ALL}")

    return "No"  # Return "No" when the link is not found or not clickable



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
        
    # Get the status of "Manage Cookies" link from get_footer_details(driver)
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
    cookie_data = []       #This will be extracted into a PD DF to export as excel spreadsheet

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
                    "manageCookiesLink": manage_cookies_link,  # Include "Manage Cookies" link status
                    "Duration": duration if duration is not None else "Session Cookie (no explicit expiry)"
                })

    driver.quit()

    return cookie_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan_cookies')
def scan_cookies():
    
    website_urls = [

         'https://ironwoodins.com/',
        # 'https://www.linqbymarsh.com/linq/auth/login',
        # 'https://icip.marshpm.com/FedExWeb/login.action',
        # 'https://www.marsh.com/us/home.html',
        #  'https://www.marsh.com/us/insights/risk-in-context.html',
        #  'https://www.dovetailexchange.com/Account/Login',
        # 'https://www.victorinsurance.com/us/en',
        #  'https://www.victorinsurance.it',
        #  'https://www.victorinsurance.nl',
        #  'https://www.marshunderwritingsubmissioncenter.com',
        #  'https://victorinsurance.nl/verzekeraars, 
        
        #---------Other Websites-------------
        'https://www.afsretirementedge.com/',
         'https://www.aga-us.com/',     
        # 'https://www.afsretirementedge.com/',
        # 'https://afriskservices.co.za'

        # 'https://ironwoodins.com/', #osano
        #  'https://www.linqbymarsh.com/linq/auth/login', #trustarc
        #  'https://www.marsh.com/us/home.html', #  trustarc
        # 'https://www.marsh.com/us/insights/risk-in-context.html', #trustarc
        # 'https://www.victorinsurance.com/us/en.html', # trustarc
        # 'https://www.victorinsurance.it', #osano
        #  'https://www.victorinsurance.nl',
        #  'https://icip.marshpm.com/FedExWeb/login.action',
        #  'https://www.dovetailexchange.com/Account/Login',
        #  'https://www.marshunderwritingsubmissioncenter.com',
        #  'https://victorinsurance.nl/verzekeraars'

    ]

    banner_identifiers = [
        ("ID", "truste-consent-track"),
        ("CLASS_NAME", "osano-cm-dialog__buttons"),
        ("ID", "osano-cm-buttons")
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

    return jsonify({"cookies": cookie_data, "csv_filename": csv_filename})






if __name__ == "__main__":
    app.run(debug=True)

# s = sched.scheduler(time.time, time.sleep)
# def run_script(sc):
#     # print("Running scheduled scan...")
#     s.enter(150, 1, run_script, (sc,))
# if __name__ == "__main__":
#     s.enter(0, 1, run_script, (s,))
#     s.run()


@app.route('/download_excel')
def download_excel():
    try:
        # Replace with the actual path to your Excel file
        excel_file_path = "Capstone Excel report format.xls"
        return send_file(excel_file_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {str(e)}"



# @app.route('/download_excel')
# def download_excel():
#     try:
#         # Replace with the actual path to your Excel file
#         excel_file_path = "Capstone Excel report format.xlsx"
#         return send_file(excel_file_path, as_attachment=True)
#     except Exception as e:
#         return f"An error occurred: {str(e)}"


