# utils/file_handler.py

import os
import zipfile
import time

def unzip_and_rename(download_dir, new_name="archivo_arca.csv", timeout=30):
    zip_file = None

    # Esperar aparición del .zip (que no sea .crdownload)
    for _ in range(timeout):
        files = [f for f in os.listdir(download_dir)
                 if f.endswith(".zip") and not f.endswith(".crdownload")]

        if files:
            files.sort(key=lambda f: os.path.getmtime(os.path.join(download_dir, f)), reverse=True)
            zip_file = os.path.join(download_dir, files[0])
            break

        time.sleep(1)

    if not zip_file or not os.path.exists(zip_file):
        print("⚠️ No se encontró archivo ZIP descargado.")
        return None

    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
            print(f"✅ ZIP extraído: {os.path.basename(zip_file)}")
    except Exception as e:
        print(f"❌ Error al descomprimir {zip_file}: {e}")
        return None

    # Buscar el archivo .csv extraído
    extracted_csv = None
    for f in os.listdir(download_dir):
        if f.endswith(".csv") and "monto" in f.lower():
            extracted_csv = f
            break

    if not extracted_csv:
        print("⚠️ No se encontró archivo CSV para renombrar.")
        return None

    try:
        src_path = os.path.join(download_dir, extracted_csv)
        dst_path = os.path.join(download_dir, new_name)

        if os.path.exists(dst_path):
            os.remove(dst_path)

        os.rename(src_path, dst_path)
        print(f"✅ Archivo CSV renombrado como: {new_name}")
        return dst_path
    except Exception as e:
        print(f"❌ Error al renombrar archivo CSV: {e}")
        return None
