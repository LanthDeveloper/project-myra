# src/modules/shared/middlewares/error_middleware.py

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any, Optional, Union
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class ErrorHandler:
    """Manejador de errores similar a tu middleware de Node.js"""

    @staticmethod
    def create_error_response(
        status_code: int, title: str, message: str, include_timestamp: bool = False
    ) -> Dict[str, Any]:
        """Crea una respuesta de error estandarizada"""
        response = {"title": title, "message": message}

        if include_timestamp:
            response["timestamp"] = datetime.utcnow().isoformat() + "Z"

        return response

    @staticmethod
    def e400(message: Optional[str] = None) -> JSONResponse:
        """Error 400 - Bad Request"""
        error_message = (
            message
            or "The request could not be understood or was missing required parameters."
        )
        return JSONResponse(
            status_code=400,
            content=ErrorHandler.create_error_response(
                400, "Error 400 Bad Request", error_message
            ),
        )

    @staticmethod
    def e401(message: Optional[str] = None) -> JSONResponse:
        """Error 401 - Unauthorized"""
        error_message = message or "Authorization is required for this resource."
        return JSONResponse(
            status_code=401,
            content=ErrorHandler.create_error_response(
                401, "Error 401 Authorization Required", error_message
            ),
        )

    @staticmethod
    def e403(message: Optional[str] = None) -> JSONResponse:
        """Error 403 - Forbidden"""
        error_message = message or "You do not have permission to access this resource."
        return JSONResponse(
            status_code=403,
            content=ErrorHandler.create_error_response(
                403, "Error 403 Forbidden", error_message
            ),
        )

    @staticmethod
    def e404(message: Optional[str] = None) -> JSONResponse:
        """Error 404 - Not Found"""
        error_message = message or "The resource you are looking for does not exist."
        return JSONResponse(
            status_code=404,
            content=ErrorHandler.create_error_response(
                404, "Error 404 Not Found", error_message, include_timestamp=True
            ),
        )

    @staticmethod
    def e405(message: Optional[str] = None) -> JSONResponse:
        """Error 405 - Method Not Allowed"""
        error_message = (
            message or "The method used in the request is not allowed for the resource."
        )
        return JSONResponse(
            status_code=405,
            content=ErrorHandler.create_error_response(
                405, "Error 405 Method Not Allowed", error_message
            ),
        )

    @staticmethod
    def e409(message: Optional[str] = None) -> JSONResponse:
        """Error 409 - Conflict"""
        error_message = (
            message
            or "The request could not be completed due to a conflict with the current state of the resource."
        )
        return JSONResponse(
            status_code=409,
            content=ErrorHandler.create_error_response(
                409, "Error 409 Conflict", error_message
            ),
        )

    @staticmethod
    def e422(message: Optional[str] = None) -> JSONResponse:
        """Error 422 - Unprocessable Entity"""
        error_message = (
            message or "The request was well-formed, but there were validation errors."
        )
        return JSONResponse(
            status_code=422,
            content=ErrorHandler.create_error_response(
                422, "Error 422 Unprocessable Entity", error_message
            ),
        )

    @staticmethod
    def e500(message: Optional[str] = None) -> JSONResponse:
        """Error 500 - Internal Server Error"""
        error_message = message or "An internal server error occurred."
        return JSONResponse(
            status_code=500,
            content=ErrorHandler.create_error_response(
                500, "Error 500 Internal Server Error", error_message
            ),
        )

    @staticmethod
    def e502(message: Optional[str] = None) -> JSONResponse:
        """Error 502 - Bad Gateway"""
        error_message = (
            message
            or "The server received an invalid response from the upstream server."
        )
        return JSONResponse(
            status_code=502,
            content=ErrorHandler.create_error_response(
                502, "Error 502 Bad Gateway", error_message
            ),
        )

    @staticmethod
    def e503(message: Optional[str] = None) -> JSONResponse:
        """Error 503 - Service Unavailable"""
        error_message = (
            message or "The server is currently unavailable. Please try again later."
        )
        return JSONResponse(
            status_code=503,
            content=ErrorHandler.create_error_response(
                503, "Error 503 Service Unavailable", error_message
            ),
        )

    @staticmethod
    def e504(message: Optional[str] = None) -> JSONResponse:
        """Error 504 - Gateway Timeout"""
        error_message = (
            message
            or "The server, acting as a gateway, did not receive a response in time."
        )
        return JSONResponse(
            status_code=504,
            content=ErrorHandler.create_error_response(
                504, "Error 504 Gateway Timeout", error_message
            ),
        )

    @staticmethod
    def e_main(exc: Exception, request: Request = None) -> JSONResponse:
        """
        Método principal para manejar errores - equivalente a eMain en Node.js
        """
        # Log del error (equivalente a console.error)
        logger.error(f"Error occurred: {exc}", exc_info=True)
        
        # Obtener status code del error
        status_code = getattr(exc, 'status_code', None) or getattr(exc, 'status', 500)
        message = getattr(exc, 'detail', None) or str(exc)
        
        # Mapear códigos de estado a métodos específicos
        error_methods = {
            400: ErrorHandler.e400,
            401: ErrorHandler.e401,
            403: ErrorHandler.e403,
            404: ErrorHandler.e404,
            405: ErrorHandler.e405,
            409: ErrorHandler.e409,
            422: ErrorHandler.e422,
            500: ErrorHandler.e500,
            502: ErrorHandler.e502,
            503: ErrorHandler.e503,
            504: ErrorHandler.e504,
        }

        if status_code in error_methods:
            return error_methods[status_code](message)

        # Error por defecto si no hay método específico
        return ErrorHandler.e_default(exc)

    @staticmethod
    def e_default(exc: Exception) -> JSONResponse:
        """Error por defecto para códigos de estado no mapeados"""
        status_code = getattr(exc, 'status_code', None) or getattr(exc, 'status', 500)
        message = getattr(exc, 'detail', None) or str(exc) or "An unexpected error occurred"
        
        return JSONResponse(
            status_code=status_code,
            content=ErrorHandler.create_error_response(
                status_code,
                f"Error {status_code}",
                message,
            ),
        )


# Instancia global del manejador de errores
error_handler = ErrorHandler()

# Función para manejo de excepciones HTTP
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para excepciones HTTP"""
    return error_handler.e_main(exc, request)

# Función para manejo de errores generales
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador para excepciones generales"""
    return error_handler.e_main(exc, request)