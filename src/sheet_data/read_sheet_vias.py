#read_sheet_vias.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.exceptions import GoogleAuthError
from googleapiclient.errors import HttpError
from tkinter import messagebox


#Leer datos de hoja de google sheets
def get_vias_from_sheets():
    #Api spreadsheets
    SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
    #Ruta del archivo con las credenciales
    KEY = 'keys.json'
    #ID del documento de Google Sheets
    SPREADSHEET_ID = '1KGTgVWHIq5zkx50kuhrwFWpU2yvjUaz_b6KhPlFEF-c'

    try:
        creds = service_account.Credentials.from_service_account_file(KEY, scopes= SCOPE)
        service = build('sheets' , 'v4', credentials= creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId= SPREADSHEET_ID, range='holistor_db!A2:B').execute()
        values = result.get('values', [])
        
        #Busqueda de datos
        if values:
            #Almaceno los clientes en una lista
            clients_vias = [{'name': row[0], 'via': row[1]} for row in values]
            return clients_vias
            
        else: 
            messagebox.showerror('Error', 'No se encontraron datos en la hoja de Google Sheets')
            return []
    #Excepcion para manejo de errores varios
    except GoogleAuthError as auth_error:
        messagebox.showerror('Error de autenticacion', str(auth_error))
        return []
    except HttpError as http_error:
        messagebox.showerror('Error HTTP', str(http_error))
        return []
    except Exception as e:
        messagebox.showerror('Error inesperado', str(e))
        return []
    
def obtener_via_cliente_por_nombre(client_name: str) -> str:
    """
    Busca un cliente en la lista de vías y devuelve su vía.

    Args:
        client_name (str): Nombre del cliente tal como figura en la hoja

    Returns:
        str: Vía asociada o None si no se encuentra
    """
    todas_las_vias = get_vias_from_sheets()
    for item in todas_las_vias:
        if item['name'].strip().lower() == client_name.strip().lower():
            return item['via']
    return None
