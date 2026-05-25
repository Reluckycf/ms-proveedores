# Manual técnico — ms-proveedores \[PRV]

## 1. Propósito

Este manual describe la implementación técnica del microservicio **ms-proveedores \[PRV]** del proyecto *ERP Universitario*, con base en:

- Código del repositorio `ms-proveedores`.
- Documentación del proyecto (requisitos funcionales por microservicio).

## 2. Stack y componentes

- **Lenguaje:** Python (README indica Python 3.8+).
- **Framework:** FastAPI (`main.py`).
- **ORM:** Peewee (`app/models/models.py`).
- **Base de datos:** PostgreSQL (ver `.env.example` y `docker-compose.yml`).

## 3. Estructura del proyecto

```
ms-proveedores/
├── app/
│   ├── models/models.py          # Modelos Peewee (tablas)
│   ├── routes/provider.py        # Endpoints REST (/api/v1/...)
│   ├── schemas/provider.py       # Esquemas Pydantic (validación)
│   ├── services/provider.py      # Lógica de negocio
│   ├── utils/core.py             # Request ID + respuesta estándar
│   ├── middleware.py             # RequestIDMiddleware + LoggingMiddleware
│   ├── clients.py                # Clientes HTTP a otros microservicios
│   ├── dependencies.py           # Helpers (sesión, permisos, auditoría)
│   └── config.py                 # Conexión a PostgreSQL (DATABASE_URL)
├── main.py                       # App FastAPI + startup (init_db + create_tables)
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

## 4. Configuración (variables de entorno)

Archivo de referencia: `.env.example`.

Variables identificadas:

- `DATABASE_URL`: URL de conexión PostgreSQL.
- `DEBUG`: bandera de depuración (no se usa directamente en las rutas del repositorio).
- `MS_AUTENTICACION_URL`: URL de `ms-autenticacion`.
- `MS_ROLES_URL`: URL de `ms-roles`.
- `MS_NOTIFICACIONES_URL`: URL de `ms-notificaciones`.
- `MS_AUDITORIA_URL`: URL de `ms-auditoria`.
- `APP_TOKEN`: token de aplicación enviado en header `X-App-Token` en clientes `RolesClient`, `NotificacionesClient`, `AuditoriaClient` (ver `app/clients.py`).

## 5. Ejecución local

### 5.1. Base de datos

El repositorio incluye `init_db.sh` para crear usuario y base de datos en PostgreSQL local (requiere permisos de `sudo -u postgres`).

### 5.2. Dependencias y arranque

Según `README.md`:

1. Instalar dependencias:
   - `./setup.sh` (crea venv e instala requirements) o instalación manual con `pip install -r requirements.txt`.
2. Configurar `.env` (copiando `.env.example`).
3. Ejecutar:
   - `python main.py`

El servicio expone por defecto:

- **Base URL:** `http://localhost:8001`
- **Swagger UI:** `http://localhost:8001/docs`
- **ReDoc:** `http://localhost:8001/redoc`
- **Health check:** `http://localhost:8001/health`

### 5.3. Ejecución con Docker

Archivos: `Dockerfile` y `docker-compose.yml`.

- `docker-compose.yml` levanta:
  - `postgres` (PostgreSQL)
  - `api` (ms-proveedores)

## 6. Inicialización del microservicio (startup)

En `main.py` se define un evento `startup` que:

1. Ejecuta `init_db()` (lee `DATABASE_URL` y configura Peewee).
2. Ejecuta `create_tables()` (crea tablas si no existen):
   - `proveedores`
   - `contratos`
   - `evaluaciones`
   - `cotizaciones`
   - `documentos_proveedor`

## 7. Modelo de datos (Peewee)

Fuente: `app/models/models.py`.

### 7.1. Proveedor (`proveedores`)

Campos principales:

- `nit` (único)
- `razon_social`
- `nombre_contacto`
- `email`, `telefono`
- `direccion`, `ciudad`
- `estado` (por defecto `"activo"`, opciones: `activo`, `inactivo`, `suspendido`)
- `fecha_registro`
- `puntaje_evaluacion` (por defecto `0.0`)

### 7.2. Contrato (`contratos`)

- Relación: `proveedor` (FK a Proveedor)
- `numero_contrato` (único)
- `objeto_contrato`
- `monto_total`
- `fecha_inicio`, `fecha_fin`
- `estado` (por defecto `"vigente"`, opciones: `vigente`, `vencido`, `cancelado`, `en renovacion`)
- `url_documento` (nullable), `observaciones` (nullable)

### 7.3. Evaluación (`evaluaciones`)

- Relación: `proveedor` (FK) y `contrato` (FK)
- `periodo_evaluacion`
- Criterios numéricos: `calidad`, `cumplimiento_tiempos`, `precio_competitivo`, `servicio_postventa`
- `puntaje_total`
- `evaluador_id`
- `fecha_evaluacion`

### 7.4. Cotización (`cotizaciones`)

- Relación: `proveedor` (FK)
- `descripcion`
- `precio_unitario`
- `condiciones_comerciales` (nullable)
- `vigencia_cotizacion`
- `fecha_cotizacion`
- `estado` (por defecto `"activa"`, opciones: `activa`, `expirada`, `aceptada`, `rechazada`)

### 7.5. Documento del proveedor (`documentos_proveedor`)

- Relación: `proveedor` (FK)
- `tipo_documento` (opciones: `rut`, `camara_comercio`, `certificacion`, `poliza`)
- `nombre_documento`
- `url_archivo`
- `fecha_emision`, `fecha_vencimiento`
- `estado` (por defecto `"vigente"`, opciones: `vigente`, `vencido`, `por_vencer`)
- `fecha_carga`

