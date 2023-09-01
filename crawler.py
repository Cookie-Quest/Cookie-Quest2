from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import datetime
import xlsxwriter

workbook = xlsxwriter.Workbook('Crawler_SpreedSheet.xlsx')

# import csv

# # Define the CSV file path
# csv_file_path = "crawler_csv"
# data = {'page title': [], 'Cookie Name': [], 'Domain': [], 'Expires': [], 'Secure': []}
# printed_info = []

# Function to format the expiry timestamp
def format_expiry(expiry_timestamp):
    if expiry_timestamp:
        expiry_datetime = datetime.datetime.fromtimestamp(expiry_timestamp)
        return expiry_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return "N/A"

<<<<<<< HEAD


def check_and_report_banner(driver):
    banner_ids = ["truste-consent-track", "osano-cm-manage osano-cm-buttons__button osano-cm-button osano-co-button --type_manage", 
                  "osano-cm-window__dialog osano-cm-dialog osano-cm-dialog--position_bottom osano-cm-dialog--type_bar"]
    
    # class_ids = ["osano-cm-dialog__content osano-cm-content"]

=======
# Function to check and report banners
def check_and_report_banner(driver):
    banner_ids = ["truste-consent-track", "osano-cm-manage osano-cm-buttons__button osano-cm-button osano-co-button --type_manage"]
    banner_info = []
>>>>>>> 1217596641e8ce81011114fc81a65a4fa3be19c8
    for banner_id in banner_ids:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, banner_id)))
            consent_banner_div = driver.find_element(By.ID, banner_id)
            buttons = consent_banner_div.find_elements(By.TAG_NAME, "button")
            div_elements = consent_banner_div.find_elements(By.CSS_SELECTOR, 'osano-cm-dialog__content osano-cm-content')


            # class_name = consent_banner_div.find_elements(By.CLASS_NAME, "osano-cm-dialog__content osano-cm-content")
            
            if buttons:
                banner_info.append(f"Consent banner with ID '{banner_id}' is present on the page:")
                banner_info.append(f"Number of buttons: {len(buttons)}")
                for idx, button in enumerate(buttons, start=1):
<<<<<<< HEAD
                    print(f"Button {idx} text: {button.text}")

            if div_elements:
                print(f"div elements found with banner '{banner_id}':")
                for idx, div_elements in enumerate(div_elements, start=1):
                    print(f"Div element {idx} text: {div_elements.text}")
               
                
=======
                    banner_info.append(f"Button {idx} text: {button.text}")
>>>>>>> 1217596641e8ce81011114fc81a65a4fa3be19c8
            else:
                banner_info.append(f"No buttons found in the consent banner with ID '{banner_id}'.")
        except TimeoutException:
            continue
    return banner_info

# Function to scan a website
def scan_website(website_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service('./driver/chromedriver.exe')  # Adjust the path to your chromedriver.exe
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print(f"Scanned website: {website_url}")
    driver.get(website_url)
    printed_info.append(f"Scanned website: {website_url}")
    printed_info.append(f"Page title: {driver.title}")

    cookie_names = [
        'osano_consentmanager',
        'osano_consentmanager_uuid',
        'TrustArc',
        'JSESSIONID'
    ]

    cookies = driver.get_cookies()

    for cookie in cookies:
        if cookie['name'] in cookie_names:
            data['page title'].append(driver.title)  # Store the page title
            data['Cookie Name'].append(cookie['name'])
            data['Domain'].append(cookie['domain'])
            data['Expires'].append(format_expiry(cookie['expiry']))
            data['Secure'].append(cookie['secure'])
            printed_info.append(f"Cookie Name: {cookie['name']}")
            printed_info.append(f"Domain: {cookie['domain']}")
            printed_info.append(f"Expires: {format_expiry(cookie['expiry'])}")
            printed_info.append(f"Secure: {cookie['secure']}")
            printed_info.append("-----")

    # Check for consent banners
    banner_info = check_and_report_banner(driver)
    if not banner_info:
        printed_info.append("No consent banners found on the page.")
    else:
        printed_info.extend(banner_info)

    driver.quit()

# Main function
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

    # Loop through the website URLs
    for url in website_urls:
        scan_website(url)
    print("Script execution finished")

worksheet = workbook.add_worksheet()
 
# Use the worksheet object to write
# data via the write() method.
worksheet.write('A1', 'Hello..')
worksheet.write('B1', 'Geeks')
worksheet.write('C1', 'For')
worksheet.write('D1', 'Geeks')
 
# Finally, close the Excel file
# via the close() method.
workbook.close()


 
# Finally, close the Excel file
# via the close() method.

    # # Write printed information to a CSV file
    # with open(csv_file_path + "_printed_info.csv", mode="w", newline="", encoding="utf-8") as file:
    #     writer = csv.writer(file)
    #     for info in printed_info:
    #         writer.writerow([info])

    # # Write parsed data to a CSV file
    # with open(csv_file_path + ".csv", mode="w", newline="", encoding="utf-8") as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['Page Title', 'Cookie Name', 'Domain', 'Expires', 'Secure'])  # Header row
    #     for i in range(len(data['page title'])):
    #         writer.writerow([
    #             data['page title'][i],
    #             data['Cookie Name'][i],
    #             data['Domain'][i],
    #             data['Expires'][i],
    #             data['Secure'][i]
    #         ])

    # # Print success message
    # print(f"CSV files '{csv_file_path}.csv' and '{csv_file_path}_printed_info.csv' have been created.")

if __name__ == "__main__":
    main()
