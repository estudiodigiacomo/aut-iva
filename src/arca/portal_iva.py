from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from utils.folder_manager import folders_report
from utils.chrome_driver import create_driver
from arca.login_arca import login_afip
from sheet_data.login_sheet_reader import get_login_credentials
from sheet_data.sheets_loader import update_client_data
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import time
from utils.file_handler import unzip_and_rename
from data_processor import sum_total_from_csv
import os

def get_month_name(month_number):
    months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
              "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    return months[month_number - 1]

def portal_iva(client_name):
    credentials_path = "keys.json"
    iva_sheet_name = "Automatizacion de IVA"
    auth_sheet_name = "DB_AUT"

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open(iva_sheet_name).sheet1
    rows = sheet.get_all_values()

    headers = rows[0]
    cliente_idx = headers.index("Cliente")
    cuit_idx = headers.index("CUIT")

    row = next((r for r in rows[1:] if r[cliente_idx] == client_name), None)
    if not row:
        print(f"No se encontró al cliente {client_name} en la hoja.")
        return

    cuit = row[cuit_idx]

    try:
        print(f"Procesando cliente: {client_name}")
        download_path = folders_report(client_name)
        driver = create_driver(download_path)

        creds_dict = get_login_credentials(credentials_path, auth_sheet_name, client_name)
        password = creds_dict["password"]

        driver = login_afip(driver, client_name, cuit, password)
        print(f"Login exitoso para {client_name}")

        input_search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "buscadorInput")))
        input_search.send_keys('Portal IVA')
        time.sleep(2)

        portal_iva_item = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "rbt-menu-item-0")))
        portal_iva_item.click()

        original_window = driver.current_window_handle
        WebDriverWait(driver, 10).until(EC.new_window_is_opened([original_window]))
        new_window = [w for w in driver.window_handles if w != original_window][0]
        driver.switch_to.window(original_window)
        driver.close()
        driver.switch_to.window(new_window)

        ingresar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Sin texto (iva.home.btn.nueva.declaracion.alt)']"))
        )
        ingresar_btn.click()

        # Nuevo bloque robusto para seleccionar el período
        today = datetime.today()
        first_day_this_month = today.replace(day=1)
        last_month = first_day_this_month - timedelta(days=1)
        mes = last_month.month
        anio = last_month.year
        mes_str = f"{mes:02d}"
        anio_str = str(anio)

        dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "periodo")))
        select = Select(dropdown)

        found = False
        for option in select.options:
            text = option.text.lower()
            value = option.get_attribute("value")
            if (mes_str in text or mes_str in value or get_month_name(mes).lower() in text) and anio_str in text:
                select.select_by_visible_text(option.text)
                print(f"✅ Período seleccionado: {option.text}")
                found = True
                break

        if not found:
            print(f"❌ El período {mes_str}/{anio_str} no está disponible en el selector.")
            return

        continuar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Sin texto (iva.btn.home.validar.periodo.alt)']"))
        )
        continuar_btn.click()

        libro_iva_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Sin texto (iva.btn.home.liva.alt)']"))
        )
        libro_iva_btn.click()

        ventas_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnLibroVentas")))
        ventas_btn.click()

        importar_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnDropdownImportar")))
        importar_dropdown.click()

        importar_arca_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "lnkImportarAFIP")))
        importar_arca_option.click()

        importar_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnImportarAFIPImportar")))
        importar_btn.click()

        cerrar_modal_btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="modalTareas"]/div/div/div[1]/button'))
        )
        cerrar_modal_btn.click()

        csv_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='CSV']]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", csv_btn)
        time.sleep(1)
        ActionChains(driver).move_to_element(csv_btn).click().perform()
        print(" CSV descargado")
        time.sleep(3)
        ventas_path = unzip_and_rename(download_path, new_name="Libro de IVA - Ventas - ARCA.csv")
        ventas_total = sum_total_from_csv(os.path.join(download_path, "Libro de IVA - Ventas - ARCA.csv"), tipo="ventas")

        update_client_data(credentials_path, iva_sheet_name, client_name, tax_id=cuit, ventas_arca=ventas_total)

        libro_compras_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='verCompras.do?t=21' and contains(@class, 'btn-success')]"))
        )
        libro_compras_btn.click()

        importar_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnDropdownImportar")))
        importar_dropdown.click()

        importar_arca_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "lnkImportarAFIP")))
        importar_arca_option.click()

        importar_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnImportarAFIPImportar")))
        importar_btn.click()

        cerrar_modal_btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="modalTareas"]/div/div/div[1]/button'))
        )
        cerrar_modal_btn.click()

        csv_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='CSV']]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", csv_btn)
        time.sleep(1)
        ActionChains(driver).move_to_element(csv_btn).click().perform()
        print(" CSV descargado")
        time.sleep(5)
        compras_path = unzip_and_rename(download_path, new_name="Libro de IVA - Compras - ARCA.csv")
        compras_total = sum_total_from_csv(os.path.join(download_path, "Libro de IVA - Compras - ARCA.csv"), tipo="compras")

        update_client_data(credentials_path, iva_sheet_name, client_name, tax_id=cuit, compras_arca=compras_total)

        time.sleep(5)

    except Exception as e:
        print(f"Error en cliente {client_name}: {e}")
