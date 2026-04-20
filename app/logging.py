# Logging configuration (JSON format)

import json
from datetime import datetime
from typing import Dict, Any


def crear_log_json(
    request_id: str,
    servicio: str,
    funcionalidad: str,
    metodo: str,
    codigo_respuesta: int,
    duracion_ms: int,
    usuario_id: str = "sistema",
    detalle: str = "Operación ejecutada"
) -> str:
    """Crear log en formato JSON"""
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "servicio": servicio,
        "funcionalidad": funcionalidad,
        "metodo": metodo,
        "codigo_respuesta": codigo_respuesta,
        "duracion_ms": duracion_ms,
        "usuario_id": usuario_id,
        "detalle": detalle
    }
    return json.dumps(log)
