import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_login_credentials(credentials_path, sheet_name, client_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).worksheet("aut-sheets")
    rows = sheet.get_all_values()

    for row in rows[1:]:  # omitir encabezado
        if len(row) >= 3 and row[0].strip().lower() == client_name.strip().lower():
            return {
                "cuit": row[1].strip(),
                "password": row[2].strip()
            }

    raise ValueError(f"Cliente '{client_name}' no encontrado en la hoja '{sheet_name}'")
