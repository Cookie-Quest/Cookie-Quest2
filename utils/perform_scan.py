import requests
import time

def perform_scan():
    try:
        # Schedule the scan_cookies_route every 150 seconds (2.5 minutes)
        response = requests.get('http://127.0.0.1:5000/scan_cookies')  # Update the port if needed
        if response.status_code == 200:
            cookies = response.json()['cookies']
            # Process the cookies data as needed
            print(f'Scanned at {time.ctime()} - Cookies: {cookies}')
        else:
            print(f"An error occurred: {response.status_code}", response.status_code)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
