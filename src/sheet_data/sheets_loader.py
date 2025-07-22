import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_row_index(sheet, client_name):
    records = sheet.get_all_values()
    for i, row in enumerate(records[1:], start=2):
        if row and row[0].strip().lower() == client_name.lower():
            return i
    return len(records) + 1


def connect_to_sheet(credentials_path, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet


def update_client_data(credentials_path, sheet_name, client_name, tax_id=None,
                       ventas_arca=None, compras_arca=None):
    sheet = connect_to_sheet(credentials_path, sheet_name)
    row_index = get_row_index(sheet, client_name)

    if tax_id:
        sheet.update_acell(f"B{row_index}", tax_id)

    if compras_arca is not None:
        sheet.update_acell(f"D{row_index}", compras_arca)

    if ventas_arca is not None:
        sheet.update_acell(f"I{row_index}", ventas_arca)

def obtener_clientes_iva(sheet_name="Automatizacion de IVA") -> list:
    """
    Lee la hoja 'Automatización de IVA' y devuelve una lista de dicts con cliente y CUIT.

    Returns:
        list: [{'cliente': str, 'cuit': str}, ...]
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).sheet1  # Asegurate que apunta a la hoja correcta
    registros = sheet.get_all_records()

    clientes = []
    for fila in registros:
        nombre = fila.get("Cliente")
        cuit = fila.get("CUIT")
        if nombre and cuit:
            clientes.append({
                "cliente": str(nombre).strip(),
                "cuit": str(cuit).strip()
            })


    return clientes

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def actualizar_totales_holistor(cliente: str, compras: float, ventas: float, sheet_name="Automatizacion de IVA"):
    """
    Actualiza los campos de Compras y Ventas Holistor para el cliente dado.

    Args:
        cliente (str): Nombre del cliente (debe coincidir con la columna A)
        compras (float): Total de compras Holistor
        ventas (float): Total de ventas Holistor
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).sheet1
    valores = sheet.get_all_values()
    
    def _to_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    compras = _to_float(compras)
    ventas = _to_float(ventas)

    for idx, fila in enumerate(valores[1:], start=2):  # Saltear encabezado, comienza en fila 2
        nombre_fila = fila[0].strip().lower()
        if nombre_fila == cliente.strip().lower():
            # Columna C = índice 3 (compras), Columna H = índice 8 (ventas)
            sheet.update_cell(idx, 3, round(compras, 2))
            sheet.update_cell(idx, 8, round(ventas, 2))
            print(f"✅ Totales Holistor actualizados para {cliente}")
            return

    print(f"⚠️ Cliente '{cliente}' no encontrado en hoja de cálculo.")
