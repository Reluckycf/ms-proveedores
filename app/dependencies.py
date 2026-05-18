from fastapi import HTTPException, Request, Depends
from app.clients import AuthClient, RolesClient, AuditoriaClient, NotificacionesClient
import time
import uuid
from datetime import datetime


async def generar_request_id() -> str:
    """
    Genera un identificador único de rastreo con el formato:
    código del servicio + timestamp Unix + identificador corto aleatorio
    Ejemplo: PRV-1740000000-a3f8b2
    """
    timestamp = int(time.time())
    random_id = uuid.uuid4().hex[:6]
    return f"PRV-{timestamp}-{random_id}"


async def validar_sesion(request: Request) -> dict:
    """
    Valida sesión antes de ejecutar lógica de negocio.
    Es la primera validación que todos los microservicios deben hacer.
    Según la regla 6.1: Validación de Sesión Obligatoria
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    
    sesion = await AuthClient.validate_session(token)
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión inválida")
    
    return sesion


async def validar_permiso(sesion: dict, permission_code: str) -> bool:
    """
    Valida permisos después de validar sesión.
    Según la regla 6.2: Validación de Permisos por Funcionalidad
    Cada funcionalidad tiene un código de permiso único (ej: PRV_CREATE_PROVEEDOR)
    """
    role_id = sesion.get("role_id")
    if not role_id:
        raise HTTPException(status_code=403, detail="Rol no asignado")
    
    autorizado = await RolesClient.validate_permission(role_id, permission_code)
    if not autorizado:
        raise HTTPException(status_code=403, detail="Permiso insuficiente")
    
    return True


async def registrar_auditoria(
    request_id: str,
    funcionalidad: str,
    metodo: str,
    codigo_respuesta: int,
    usuario_id: str = "sistema",
    detalle: str = "",
    duracion_ms: int = 0
) -> None:
    """
    Registra operación en auditoría de forma asíncrona.
    Según la regla 6.6: Auditoría y Logs en Formato JSON
    
    El envío NO bloquea la respuesta al usuario si falla.
    Si el envío al servicio de auditoría falla, el microservicio continúa operando normalmente.
    """
    try:
        await AuditoriaClient.registrar_log(
            request_id=request_id,
            funcionalidad=funcionalidad,
            metodo=metodo,
            codigo_respuesta=codigo_respuesta,
            duracion_ms=duracion_ms,
            usuario_id=usuario_id,
            detalle=detalle or f"Operación {funcionalidad} completada"
        )
    except Exception:
        # No bloquear si el servicio de auditoría no está disponible
        pass


async def enviar_alerta_contrato(
    numero_contrato: str, 
    proveedor: str, 
    fecha_fin: str
) -> None:
    """
    Envía alerta de contrato próximo a vencer.
    Según ms-proveedores: Debe enviar alertas para contratos vencidos en próximos 30 días.
    """
    try:
        await NotificacionesClient.enviar_contrato_vencimiento(
            numero_contrato=numero_contrato,
            proveedor=proveedor,
            fecha_fin=fecha_fin
        )
    except Exception:
        # No bloquear si el servicio de notificaciones no está disponible
        pass


async def enviar_alerta_documento(
    proveedor: str,
    tipo_doc: str,
    fecha_venc: str
) -> None:
    """
    Envía alerta de documento próximo a vencer.
    Según ms-proveedores: Debe enviar alertas para documentos vencidos en próximos 30 días.
    """
    try:
        await NotificacionesClient.enviar_documento_vencimiento(
            proveedor=proveedor,
            tipo_doc=tipo_doc,
            fecha_venc=fecha_venc
        )
    except Exception:
        # No bloquear si el servicio de notificaciones no está disponible
        pass


async def enviar_alerta_puntaje_bajo(
    proveedor: str,
    puntaje: float
) -> None:
    """
    Envía alerta de proveedor con puntaje bajo.
    Según ms-proveedores: Debe enviar alertas para proveedores con puntaje < 3.0.
    """
    try:
        await NotificacionesClient.enviar_puntaje_bajo(
            proveedor=proveedor,
            puntaje=puntaje
        )
    except Exception:
        # No bloquear si el servicio de notificaciones no está disponible
        pass
