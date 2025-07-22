from run_pipeline import run_iva_pipeline
from sheet_data.sheets_loader import obtener_clientes_iva

def main():
    clientes = obtener_clientes_iva()
    for cliente in clientes:
        nombre = cliente["cliente"]
        print("\n==============================")
        print(f"🔍 Procesando cliente: {nombre}")
        try:
            run_iva_pipeline(nombre)
            print(f"✅ Finalizado: {nombre}")
        except Exception as e:
            print(f"❌ Error procesando {nombre}: {e}")
            print("⏭️ Continuando con el siguiente cliente...")

if __name__ == "__main__":
    main()