# Documentación Automática de FastAPI

## Introducción

Este proyecto utiliza **FastAPI**, que genera automáticamente documentación interactiva basada en los docstrings, type hints y esquemas Pydantic del código.

La documentación se actualiza automáticamente cada vez que se modifican los endpoints o esquemas.

## Cómo Acceder a la Documentación

### 1. **Swagger UI** (Interfaz Web Interactiva)

**URL:** `http://localhost:8001/docs`

**Características:**
- Interfaz web moderna y intuitiva
- Explorar todos los endpoints disponibles
- Probar endpoints directamente desde el navegador
- Ver esquemas de request y response
- Ver ejemplos de datos
- Autenticación (si está configurada)

### 2. **ReDoc** (Documentación Alternativa)

**URL:** `http://localhost:8001/redoc`

**Características:**
- Documentación limpia y legible
- Organizada por tags (Proveedores, Contratos, Evaluaciones, etc.)
- Excelente para documentación de referencia
- Mejor para lectura que para pruebas

### 3. **OpenAPI JSON** (Especificación Técnica)

**URL:** `http://localhost:8001/openapi.json`

**Características:**
- Especificación completa en formato OpenAPI 3.0
- Útil para generar clientes automáticos
- Integración con herramientas externas
- Formato estándar de la industria

## Estructura de la Documentación

### Tags (Agrupaciones)

La documentación agrupa los endpoints por funcionalidad:

- **Proveedores**: Crear, actualizar, listar y desactivar proveedores
- **Contratos**: Gestión de contratos con proveedores
- **Evaluaciones**: Evaluación de desempeño de proveedores
- **Cotizaciones**: Registro y comparación de cotizaciones
- **Documentos**: Gestión de documentos de proveedores
- **Health Check**: Estado del servicio

### Información por Endpoint

Cada endpoint documenta:

1. **Descripción General**
   - Qué hace el endpoint
   - Cuándo usarlo

2. **Parámetros**
   - Parámetros de ruta (path)
   - Parámetros de query
   - Body (para POST/PUT)
   - Tipos de datos
   - Restricciones (min, max, pattern, etc.)
   - Ejemplos

3. **Respuestas Posibles**
   - Código HTTP (200, 400, 404, 500, etc.)
   - Descripción
   - Esquema de respuesta
   - Ejemplo de respuesta exitosa

4. **Códigos de Error**
   - 400: Bad Request (datos inválidos)
   - 404: Not Found (recurso no existe)
   - 500: Internal Server Error (error del servidor)

## Ejemplos de Endpoints Documentados

### 1. Crear Proveedor
- **Método:** POST
- **Ruta:** `/api/v1/proveedores`
- **Documentación:**
  - Explica validación de NIT único
  - Muestra estructura de datos requerida
  - Ejemplo de respuesta exitosa

### 2. Listar Evaluaciones de Proveedor
- **Método:** GET
- **Ruta:** `/api/v1/proveedores/{proveedor_id}/evaluaciones`
- **Documentación:**
  - Explica que retorna historial completo
  - Parámetros requeridos
  - Estructura de respuesta

### 3. Registrar Evaluación
- **Método:** POST
- **Ruta:** `/api/v1/evaluaciones`
- **Documentación:**
  - Explica cálculo automático de puntaje
  - Escala 1-5 para cada dimensión
  - Actualización automática de promedio del proveedor

## Esquemas Documentados

### ProveedorCreate
```json
{
  "nit": "123456789-1",
  "razon_social": "Empresa XYZ S.A.",
  "nombre_contacto": "Juan Pérez García",
  "email": "contacto@empresa.com",
  "telefono": "+34 91 234 56 78",
  "direccion": "Calle Principal 123",
  "ciudad": "Madrid"
}
```

### EvaluacionCreate
```json
{
  "proveedor_id": 1,
  "contrato_id": 1,
  "periodo_evaluacion": "Q1 2024",
  "calidad": 5,
  "cumplimiento_tiempos": 4,
  "precio_competitivo": 4,
  "servicio_postventa": 5,
  "evaluador_id": "emp_001"
}
```

## Características de la Documentación

### 1. **Validación Automática**
- FastAPI valida automáticamente según Field() definitions
- Muestra errores claros si los datos no cumplen restricciones
- Ejemplo: campo "calidad" debe estar entre 1 y 5

### 2. **Ejemplos en Vivo**
- Prueba endpoints directamente desde Swagger UI
- Ver respuestas reales en tiempo real
- No necesitas herramientas externas como Postman