## 8. API REST (rutas)

Fuente: `app/routes/provider.py`.

Prefijo: `/api/v1` (router con `tags=["proveedores"]`).

### 8.1. Proveedores

- `POST   /api/v1/proveedores`
- `GET    /api/v1/proveedores/{proveedor_id}`
- `GET    /api/v1/proveedores`
- `PUT    /api/v1/proveedores/{proveedor_id}`
- `POST   /api/v1/proveedores/{proveedor_id}/desactivar`

### 8.2. Contratos

- `POST   /api/v1/contratos`
- `GET    /api/v1/contratos/{contrato_id}`
- `GET    /api/v1/proveedores/{proveedor_id}/contratos`
- `PUT    /api/v1/contratos/{contrato_id}`
- `GET    /api/v1/contratos/proximos-vencer`

### 8.3. Evaluaciones

- `POST   /api/v1/evaluaciones`
- `GET    /api/v1/proveedores/{proveedor_id}/evaluaciones`

### 8.4. Cotizaciones

- `POST   /api/v1/cotizaciones`
- `PUT    /api/v1/cotizaciones/{cotizacion_id}`
- `GET    /api/v1/cotizaciones/comparar?descripcion=...`

### 8.5. Documentos

- `POST   /api/v1/documentos`
- `GET    /api/v1/proveedores/{proveedor_id}/documentos`
- `GET    /api/v1/documentos/proximos-vencer`

## 9. Formato de respuesta estándar y trazabilidad

Fuente: `app/utils/core.py`.

- Se genera un `request_id` con formato: `PRV-{timestamp}-{random}`.
- Las respuestas siguen la estructura:

```json
{
  "request_id": "PRV-1740000000-a3f8b2",
  "success": true,
  "data": {},
  "message": "Descripción de la operación",
  "timestamp": "2026-04-20T15:30:45.123456"
}
```

Middlewares (fuente: `app/middleware.py`):

- `RequestIDMiddleware`:
  - Reutiliza `X-Request-ID` si viene en headers; si no, genera uno nuevo.
  - Propaga el header `X-Request-ID` en la respuesta.
- `LoggingMiddleware`:
  - Calcula duración y agrega `X-Process-Time`.

## 10. Reglas de negocio implementadas (lógica)

Fuente: `app/services/provider.py` y modelos.

- Unicidad de NIT (`Proveedor.nit` y validación previa en `ProveedorService.crear_proveedor`).
- Unicidad de número de contrato (validación previa en `ContratoService.crear_contrato`).
- Cálculo de `contrato_vigente` por proveedor (`ProveedorService.verificar_contrato_vigente`).
- Puntaje de evaluación:
  - `puntaje_total` de evaluación = promedio de 4 criterios.
  - `puntaje_evaluacion` del proveedor = promedio histórico de evaluaciones.
- Control de vigencia de documentos: se calcula estado (`vigente` / `vencido` / `por_vencer`) según `fecha_vencimiento`.
- Alertas (vía `NotificacionesClient`):
  - Contratos próximos a vencer.
  - Documentos próximos a vencer.
  - Puntaje bajo (< 3.0).

## 11. Integración con otros microservicios (clientes HTTP)

Fuente: `app/clients.py` y `app/dependencies.py`.

Clientes implementados:

- `AuthClient.validate_session(token)` → `ms-autenticacion` (`/api/v1/sesiones/validar`)
- `RolesClient.validate_permission(role_id, permission_code)` → `ms-roles` (`/api/v1/permisos/validar`) con `X-App-Token`
- `NotificacionesClient.enviar_alerta(...)` → `ms-notificaciones` (`/api/v1/notificaciones/alerta`) con `X-App-Token`
- `AuditoriaClient.registrar_log(...)` → `ms-auditoria` (`/api/v1/logs`) con `X-App-Token`

Nota: en `GUIA_INTEGRACION.md` se muestra un ejemplo para integrar validación de sesión/permisos y auditoría dentro de los endpoints. En el archivo `app/routes/provider.py` del repositorio, las rutas están definidas de forma sincrónica y no llaman estos `dependencies` por defecto.

## 12. Ejemplos de payloads

Fuente: `EJEMPLOS_JSON.json`.

- Crear proveedor:

```json
{
  "nit": "900123456-7",
  "razon_social": "Soluciones Tecnológicas XYZ S.A.S.",
  "nombre_contacto": "Carlos Daniel Rodríguez",
  "email": "carlos.rodriguez@soluciones.com",
  "telefono": "+573218765432",
  "direccion": "Calle 10 No 45-67 Apto 501",
  "ciudad": "Santiago de Cali"
}
```

- Crear contrato:

```json
{
  "proveedor_id": 1,
  "numero_contrato": "CTR-2026-001",
  "objeto_contrato": "Suministro de licencias de software mediante acuerdo de suscripción anual con soporte técnico 24/7",
  "monto_total": 5000000,
  "fecha_inicio": "2026-01-15",
  "fecha_fin": "2027-01-15",
  "url_documento": "https://storage.example.com/contratos/CTR-2026-001.pdf",
  "observaciones": "Incluye soporte prioritario para 5 usuarios administrativos"
}
```

## 13. Referencias internas del repositorio

- `README.md`
- `INICIO_RAPIDO.md`
- `DOCUMENTACION_TECNICA.md`
- `GUIA_INTEGRACION.md`

