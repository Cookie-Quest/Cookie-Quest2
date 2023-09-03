# utils/detect_manage_cookies_link.py

def detect_manage_cookies_link(footer_text):
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

    return None
