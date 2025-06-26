# utils/chrome_driver.py
import os
import json
from selenium import webdriver

def create_driver(download_dir):
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-web-security')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")

    # Carpeta de descarga dinámica
    prefs = {
        "download.default_directory": os.path.normpath(download_dir),
        "savefile.default_directory": os.path.normpath(download_dir),
        "profile.default_content_setting_values.automatic_downloads": 1,
        "safebrowsing.enabled": True
    }

    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.get("https://auth.afip.gob.ar/contribuyente_/login.xhtml")
    return driver
