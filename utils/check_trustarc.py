# utils/check_trustarc.py

def check_trustarc(driver):
    html = driver.page_source
    return "truste" in html
