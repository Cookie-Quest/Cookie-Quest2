# website_manager.py

# List to store the websites to be scanned
website_urls = []

def add_website_to_scan(website_url):
    website_urls.append(website_url)

def get_website_list():
    return website_urls
