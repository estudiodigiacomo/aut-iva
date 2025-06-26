# utils/folder_manager.py
import os
import datetime

def folders_report(client_name):
    try:
        client_name_formated = client_name.title()
        date = datetime.datetime.now()
        formatted_folder = date.strftime("%d-%m-%Y")
        folder_clients = r'd:\Clientes'
        folder_client = os.path.join(folder_clients, client_name_formated)
        folder_report = os.path.join(folder_client, 'Liquidacion de IVA Automatizada')
        folder_date_emision = os.path.join(folder_report, f'Emisión {formatted_folder}')

        for path in [folder_clients, folder_client, folder_report, folder_date_emision]:
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"Carpeta creada: {path}")

        return folder_date_emision
    except Exception as e:
        print('❌ Error al crear carpetas:', str(e))
        return None
