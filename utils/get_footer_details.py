# utils/get_footer_details.py
from utils.find_element_with_multiple_xpaths import find_element_with_multiple_xpaths
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from colorama import Fore, Style, Back, init

def get_footer_details(driver):
    try:
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

            translations = [
                "Manage Cookies",
                "Beheer cookies",  # Dutch
                "Gérer les cookies",  # French
                "Gestione dei cookie",  # Italian
                "Gestión de cookies",  # Spanish
                "Verwalten von Cookies",  # German
                # Add more translations for other languages as needed
            ]

            found_translation = False
            for translation in translations:
                if translation.lower() in footer_text.lower():
                    found_translation = True
                    break

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
