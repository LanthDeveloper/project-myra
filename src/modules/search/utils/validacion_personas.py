from datetime import datetime
from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv
from modules.search.utils.consulta_ruc import procesar_df_rucs
from modules.search.utils.consulta_reinfo import agregar_codigo_unico_al_df

load_dotenv()  # Cargar variables de entorno si no se han cargado aún

BASE_DIR = Path(__file__).resolve().parents[4]  # project-myra-backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000")

async def validacion_total(excel_path):
    df = pd.read_excel(excel_path)

    # Procesamiento de RUCs
    df1 = await procesar_df_rucs(df, columna_ruc="ruc")

    # Validar si existe función correctamente
    try:
        test = pd.DataFrame({"ruc": ["10000000001"]})
        await agregar_codigo_unico_al_df(test)
        print("✅ Función agregar_codigo_unico_al_df disponible")
    except KeyError:
        print("⚠️ Las columnas 'actividad_economica' y 'alerta' no existen en el DataFrame.")
    
    df2 = await agregar_codigo_unico_al_df(df1)

    # Preparar ruta del archivo RECPO del mes
    nombre_archivo_recpo = f"recpo_{datetime.now().strftime('%Y-%m')}.xlsx"
    ruta_archivo_recpo = Path(__file__).resolve().parent / nombre_archivo_recpo

    # Leer archivo RECPO si existe
    if ruta_archivo_recpo.exists():
        df_recpo = pd.read_excel(ruta_archivo_recpo)
        print("✅ recpo cargado correctamente")
    else:
        print(f"⚠️ El archivo '{ruta_archivo_recpo}' no existe.")
        df_recpo = pd.DataFrame()

    df_recpo["ruc"] = df_recpo["ruc"].astype(str)
    df2["ruc"] = df2["ruc"].astype(str)
    df3 = df2.merge(df_recpo[["ruc", "N° Registro"]], on="ruc", how="left")
    df3 = df3.rename(columns={"N° Registro": "Registro RECPO"})
    df3["Registro RECPO"] = df3["Registro RECPO"].fillna("⚠️ No tiene RECPO")

    # Guardar Excel resultante en carpeta public del proyecto raíz
    carpeta_salida = BASE_DIR / "public"
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_excel_salida = carpeta_salida / "veta_test_procesado.xlsx"
    df3.to_excel(ruta_excel_salida, index=False)
    print(f"✅ Archivo guardado en: {ruta_excel_salida}")

    # Convertir columnas clave a string
    for col in ["actividad_economica", "Código Único", "Registro RECPO"]:
        df3[col] = df3[col].astype(str)

    # Aplicar filtros de alerta
    cond1 = ~df3["actividad_economica"].str.contains("MINERA|EXTRACCIÓN", case=False, na=False)
    cond2 = df3["Código Único"].str.strip().isin(["No tiene REINFO", "Error"])
    cond3 = df3["Registro RECPO"].str.contains("No tiene", case=False, na=False)
    cond4 = df3["Código Único"].str.strip() == "Error"

    df_alertas = df3[cond1 | cond2 | cond3 | cond4].drop_duplicates(subset="ruc")

    df_alertas2 = df_alertas.rename(columns={
        "ruc": "ruc",
        "nombre_del_minero": "name",
        "actividad_economica": "economicActivity",
        "Código Único": "uniqueCode",
        "Registro RECPO": "recpo"
    })

    alertas_json = df_alertas2[["ruc", "name", "economicActivity", "uniqueCode", "recpo"]].to_dict(orient="records")

    resultado = {
        "data": alertas_json,
        "url": f"{BACKEND_URL}/static/veta_test_procesado.xlsx"
    }

    print("✅ JSON de alertas críticas generado correctamente")
    return resultado, str(ruta_excel_salida)
