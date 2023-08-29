import requests
from bs4 import BeautifulSoup
import http.cookiejar
import urllib.request
import urllib.error

def scan_cookies(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the <script> tags
    script_tags = soup.findAll('script')

    # Extract the cookie information from the <script> tags
    cookies = []
    for script_tag in script_tags:
        script_url = script_tag.get('src')
        if script_url:
            print(f"Fetching script from URL: {script_url}")
            try:
                cookie_jar = http.cookiejar.CookieJar()
                opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
                urllib.request.install_opener(opener)

                # Send a request
                script_response = urllib.request.urlopen(script_url)
                script_content = script_response.read().decode('utf-8')
                print(f"Script Content: {script_content}")

                # Collect cookies from the cookie jar
                for cookie in cookie_jar:
                    cookies.append((cookie.name, cookie.value))
            except urllib.error.URLError as e:
                print(f"Error fetching script: {e}")

    return cookies

url = 'https://ironwoodins.com/'
cookie_data = scan_cookies(url)
for name, value in cookie_data:
    print(f"Cookie: {name} = {value}")
