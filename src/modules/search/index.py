# src/modules/search/index.py
from fastapi import APIRouter, Depends
from modules.search.routes.private_routes import router as private_router

# Router global que engloba todo el módulo de autenticación
search_module = APIRouter(prefix="/search", tags=["Search"])

# Incluir rutas privadas con dependency de autenticación
search_module.include_router(private_router)

# Exportar solo el router global
__all__ = ["search_module"]