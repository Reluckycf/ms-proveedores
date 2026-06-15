import httpx
import os
from datetime import datetime
from typing import Optional, Dict, Any
import asyncio

AUTH_SERVICE = os.getenv("MS_AUTENTICACION_URL", "http://localhost:8000")
ROLES_SERVICE = os.getenv("MS_ROLES_URL", "http://localhost:8002")
NOTIF_SERVICE = os.getenv("MS_NOTIFICACIONES_URL", "http://localhost:8003")
AUDIT_SERVICE = os.getenv("MS_AUDITORIA_URL", "http://localhost:8004")

APP_TOKEN = os.getenv("APP_TOKEN", "prv_token_dev_12345")


class AuthClient:
    @staticmethod
    async def validate_session(token: str) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{AUTH_SERVICE}/api/v1/auth/session/validate",
                    json={"token": token},
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid"):
                        return data
                return None
        except Exception as e:
            print(f"Error validando sesión: {str(e)}")
            return None


class RolesClient:
    @staticmethod
    async def validate_permission(role_name: str, permission_code: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{ROLES_SERVICE}/api/v1/validacion/permiso",
                    params={"rol": role_name, "permiso": permission_code},
                    headers={"Authorization": f"Bearer {APP_TOKEN}"},
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json().get("data", {}).get("autorizado", False)
                return False
        except Exception as e:
            print(f"Error validando permiso: {str(e)}")
            return False


class NotificacionesClient:
    @staticmethod
    async def enviar_alerta(tipo: str, asunto: str, descripcion: str, datos: Dict = None):
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{NOTIF_SERVICE}/api/v1/notificaciones/alerta",
                    json={
                        "tipo": tipo,
                        "asunto": asunto,
                        "descripcion": descripcion,
                        "datos": datos or {}
                    },
                    headers={"X-App-Token": APP_TOKEN},
                    timeout=5.0
                )
        except Exception:
            pass

    @staticmethod
    async def enviar_contrato_vencimiento(numero_contrato: str, proveedor: str, fecha_fin: str):
        await NotificacionesClient.enviar_alerta(
            tipo="CONTRATO_PROXIMO_VENCER",
            asunto=f"Contrato próximo a vencer: {numero_contrato}",
            descripcion=f"Contrato {numero_contrato} con {proveedor} vence el {fecha_fin}",
            datos={"numero_contrato": numero_contrato, "fecha_fin": fecha_fin}
        )

    @staticmethod
    async def enviar_documento_vencimiento(proveedor: str, tipo_doc: str, fecha_venc: str):
        await NotificacionesClient.enviar_alerta(
            tipo="DOCUMENTO_PROXIMO_VENCER",
            asunto=f"Documento próximo a vencer: {tipo_doc}",
            descripcion=f"Documento {tipo_doc} de {proveedor} vence el {fecha_venc}",
            datos={"tipo_documento": tipo_doc, "fecha_vencimiento": fecha_venc}
        )

    @staticmethod
    async def enviar_puntaje_bajo(proveedor: str, puntaje: float):
        await NotificacionesClient.enviar_alerta(
            tipo="PROVEEDOR_PUNTAJE_BAJO",
            asunto=f"Puntaje de evaluación bajo: {proveedor}",
            descripcion=f"Proveedor {proveedor} tiene puntaje de evaluación bajo: {puntaje}",
            datos={"proveedor": proveedor, "puntaje": puntaje}
        )


class AuditoriaClient:
    @staticmethod
    async def registrar_log(
        trace_id: str,
        action: str,
        method: str,
        status_code: int,
        duration_ms: int,
        user_id: str = "sistema",
        detail: str = ""
    ):
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{AUDIT_SERVICE}/api/v1/logs",
                    json={
                        "timestamp": datetime.now().isoformat(),
                        "trace_id": trace_id,
                        "service_name": "ms-proveedores",
                        "action": action,
                        "method": method,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "user_id": user_id,
                        "detail": detail
                    },
                    headers={"X-App-Token": APP_TOKEN},
                    timeout=5.0
                )
        except Exception as e:
            print(f"Error registrando log: {str(e)}")
