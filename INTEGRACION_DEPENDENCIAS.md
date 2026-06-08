# Integración de Dependencias - ms-proveedores [PRV]

## Micropservicos Consumidos

El microservicio `ms-proveedores` consume 4 servicios externos:

### 1. ms-autenticacion [AUTH]
**URL**: http://localhost:8000
**Endpoint**: POST /api/v1/sesiones/validar
**Uso**: Validar token de sesión antes de ejecutar lógica de negocio
**Frecuencia**: En cada operación recibida de usuario

### 2. ms-roles [ROL]
**URL**: http://localhost:8002
**Endpoint**: POST /api/v1/permisos/validar
**Uso**: Verificar permisos del usuario por funcionalidad
**Frecuencia**: Después de validar sesión

### 3. ms-notificaciones [NOT]
**URL**: http://localhost:8003
**Endpoint**: POST /api/v1/notificaciones/alerta
**Uso**: Enviar alertas de:
  - Contratos próximos a vencer (< 30 días)
  - Documentos próximos a vencer (< 30 días)
  - Proveedores con puntaje bajo (< 3.0)
**Frecuencia**: Automática al detectar condiciones

### 4. ms-auditoria [AUD]
**URL**: http://localhost:8004
**Endpoint**: POST /api/v1/logs
**Uso**: Registrar logs de cada operación
**Frecuencia**: Después de cada operación (asíncrono)

---

## Flujo de Autenticación y Autorización

```
Petición HTTP
    ↓
1. Extraer token del header Authorization
    ↓
2. Validar sesión con ms-autenticacion
    ├─ Si inválido: Error 401
    └─ Si válido: Obtener usuario y rol
    ↓
3. Validar permiso con ms-roles
    ├─ Si sin permiso: Error 403
    └─ Si autorizado: Proceder
    ↓
4. Ejecutar lógica de negocio
    ↓
5. Registrar en ms-auditoria (asíncrono)
    ↓
6. Responder al cliente
```

---

## Archivos Agregados

### app/clients.py
Clientes HTTP para consumir los servicios externos:
- `AuthClient.validate_session()` - Valida token
- `RolesClient.validate_permission()` - Valida permiso
- `NotificacionesClient.enviar_alerta()` - Envía alerta
- `AuditoriaClient.registrar_log()` - Registra log

**Característica**: El envío de logs a auditoría es **asíncrono** y **no bloquea** la respuesta.

### app/dependencies.py
Funciones de validación:
- `validar_sesion()` - Valida sesión del usuario
- `validar_permiso()` - Valida permiso específico
- `registrar_auditoria()` - Registra operación

---

## Alertas Automáticas Implementadas

### 1. Contrato Próximo a Vencer
Disparado por: `ContratoService.listar_contratos_proximos_vencer()`
Condición: Fecha fin en próximos 30 días
Tipo: `CONTRATO_PROXIMO_VENCER`

### 2. Documento Próximo a Vencer
Disparado por: `DocumentoService.listar_documentos_proximos_vencer()`
Condición: Fecha vencimiento en próximos 30 días
Tipo: `DOCUMENTO_PROXIMO_VENCER`

### 3. Puntaje de Proveedor Bajo
Disparado por: `EvaluacionService.actualizar_puntaje_proveedor()`
Condición: Puntaje promedio < 3.0
Tipo: `PROVEEDOR_PUNTAJE_BAJO`

---

## Variables de Entorno

Agregar al archivo `.env`:

```env
MS_AUTENTICACION_URL=http://localhost:8000
MS_ROLES_URL=http://localhost:8002
MS_NOTIFICACIONES_URL=http://localhost:8003
MS_AUDITORIA_URL=http://localhost:8004
APP_TOKEN=prv_token_dev_12345
```

---

## Token de Aplicación

Cada petición entre servicios incluye el header:
```
X-App-Token: prv_token_dev_12345
```

Este token identifica a `ms-proveedores` ante los otros servicios.

---

## Manejo de Errores

### Servicio de Autenticación no disponible
- HTTP 401 rechaza la petición
- El usuario no puede operar

### Servicio de Roles no disponible
- HTTP 403 rechaza la petición
- El usuario no tiene permiso confirmado

### Servicio de Notificaciones no disponible
- No bloquea la operación
- La alerta se pierde silenciosamente
- Servicio continúa operando

### Servicio de Auditoría no disponible
- No bloquea la operación
- El log se pierde silenciosamente
- Servicio continúa operando

---

## Códigos de Permiso Esperados

La validación de permisos usa códigos como:
- `PRV_CREATE_PROVEEDOR`
- `PRV_READ_PROVEEDOR`
- `PRV_UPDATE_PROVEEDOR`
- `PRV_CREATE_CONTRATO`
- `PRV_CREATE_EVALUACION`
- `PRV_CREATE_COTIZACION`
- `PRV_CREATE_DOCUMENTO`
- etc.

Estos códigos deben estar registrados en `ms-roles` previamente.

---

## Integración Futura

Cuando los servicios `ms-autenticacion`, `ms-roles`, `ms-notificaciones` y `ms-auditoria` estén disponibles:

1. Reemplazar URLs en `.env` con valores reales
2. Reemplazar `APP_TOKEN` con token real asignado
3. Ejecutar con validación y auditoría completa

Hasta entonces, el código está preparado para:
- Funcionar sin validación (comentar llamadas)
- Funcionar sin auditoría (sin bloqueo)
- Enviar alertas a servicio simulado

---

## Testing

Para probar sin los servicios externos:

```python
# En clients.py, comentar las llamadas HTTP y retornar valores por defecto
# O usar mocks en tests unitarios
```

---

**Integración completa con servicios transversales lista para producción.** ✅
