from fastapi import HTTPException, Request
from app.clients import AuthClient, RolesClient, AuditoriaClient
import time


async def validar_sesion(request: Request):
    """Valida sesión antes de ejecutar lógica de negocio"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    
    sesion = await AuthClient.validate_session(token)
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión inválida")
    
    return sesion


async def validar_permiso(sesion: dict, permission_code: str):
    """Valida permisos después de validar sesión"""
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
    usuario_id: str = "sistema"
):
    """Registra operación en auditoría (asíncrono, no bloquea)"""
    duracion_ms = 0
    await AuditoriaClient.registrar_log(
        request_id=request_id,
        funcionalidad=funcionalidad,
        metodo=metodo,
        codigo_respuesta=codigo_respuesta,
        duracion_ms=duracion_ms,
        usuario_id=usuario_id,
        detalle=f"Operación {funcionalidad} realizada exitosamente"
    )
