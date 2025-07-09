# src/app.py
import logging
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles  
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Middlewares personalizados
from modules.shared.middlewares.error_middleware import (
    http_exception_handler,
    general_exception_handler,
    error_handler,
)
from modules.shared.middlewares.logging_middleware import log_requests_middleware


# Modules
from modules.search.index import search_module

# Configuración del logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Dominios permitidos
PRODUCTION_DOMAINS = [
    "python-backend-test-production.up.railway.app",
    "smart-due.up.railway.app",
    "smart-due.vercel.app",
    "smart-due-v2.vercel.app",
    "smart-due-fronted-v2.vercel.app",
    "google-scrapper-backend-production.up.railway.app",
    "project-myra-backend.up.railway.app",
    "project-myra-frontend.vercel.app"
]

LOCAL_DOMAINS = ["localhost", "0.0.0.0"]

ALLOWED_DOMAINS = [*LOCAL_DOMAINS, *PRODUCTION_DOMAINS]

# Generar CORS origins
CORS_ORIGINS = [
    *[f"http://localhost:{port}" for port in range(3000, 3010)],
    *[f"https://localhost:{port}" for port in range(3000, 3010)],
    *[f"http://localhost:{port}" for port in range(5000, 5010)],
    *[f"https://localhost:{port}" for port in range(5000, 5010)],
    "http://0.0.0.0:3000",
    "http://0.0.0.0:5000",
    *[f"https://{domain}" for domain in PRODUCTION_DOMAINS],
]

app = FastAPI(
    title="Python Backend Test",
    description="Backend API",
    version="1.0.0",
)

# --- Montar archivos estáticos desde /public ---
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
public_dir = os.path.join(project_root, "public")

if os.path.exists(public_dir):
    app.mount("/static", StaticFiles(directory=public_dir), name="static")
else:
    logging.warning("⚠️ Carpeta 'public/' no encontrada. Archivos estáticos no disponibles.")

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_DOMAINS)

# Middleware de logs
app.middleware("http")(log_requests_middleware)

# Manejo de excepciones
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Ruta raíz
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World!"}


# Endpoint para favicon.ico (compatibilidad con navegadores)
@app.get("/favicon.ico", tags=["Favicon"])
async def favicon():
    if os.path.exists(public_dir):
        favicon_path = os.path.join(public_dir, "favicon.ico")
        if os.path.isfile(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")

    raise HTTPException(status_code=404, detail="Favicon not found")


# Modules
app.include_router(search_module, prefix="/api")

# Ruta catch-all para rutas no definidas
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"], tags=["Catch-All"])
async def catch_all(request: Request, path: str):
    return error_handler.e404("The resource you are looking for does not exist.")