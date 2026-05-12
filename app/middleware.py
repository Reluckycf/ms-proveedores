from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.utils.core import generate_request_id
import time


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware que asigna un identificador único a cada solicitud HTTP.
    
    Características:
    - Genera o utiliza un Request ID existente (header X-Request-ID)
    - Lo almacena en el estado de la solicitud
    - Lo retorna en los headers de la respuesta
    
    Beneficios:
    - Trazabilidad completa de solicitudes en logs distribuidos
    - Correlación de errores con solicitudes específicas
    - Debugging facilitado en sistemas complejos
    
    Encabezados:
    - Input: X-Request-ID (opcional)
    - Output: X-Request-ID (en todas las respuestas)
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Procesa la solicitud y asigna un Request ID.
        
        Parámetros:
            request: Objeto de la solicitud HTTP
            call_next: Función para continuar con el siguiente middleware/ruta
        
        Retorna:
            Response: Respuesta con X-Request-ID en headers
        """
        request_id = request.headers.get("X-Request-ID", generate_request_id())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware que registra el tiempo de procesamiento de cada solicitud.
    
    Características:
    - Mide el tiempo total de procesamiento de la solicitud
    - Incluye el tiempo en el header X-Process-Time de la respuesta
    - Útil para monitoreo de performance y detección de cuellos de botella
    
    Encabezados:
    - Output: X-Process-Time (tiempo en segundos)
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Procesa la solicitud y mide su tiempo de ejecución.
        
        Parámetros:
            request: Objeto de la solicitud HTTP
            call_next: Función para continuar con el siguiente middleware/ruta
        
        Retorna:
            Response: Respuesta con X-Process-Time en headers
        """
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        response.headers["X-Process-Time"] = str(duration)
        
        return response
