import uuid
import time
from datetime import datetime
from typing import Any, Dict, Optional


def generate_request_id() -> str:
    """Genera un identificador único para cada solicitud HTTP.
    
    Formato: PRV-{timestamp}-{random}
    
    El formato permite:
    - Identificar fácilmente solicitudes del servicio PRV
    - Correlacionar logs con solicitudes específicas
    - Facilitar debugging de problemas
    
    Retorna:
        str: Identificador único en formato PRV-{timestamp}-{random}
        
    Ejemplo:
        >>> generate_request_id()
        'PRV-1704067200-a1b2c3'
    """
    timestamp = int(time.time())
    random_id = str(uuid.uuid4())[:6]
    return f"PRV-{timestamp}-{random_id}"


def standard_response(
    request_id: str,
    success: bool,
    data: Optional[Any] = None,
    message: str = "",
    status_code: int = 200,
) -> Dict[str, Any]:
    """Construye una respuesta estándar para todos los endpoints.
    
    Proporciona un formato consistente para todas las respuestas del API,
    facilitando el consumo por clientes y la depuración.
    
    Parámetros:
        request_id: Identificador único de la solicitud
        success: Indica si la operación fue exitosa (True/False)
        data: Datos a retornar (puede ser None en errores)
        message: Mensaje descriptivo de la operación
        status_code: Código HTTP de la respuesta
    
    Retorna:
        Dict con la estructura estándar de respuesta:
        {
            "request_id": str,
            "success": bool,
            "data": Any,
            "message": str,
            "timestamp": str (ISO format)
        }
    
    Ejemplo:
        >>> standard_response("PRV-1234-abc", True, {"id": 1}, "Exitoso")
        {
            'request_id': 'PRV-1234-abc',
            'success': True,
            'data': {'id': 1},
            'message': 'Exitoso',
            'timestamp': '2024-01-01T12:00:00.000000'
        }
    """
    return {
        "request_id": request_id,
        "success": success,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }


class StandardResponse:
    """Clase auxiliar para construir respuestas estándar en endpoints.
    
    Proporciona métodos convenientes para formatear respuestas de éxito y error
    manteniendo el identificador de solicitud.
    
    Uso:
        response = StandardResponse(request_id)
        return response.success(data, "Operación exitosa")
        return response.error("Error en la operación")
    
    Atributos:
        request_id: Identificador único de la solicitud actual
    """
    
    def __init__(self, request_id: str):
        """Inicializa la respuesta con un identificador de solicitud.
        
        Parámetros:
            request_id: Identificador único de la solicitud (ej: PRV-1234-abc)
        """
        self.request_id = request_id

    def success(self, data: Any = None, message: str = "") -> Dict[str, Any]:
        """Construye una respuesta de éxito.
        
        Parámetros:
            data: Datos a retornar (por defecto None)
            message: Mensaje descriptivo de la operación
        
        Retorna:
            Dict: Respuesta formateada como éxito
        
        Ejemplo:
            >>> response = StandardResponse("PRV-123-abc")
            >>> response.success({"id": 1, "nombre": "Proveedor"}, "Creado exitosamente")
        """
        return standard_response(self.request_id, True, data, message)

    def error(self, message: str, data: Any = None) -> Dict[str, Any]:
        """Construye una respuesta de error.
        
        Parámetros:
            message: Descripción del error
            data: Datos adicionales del error (opcional)
        
        Retorna:
            Dict: Respuesta formateada como error (success=False)
        
        Ejemplo:
            >>> response = StandardResponse("PRV-123-abc")
            >>> response.error("Proveedor no encontrado", {"searched_id": 999})
        """
        return standard_response(self.request_id, False, data, message)
