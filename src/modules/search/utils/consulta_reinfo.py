import pandas as pd
import io
from playwright.async_api import async_playwright
import asyncio
import time
import random
import logging
from typing import Optional, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReinfoScraper:
    def __init__(self):
        self.browser = None
        self.context = None
        self.CODIGOS_INVALIDOS = {
            "750001619", "10149108", "660000314", "70013606", "70005506", "50009409",
            "10253815", "10125116", "10078012", "10373105", "10419912", "10003298",
            "740001713", "10285912", "10350212", "740002620", "740000513", "10360012",
            "510000809", "740000820", "10077712", "730001119", "50011003", "10391208"
        }

    async def __aenter__(self):
        await self.init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_browser()

    async def init_browser(self):
        logger.info("🚀 Iniciando navegador...")
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--single-process',
                    '--memory-pressure-off',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',
                    '--disable-javascript-harmony-shipping',
                    '--max_old_space_size=4096'
                ]
            )
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Linux; X11; Ubuntu; rv:109.0) Gecko/20100101 Firefox/119.0",
                viewport={"width": 1280, "height": 800},
                locale="es-PE",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "es-PE,es;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Cache-Control": "no-cache"
                }
            )
            await self.context.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}", lambda route: route.abort())
            logger.info("✅ Navegador iniciado correctamente")

    async def close_browser(self):
        logger.info("🛑 Cerrando navegador...")
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        logger.info("✅ Navegador cerrado")

    def calcular_backoff_delay(self, intento: int, base_delay: float = 2.0, max_delay: float = 30.0) -> float:
        exponential_delay = min(base_delay * (2 ** (intento - 1)), max_delay)
        jitter = random.uniform(0.1, 0.3) * exponential_delay
        return exponential_delay + jitter

    async def verificar_conexion_sitio(self, url: str, timeout: int = 5) -> bool:
        try:
            logger.info(f"🌐 Verificando conexión al sitio: {url} (timeout: {timeout}s)")
            page = await self.context.new_page()
            await page.goto(url, timeout=timeout * 1000, wait_until='domcontentloaded')
            content = await page.content()
            logger.debug(f"📄 HTML recibido: {content[:500]}")
            await page.close()
            logger.info("✅ Sitio disponible")
            return True
        except Exception as e:
            logger.warning(f"❌ Sitio no disponible: {e}")
            return False

    async def navegar_con_reintentos(self, page, url: str, max_nav_intentos: int = 3):
        for nav_intento in range(max_nav_intentos):
            try:
                logger.info(f"🧭 Navegando (intento {nav_intento + 1}) a {url}")
                if nav_intento == 0:
                    await page.goto(url, wait_until='domcontentloaded', timeout=20000)
                elif nav_intento == 1:
                    await page.goto(url, wait_until='networkidle', timeout=25000)
                else:
                    await page.goto(url, wait_until='load', timeout=30000)
                logger.info("✅ Navegación completada")
                return
            except Exception as e:
                logger.warning(f"⚠️ Error en navegación (intento {nav_intento + 1}): {e}")
                if nav_intento < max_nav_intentos - 1:
                    await asyncio.sleep(2)
                else:
                    raise e

    async def esperar_carga_completa(self, page, timeout: int):
        logger.info("⌛ Esperando carga completa de la página")
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout * 1000)
        except:
            await page.wait_for_load_state("domcontentloaded", timeout=timeout * 1000)
        await asyncio.sleep(random.uniform(1, 2))
        logger.info("✅ Página cargada completamente")

    async def obtener_codigo_unico(self, ruc: str, max_intentos: int = 4, timeout_base: int = 25) -> str:
        ruc = str(ruc).strip()
        logger.info(f"🔎 Buscando código único para RUC: {ruc}")

        if not await self.verificar_conexion_sitio("https://pad.minem.gob.pe/REINFO_WEB/Index.aspx", 5):
            logger.error(f"❌ Sitio REINFO no disponible para RUC {ruc}")
            return "Sitio no disponible"

        for intento in range(1, max_intentos + 1):
            page = None
            try:
                timeout_actual = timeout_base + (intento * 5)
                page = await self.context.new_page()
                page.set_default_timeout(timeout_actual * 1000)
                page.set_default_navigation_timeout(timeout_actual * 1000)

                logger.info(f"🌐 Intento {intento}/{max_intentos}: navegando al sitio REINFO (timeout: {timeout_actual}s)")
                await self.navegar_con_reintentos(page, "https://pad.minem.gob.pe/REINFO_WEB/Index.aspx")
                await self.esperar_carga_completa(page, timeout_actual)

                await page.wait_for_selector("#txtruc", timeout=10000)
                await page.fill("#txtruc", ruc)
                await asyncio.sleep(random.uniform(0.5, 1.5))
                await page.wait_for_selector("#btnBuscar", timeout=5000)
                await page.click("#btnBuscar")

                await page.wait_for_selector("#stdregistro", timeout=12000)

                html_tabla = await page.evaluate("""
                    () => {
                        const table = document.querySelector('#stdregistro');
                        return table ? table.outerHTML : null;
                    }
                """)
                if not html_tabla:
                    raise Exception("No se pudo extraer la tabla")

                df_tabla = pd.read_html(io.StringIO(html_tabla), flavor="bs4")[0]
                if isinstance(df_tabla.columns, pd.MultiIndex):
                    df_tabla.columns = [' '.join(col).strip() for col in df_tabla.columns]

                if "DERECHO MINERO Código Único" in df_tabla.columns:
                    codigos = df_tabla["DERECHO MINERO Código Único"].dropna().astype(str).unique()
                    if set(codigos) == self.CODIGOS_INVALIDOS:
                        logger.warning(f"⚠️ {ruc} → Conjunto inválido detectado en intento {intento}")
                        if intento < max_intentos:
                            raise Exception("Resultado inválido detectado")
                        else:
                            return "Resultado inválido"
                    codigo_concatenado = ", ".join(codigos)
                    logger.info(f"✅ {ruc} → {codigo_concatenado}")
                    return codigo_concatenado
                else:
                    logger.warning(f"⚠️ {ruc} → Columna 'Código Único' no encontrada")
                    return "No tiene REINFO"

            except Exception as e:
                logger.error(f"❌ Error RUC {ruc} (intento {intento}): {str(e)}")
                if intento < max_intentos:
                    delay = self.calcular_backoff_delay(intento)
                    logger.info(f"🔁 Reintentando en {delay:.1f} segundos...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"⛔ Máximo de intentos alcanzado para RUC {ruc}")
                    return "Error de timeout"
            finally:
                if page:
                    await page.close()

        return "Error"

async def obtener_codigo_unico(ruc: str, max_intentos: int = 4, espera_reintento: float = 3) -> str:
    async with ReinfoScraper() as scraper:
        return await scraper.obtener_codigo_unico(ruc, max_intentos)

async def verificar_sitio_reinfo() -> Dict[str, Any]:
    async with ReinfoScraper() as scraper:
        disponible = await scraper.verificar_conexion_sitio("https://pad.minem.gob.pe/REINFO_WEB/Index.aspx", 5)

        print(f"✅ Código de estado HTTP: {disponible.status_code}")
        print("🧾 Contenido inicial de la respuesta:")
        print(disponible.text[:500]) 
        return {
            "disponible": disponible,
            "timestamp": time.time(),
            "url": "https://pad.minem.gob.pe/REINFO_WEB/Index.aspx"
        }

async def agregar_codigo_unico_al_df(df: pd.DataFrame, columna_ruc: str = "ruc") -> pd.DataFrame:
    df = df.copy()
    codigos = []

    async with ReinfoScraper() as scraper:
        for idx, row in df.iterrows():
            ruc = str(row[columna_ruc])
            logger.info(f"🔄 Procesando RUC {ruc} (fila {idx})...")
            try:
                codigo = await scraper.obtener_codigo_unico(ruc)
            except Exception as e:
                logger.error(f"❌ Error al obtener código único para {ruc}: {e}")
                codigo = "Error"
            codigos.append(codigo)
            await asyncio.sleep(random.uniform(0.5, 1.5))  # pequeña pausa para evitar sobrecarga

    df["Código Único"] = codigos
    return df

if __name__ == "__main__":
    async def test():
        print("🧪 Iniciando prueba...")
        estado = await verificar_sitio_reinfo()
        print(f"Estado del sitio: {estado}")
        ruc_prueba = "20606564016"
        codigo = await obtener_codigo_unico(ruc_prueba)
        print(f"Código para {ruc_prueba}: {codigo}")

    asyncio.run(test())
