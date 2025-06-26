from arca.portal_iva import portal_iva
from sheet_data.sheets_loader import obtener_clientes_iva, actualizar_totales_holistor
from sheet_data.read_sheet_vias import obtener_via_cliente_por_nombre
from utils.folder_manager import folders_report
from holsitor.dbf_a_excel import convertir_dbf_a_excel
from utils.logger import crear_logger_cliente
from holsitor.process_holistor_data import (
    calcular_total_ventas_desde_excel,
    calcular_total_compras_desde_excel
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def run_iva_pipeline(client_name: str):
    print(f"\n Iniciando pipeline de IVA para: {client_name}")
    portal_iva(client_name)
    procesar_holistor_para_cliente(client_name)
    calcular_y_cargar_margenes(client_name)

def procesar_holistor_para_cliente(client_name: str):
    print(f"\n🔄 Procesando Holistor para: {client_name}")

    via = obtener_via_cliente_por_nombre(client_name)
    if not via:
        print(f"❌ Vía no encontrada para el cliente {client_name}")
        return

    output_folder = folders_report(client_name)
    if not output_folder:
        print(f"❌ No se pudo crear carpeta de emisión para {client_name}")
        return

    log, guardar_log = crear_logger_cliente(output_folder)

    ventas_excel = convertir_dbf_a_excel("MOVIVAV.DBF", "Ventas", via, output_folder, client_name)
    compras_excel = convertir_dbf_a_excel("MOVIVAC.DBF", "Compras", via, output_folder, client_name)

    if not ventas_excel or not compras_excel:
        log(f"❌ Error en la conversión de archivos DBF a Excel para {client_name}")
        guardar_log()
        return

    log(f"📄 Leyendo archivo de ventas: {ventas_excel}")
    ventas_total = calcular_total_ventas_desde_excel(ventas_excel, log)

    log(f"📄 Leyendo archivo de compras: {compras_excel}")
    compras_total = calcular_total_compras_desde_excel(compras_excel, log)

    actualizar_totales_holistor(cliente=client_name, compras=compras_total, ventas=ventas_total)

    log(f"✅ Totales Holistor actualizados para {client_name}")
    guardar_log()
    print(f"✅ Holistor finalizado para {client_name}")

def calcular_y_cargar_margenes(cliente: str):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", scope)
        client = gspread.authorize(creds)

        sheet = client.open("Automatizacion de IVA").sheet1
        valores = sheet.get_all_values()

        for idx, fila in enumerate(valores[1:], start=2):  # desde fila 2 (header + datos)
            nombre_fila = fila[0].strip().lower()
            if nombre_fila == cliente.strip().lower():
                try:
                    compras_hol  = float(fila[2].replace(",", ".") or 0)  # C
                    compras_arca = float(fila[3].replace(",", ".") or 0)  # D
                    ventas_hol   = float(fila[7].replace(",", ".") or 0)  # H
                    ventas_arca  = float(fila[8].replace(",", ".") or 0)  # I

                    margen_compras = abs(compras_hol - compras_arca) / compras_arca if compras_arca else 0
                    margen_ventas  = abs(ventas_hol - ventas_arca) / ventas_arca if ventas_arca else 0

                    print(f"📊 Cálculo de márgenes para {cliente}")
                    print(f"🧾 Compras ARCA: {compras_arca}, Holistor: {compras_hol} → Margen: {margen_compras:.2%}")
                    print(f"🧾 Ventas ARCA: {ventas_arca}, Holistor: {ventas_hol} → Margen: {margen_ventas:.2%}")

                    sheet.update_cell(idx, 5, f"{margen_compras:.2%}")  # Columna E
                    sheet.update_cell(idx, 10, f"{margen_ventas:.2%}")  # Columna J

                     # Comentarios de informe
                    sheet.update_cell(idx, 6, "CARGA MANUAL")  # Columna F - Informe compras
                    sheet.update_cell(idx, 11, "CARGA MANUAL") # Columna K - Informe ventas

                    print(f"✅ Márgenes cargados para {cliente}")
                except Exception as e:
                    print(f"⚠️ Error al calcular márgenes para {cliente}: {e}")
                return

        print(f"⚠️ Cliente '{cliente}' no encontrado en la hoja.")

    except Exception as err:
        import traceback
        print("❌ Error global al calcular márgenes:")
        traceback.print_exc()
