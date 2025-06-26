# file: arca/login_arca.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from utils.chrome_driver import create_driver
import json
import logging 

# Configurar logging para este módulo también
logging.basicConfig(filename='iva_automation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')

# Modificamos la firma para que reciba el cuit y password directamente
def login_afip(driver, client_name, cuit, password):
    try:
        driver.get('https://auth.afip.gob.ar/contribuyente_/login.xhtml')
        logging.info(f"Navegando a la página de login de AFIP para {client_name}.")

        cuil_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "F1:username")))
        cuil_field.send_keys(cuit)

        btn_cuil_after = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "F1:btnSiguiente")))
        btn_cuil_after.click()

        password_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "F1:password")))
        password_field.send_keys(password)

        btn_get_into = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "F1:btnIngresar")))
        btn_get_into.click()

        return driver

    except Exception as e:
        logging.error(f"❌ Error inesperado durante el login de AFIP para {client_name}: {e}", exc_info=True)
        if driver:
            driver.quit()
        return None
