# Ejemplo de Integración de Dependencias

Este archivo muestra cómo integrar la validación de sesión, permisos, alertas y auditoría en los endpoints.

## Opción 1: Integración Completa (Recomendada para Producción)

```python
from fastapi import APIRouter, HTTPException, Request
from app.dependencies import validar_sesion, validar_permiso, registrar_auditoria
from app.utils.core import generate_request_id, StandardResponse
from app.services.provider import ProveedorService
import time

router = APIRouter()

@router.post("/api/v1/proveedores")
async def crear_proveedor(request: Request, proveedor: ProveedorCreate):
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    inicio = time.time()
    
    try:
        # 1. Validar sesión obligatorio
        sesion = await validar_sesion(request)
        usuario_id = sesion.get("usuario_id", "sistema")
        
        # 2. Validar permiso específico
        await validar_permiso(sesion, "PRV_CREATE_PROVEEDOR")
        
        # 3. Ejecutar lógica de negocio
        nuevo = ProveedorService.crear_proveedor(proveedor)
        
        # 4. Registrar auditoría (asíncrono, no bloquea)
        duracion = int((time.time() - inicio) * 1000)
        await registrar_auditoria(
            request_id=request_id,
            funcionalidad="crear_proveedor",
            metodo="POST",
            codigo_respuesta=201,
            usuario_id=usuario_id
        )
        
        return response.success(
            {"id": nuevo.id, "nit": nuevo.nit},
            "Proveedor creado exitosamente"
        )
        
    except HTTPException as e:
        await registrar_auditoria(
            request_id=request_id,
            funcionalidad="crear_proveedor",
            metodo="POST",
            codigo_respuesta=e.status_code,
            usuario_id="desconocido"
        )
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Opción 2: Sin Validación (Para Desarrollo/Testing)

```python
@router.post("/api/v1/proveedores")
def crear_proveedor(proveedor: ProveedorCreate):
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    try:
        nuevo = ProveedorService.crear_proveedor(proveedor)
        return response.success(
            {"id": nuevo.id, "nit": nuevo.nit},
            "Proveedor creado exitosamente"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Pasos de Integración en Rutas Reales

1. **Verificar disponibilidad de servicios en .env**
   ```bash
   MS_AUTENTICACION_URL=http://localhost:8000
   MS_ROLES_URL=http://localhost:8002
   APP_TOKEN=prv_token_dev_12345
   ```

2. **Agregar imports en app/routes/provider.py**
   ```python
   from app.dependencies import validar_sesion, validar_permiso, registrar_auditoria
   ```

3. **Envolver endpoints críticos** con:
   - `await validar_sesion(request)` - Primero
   - `await validar_permiso(sesion, "PRV_CODIGO")` - Segundo
   - `await registrar_auditoria(...)` - Último (asíncrono)

4. **Códigos de permiso esperados**:
   ```
   PRV_CREATE_PROVEEDOR
   PRV_READ_PROVEEDOR
   PRV_UPDATE_PROVEEDOR
   PRV_DELETE_PROVEEDOR
   PRV_CREATE_CONTRATO
   PRV_READ_CONTRATO
   PRV_CREATE_EVALUACION
   PRV_CREATE_COTIZACION
   PRV_CREATE_DOCUMENTO
   ```

## Flujo de Ejecución

```
1. Cliente → Endpoint con Authorization header
   ├── Authorization: Bearer {token}
   
2. validar_sesion()
   ├── Extrae token del header
   ├── Llama a ms-autenticacion
   ├── Retorna usuario, rol, permisos
   └── Si falla: HTTP 401
   
3. validar_permiso()
   ├── Valida con ms-roles
   ├── Verifica si role_id tiene permission_code
   └── Si falla: HTTP 403
   
4. Lógica de negocio
   ├── Ejecuta la operación
   ├── Envía alertas si aplica (asíncrono)
   └── Retorna respuesta
   
5. registrar_auditoria()
   ├── Envía log a ms-auditoria (asíncrono)
   ├── No bloquea respuesta
   └── Si falla, continúa normalmente
   
6. Cliente ← Respuesta JSON estándar
   └── Con request_id incluido
```

## Manejo de Fallos

```python
try:
    sesion = await validar_sesion(request)
except HTTPException as e:
    # Sesión inválida (401)
    # Usuario no está autenticado
    raise

try:
    await validar_permiso(sesion, "PRV_CODIGO")
except HTTPException as e:
    # Permiso insuficiente (403)
    # Usuario no tiene autorización
    raise

# Auditoría y notificaciones NUNCA lanzan excepciones
# Si fallan, se continúa operando normalmente
await registrar_auditoria(...)
```

## Variables Requeridas en sesion

```python
sesion = {
    "usuario_id": "USR-001",      # ID del usuario
    "username": "carlos",
    "role_id": 2,                 # ID del rol
    "permisos": [...]             # Lista de códigos de permiso
}
```

## Testing con Postman/curl

```bash
# Con autenticación
curl -X POST http://localhost:8001/api/v1/proveedores \
  -H "Authorization: Bearer {token_valido}" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Sin autenticación (falla con 401)
curl -X POST http://localhost:8001/api/v1/proveedores \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

**Guía completa de integración de dependencias lista.** ✅
