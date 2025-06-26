import pandas as pd
import os

def clean_amount(value):
    if pd.isna(value):
        return None
    value = str(value).strip().replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None

def sum_total_from_csv(file_path, tipo):

    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return "Archivo no encontrado"

    try:
        df = pd.read_csv(file_path, dtype=str, encoding="utf-8", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip()

        total_col = "Importe Total"
        tipo_col = "Tipo de Comprobante"

        if total_col not in df.columns or tipo_col not in df.columns:
            return "Columnas faltantes"

        df[total_col] = df[total_col].apply(clean_amount)
        df = df.dropna(subset=[total_col, tipo_col])

        total = 0.0
        for _, row in df.iterrows():
            tipo_comp = str(row[tipo_col]).strip()
            amount = row[total_col]

            if tipo == "compras" and tipo_comp in ["6", "8"]:
                continue  # Ignorar Factura B y NC B en compras
            if tipo == "ventas" and tipo_comp in ["3", "13"]:
                total -= amount  # Restar NC A y NC C en ventas
            else:
                total += amount

        return round(total, 2)

    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return f"Error: {e}"
