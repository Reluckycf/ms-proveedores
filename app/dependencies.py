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
    def __init__(self, allowed_roles: list, permission_code: str = None):
        self.allowed_roles = allowed_roles
        self.permission_code = permission_code

    async def __call__(self, user: dict = Depends(get_current_user)):
        role_name = user.get("role", "").lower()
        role_name_original = user.get("role", "")

        # RT-02: Intentar validar permiso contra ms-roles
        if self.permission_code:
            try:
                autorizado = await RolesClient.validate_permission(
                    role_name_original, self.permission_code
                )
                if autorizado:
                    return user
            except Exception:
                pass

        # Fallback: validar por nombre de rol
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
