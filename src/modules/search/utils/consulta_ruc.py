# src/modules/search/utils/consulta_ruc.py 
import asyncio
import random
import re
from bs4 import BeautifulSoup
import pandas as pd
from playwright.async_api import async_playwright

PALABRAS_MINERIA = ["mineral", "minería", "extracción", "comercialización de minerales"]

def actividad_es_mineria(actividad: str) -> bool:
    return any(p in actividad.lower() for p in PALABRAS_MINERIA)

async def consultar_ruc_sunat(ruc: str, reintentos=3) -> dict:
    ruc = str(int(float(ruc)))  # asegurar formato limpio

    for intento in range(1, reintentos + 1):
        browser = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                    locale="es-PE"
                )
                page = await context.new_page()

                print(f"🌐 Intento {intento}: Navegando a SUNAT para RUC {ruc}")
                await page.goto("https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp", timeout=20000)

                # Usamos el frame por si aún existe, pero validamos también si está directamente en la página
                frame = page.frame(name="main") or page.main_frame

                # Esperar el input y botón
                await frame.wait_for_selector("#txtRuc", timeout=10000)
                await frame.fill("#txtRuc", ruc)
                await asyncio.sleep(random.uniform(1, 2))
                await frame.click("#btnAceptar")

                # Esperar carga de resultado
                await page.wait_for_url("**/jcrS00Alias", timeout=15000)
                await page.wait_for_selector(".panel.panel-primary", timeout=10000)

                # Extraer HTML y parsear
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                actividades = [
                    td.text.strip()
                    for td in soup.select("td")
                    if re.search(r'(Principal|Secundaria)\s*-\s*\d{4}', td.text)
                ]
                actividad_str = "; ".join(actividades)
                alerta = "Normal" if actividad_es_mineria(actividad_str) else "⚠️ Actividad no minera"

                print(f"✅ Actividad económica detectada: {actividad_str[:60]}...")

                return {
                    "ruc": ruc,
                    "actividad_economica": actividad_str or "No encontrado",
                    "alerta": alerta
                }

        except Exception as e:
            print(f"❌ Error en intento {intento} para RUC {ruc}: {e}")
            await asyncio.sleep(random.uniform(5, 10))  # evitar bloqueo

        finally:
            if browser:
                await browser.close()

    return {
        "ruc": ruc,
        "actividad_economica": "Error",
        "alerta": f"❌ No se pudo consultar tras {reintentos} intentos"
    }

async def procesar_df_rucs(df: pd.DataFrame, columna_ruc="ruc") -> pd.DataFrame:
    resultados = []
    df_2 = df.drop_duplicates(subset=[columna_ruc], keep="first")
    
    for ruc in df_2[columna_ruc].dropna().astype(str).unique():
        resultado = await consultar_ruc_sunat(ruc)
        resultados.append(resultado)
        await asyncio.sleep(random.uniform(1, 1.5))
    
    print(resultados)
    df_resultados = pd.DataFrame(resultados)
    df[columna_ruc] = df[columna_ruc].astype(str)
    df_resultados[columna_ruc] = df_resultados[columna_ruc].astype(str)
    df_final = df.merge(df_resultados, on=columna_ruc, how='left')
    
    return df_final
