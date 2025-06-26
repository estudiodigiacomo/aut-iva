from run_pipeline import run_iva_pipeline
from sheet_data.sheets_loader import obtener_clientes_iva

def main():
    try:
        clientes = obtener_clientes_iva()
        for cliente in clientes:
            nombre = cliente["cliente"]
            print(f"\n==============================")
            print(f"🔍 Procesando cliente: {nombre}")
            run_iva_pipeline(nombre)
            print(f"✅ Finalizado: {nombre}")
    except Exception as e:
        print(f"❌ Error general en la ejecución del pipeline: {e}")

if __name__ == "__main__":
    main()