# src/modules/shared/middlewares/logging_middleware.py

import time
import logging
from fastapi import Request
from colorama import init, Fore, Style

# Inicializar colorama (solo la primera vez)
init(autoreset=True)

logger = logging.getLogger(__name__)


def color_status(status_code: int):
    if status_code >= 500:
        return Fore.RED  # errores de servidor
    elif status_code >= 400:
        return Fore.YELLOW  # errores del cliente
    elif status_code >= 300:
        return Fore.CYAN  # redirecciones
    elif status_code >= 200:
        return Fore.GREEN  # éxito
    else:
        return Fore.WHITE  # otro


async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    status_color = color_status(response.status_code)

    logger.info(
        "%s %s - %s%d%s - %.4fs",
        request.method,
        str(request.url),
        status_color,
        response.status_code,
        Style.RESET_ALL,
        process_time,
    )

    return response
