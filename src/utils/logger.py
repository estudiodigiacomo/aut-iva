import os

def crear_logger_cliente(output_folder: str):
    log_lines = []

    def log(msg: str):
        print(msg)
        log_lines.append(msg)

    def guardar(nombre_archivo="log_holistor.txt"):
        path = os.path.join(output_folder, nombre_archivo)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))

    return log, guardar