from fastapi import HTTPException, Request, Depends, BackgroundTasks
from app.clients import AuthClient, RolesClient, AuditoriaClient
import time

async def get_current_user(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    user = await AuthClient.validate_session(token)
    if not user:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: dict = Depends(get_current_user)):
        # Si el rol del usuario está en la lista permitida, pasa
        # ms-auth devuelve el campo como "role"
        role_name = user.get("role", "").lower()
        if role_name not in [r.lower() for r in self.allowed_roles]:
            raise HTTPException(
                status_code=403, 
                detail=f"El rol {role_name} no tiene permisos para esta acción"
            )
        return user

async def registrar_auditoria_bg(
    background_tasks: BackgroundTasks,
    trace_id: str,
    action: str,
    method: str,
    status_code: int,
    duration_ms: int,
    user_id: str,
    detail: str = ""
):
    background_tasks.add_task(
        AuditoriaClient.registrar_log,
        trace_id=trace_id,
        action=action,
        method=method,
        status_code=status_code,
        duration_ms=duration_ms,
        user_id=user_id,
        detail=detail
    )
