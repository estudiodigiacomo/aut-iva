import pandas as pd
from datetime import datetime, timedelta

def calcular_total_compras_desde_excel(path_excel: str, log=print) -> float:
    try:
        log(f"\n📄 Leyendo archivo de compras: {path_excel}")
        df = pd.read_excel(path_excel, dtype=str).fillna("")

        log(f"🧾 Columnas detectadas: {list(df.columns)}")

        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)
        fechas_invalidas = df["FECHA"].isna().sum()
        log(f"⚠️ Fechas no válidas al parsear: {fechas_invalidas}")

        df["TOT_FAC"] = pd.to_numeric(df["TOT_FAC"], errors="coerce")

        hoy = datetime.today()
        primer_dia_mes_anterior = datetime(hoy.year, hoy.month, 1) - timedelta(days=1)
        mes_anterior = primer_dia_mes_anterior.month
        anio_anterior = primer_dia_mes_anterior.year

        df_periodo = df[
            (df["FECHA"].dt.month == mes_anterior) &
            (df["FECHA"].dt.year == anio_anterior)
        ]

        log(f"🔢 Filas totales: {len(df)}")
        log(f"📅 Filas del período {mes_anterior}-{anio_anterior}: {len(df_periodo)}")

        excluidos = df_periodo[(df_periodo["TIPO"] == "B") & (df_periodo["T_MOV"].isin(["F", "NC"]))]
        for _, row in excluidos.iterrows():
            log(f"❌ Excluido (compras): TIPO={row['TIPO']}, T_MOV={row['T_MOV']}, $ {row['TOT_FAC']}")

        df_filtrado = df_periodo.drop(excluidos.index)

        total = df_filtrado["TOT_FAC"].sum()
        log(f"💰 Total compras: {total}")
        return round(total, 2)

    except Exception as e:
        log(f"❌ Error al calcular compras desde {path_excel}: {e}")
        return 0.0

def calcular_total_ventas_desde_excel(path_excel: str, log=print) -> float:
    try:
        log(f"\n📄 Leyendo archivo de ventas: {path_excel}")
        df = pd.read_excel(path_excel, dtype=str).fillna("")

        log(f"🧾 Columnas detectadas: {list(df.columns)}")

        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)
        fechas_invalidas = df["FECHA"].isna().sum()
        log(f"⚠️ Fechas no válidas al parsear: {fechas_invalidas}")

        df["TOT_FAC"] = pd.to_numeric(df["TOT_FAC"], errors="coerce")

        hoy = datetime.today()
        primer_dia_mes_anterior = datetime(hoy.year, hoy.month, 1) - timedelta(days=1)
        mes_anterior = primer_dia_mes_anterior.month
        anio_anterior = primer_dia_mes_anterior.year

        df_filtrado = df[
            (df["FECHA"].dt.month == mes_anterior) &
            (df["FECHA"].dt.year == anio_anterior)
        ]

        log(f"🔢 Filas totales: {len(df)}")
        log(f"📅 Filas del período {mes_anterior}-{anio_anterior}: {len(df_filtrado)}")

        total = 0.0
        for _, row in df_filtrado.iterrows():
            tipo = row.get("TIPO", "")
            t_mov = row.get("T_MOV", "")
            importe = row.get("TOT_FAC", 0)

            if pd.isna(importe):
                log(f"⚠️ Importe inválido: {importe} (tipo {tipo}, mov {t_mov})")
                continue

            if t_mov == "NC" and tipo in ["A", "C"]:
                log(f"➖ Nota de Crédito restada: {importe} (tipo {tipo})")
                total -= importe
            else:
                log(f"➕ Suma: {importe} (tipo {tipo}, mov {t_mov})")
                total += importe

        log(f"💰 Total ventas: {total}")
        return round(total, 2)

    except Exception as e:
        log(f"❌ Error al calcular ventas desde {path_excel}: {e}")
        return 0.0