### 3. **Esquema de Respuesta Estándar**
Todos los endpoints retornan:
```json
{
  "request_id": "PRV-1704067200-a1b2c3",
  "success": true,
  "data": { /* datos específicos */ },
  "message": "Descripción de lo que sucedió",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 4. **Request ID para Trazabilidad**
- Cada solicitud obtiene un ID único (PRV-timestamp-random)
- Se incluye en logs y respuestas
- Facilita debugging de problemas

### 5. **Headers Personalizados**
- `X-Request-ID`: Identificador de la solicitud
- `X-Process-Time`: Tiempo de procesamiento en segundos

## Cómo Usar la Documentación

### Para Desarrolladores Frontend

1. Ir a `http://localhost:8001/docs`
2. Buscar el endpoint requerido
3. Expandir para ver detalles completos
4. Probar con datos reales
5. Copiar el código generado (curl, Python, etc.)

### Para Integradores

1. Descargar el OpenAPI JSON desde `/openapi.json`
2. Usar herramientas como:
   - `openapi-generator` para generar clientes
   - `swagger-codegen` para generar SDKs
   - Importar en Postman

### Para Testing Manual

1. Abrir Swagger UI (`/docs`)
2. Expandir endpoint a probar
3. Click en "Try it out"
4. Rellenar parámetros
5. Click en "Execute"
6. Ver respuesta en tiempo real

## Información Documentada por Archivo

### main.py
- Información general del servicio
- Health check endpoints
- Detalles del startup

### schemas/provider.py
- Estructura de datos para creación/actualización
- Restricciones de validación (min/max length)
- Ejemplos de datos válidos
- Descripciones de cada campo

### models/models.py
- Descripción de entidades
- Relaciones entre tablas
- Significado de cada campo
- Estados y valores válidos

### services/provider.py
- Lógica de negocio documentada
- Parámetros y retornos de cada método
- Comportamientos especiales
- Excepciones posibles

### routes/provider.py
- Propósito de cada endpoint
- Parámetros detallados
- Respuestas posibles
- Códigos HTTP esperados
- Ejemplos de request/response

## Mejores Prácticas Implementadas

### 1. **Docstrings Claros**
- Cada función/clase tiene documentación
- Explica qué hace, no cómo lo hace
- Incluye ejemplos cuando es relevante

### 2. **Field Descriptions**
- Cada campo Pydantic tiene descripción
- Incluye restricciones (rango, formato)
- Proporciona ejemplos de valores válidos

### 3. **Response Examples**
- Ejemplos de respuestas exitosas y errores
- Estructura JSON clara
- Códigos HTTP apropiados

### 4. **Tags y Organización**
- Endpoints agrupados por funcionalidad
- Fácil de navegar
- Coherente con la lógica de negocio

### 5. **Validación Explícita**
- Field validators documentados
- Restricciones claras
- Mensajes de error informativos

## Integración con Herramientas

### Postman
1. Importar colección desde `/openapi.json`
2. Automáticamente crea todos los endpoints
3. Ejemplos precargados
4. Environment variables configuradas

### VS Code
1. Extensión: REST Client o Thunder Client
2. Usar ejemplos de la documentación
3. Ejecutar requests directamente

### CI/CD
1. Usar OpenAPI spec para validación
2. Generar clientes automáticos
3. Documentar en pipelines

## Actualización de la Documentación

La documentación se actualiza automáticamente cuando:
- Cambias docstrings en funciones
- Modificas esquemas Pydantic
- Cambias descripciones de Field()
- Añades nuevos parámetros
- Modificas status codes

**No necesita reconstruir ni desplegar**, la documentación está en vivo.

## Acceso a la Documentación en Producción

Para producción, la documentación se puede:
- Mantener habilitada (seguridad: por token/API key)
- Deshabilitar en URLs (pero seguir usando internamente)
- Proteger con autenticación HTTP Basic

Configuración en `main.py`:
```python
app = FastAPI(
    docs_url="/docs",      # Habilitar/Deshabilitar
    redoc_url="/redoc",    # Habilitar/Deshabilitar
    openapi_url="/openapi.json"  # Habilitar/Deshabilitar
)
```

## Conclusión

FastAPI proporciona documentación automática, completa y siempre actualizada, eliminando la necesidad de mantener documentación separada. Los desarrolladores pueden confiar en que la documentación es exactamente lo que el código hace.
