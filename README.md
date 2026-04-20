# ms-proveedores [PRV] - Microservicio de Gestión de Proveedores

Microservicio para la gestión integral de proveedores en el ERP Universitario.

## Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- pip

## Instalación y Ejecución

### 1. Preparar Base de Datos

```bash
chmod +x init_db.sh
./init_db.sh
```

### 2. Instalar Dependencias

```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

### 3. Configurar Ambiente

```bash
cp .env.example .env
```

Editar `.env` si es necesario con tu configuración.

### 4. Iniciar Microservicio

```bash
source venv/bin/activate
python main.py
```

El servicio estará disponible en `http://localhost:8001`

## Documentación API

Una vez ejecutando, acceder a:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Estructura del Proyecto

```
ms-proveedores/
├── app/
│   ├── models/
│   │   └── models.py          # Modelos Peewee
│   ├── routes/
│   │   └── provider.py        # Endpoints REST
│   ├── schemas/
│   │   └── provider.py        # Esquemas Pydantic
│   ├── services/
│   │   └── provider.py        # Lógica de negocio
│   ├── utils/
│   │   └── core.py            # Utilidades
│   └── config.py              # Configuración
├── main.py                    # Aplicación FastAPI
├── requirements.txt           # Dependencias
└── README.md                  # Documentación
```

## Endpoints Principales

### Proveedores
- `POST /api/v1/proveedores` - Crear proveedor
- `GET /api/v1/proveedores` - Listar proveedores
- `GET /api/v1/proveedores/{id}` - Obtener proveedor
- `PUT /api/v1/proveedores/{id}` - Actualizar proveedor
- `POST /api/v1/proveedores/{id}/desactivar` - Desactivar proveedor

### Contratos
- `POST /api/v1/contratos` - Crear contrato
- `GET /api/v1/contratos/{id}` - Obtener contrato
- `GET /api/v1/proveedores/{id}/contratos` - Listar contratos proveedor
- `PUT /api/v1/contratos/{id}` - Actualizar contrato
- `GET /api/v1/contratos/proximos-vencer` - Contratos próximos a vencer (30 días)

### Evaluaciones
- `POST /api/v1/evaluaciones` - Registrar evaluación
- `GET /api/v1/proveedores/{id}/evaluaciones` - Listar evaluaciones

### Cotizaciones
- `POST /api/v1/cotizaciones` - Registrar cotización
- `PUT /api/v1/cotizaciones/{id}` - Actualizar cotización
- `GET /api/v1/cotizaciones/comparar` - Comparar cotizaciones

### Documentos
- `POST /api/v1/documentos` - Registrar documento
- `GET /api/v1/proveedores/{id}/documentos` - Listar documentos
- `GET /api/v1/documentos/proximos-vencer` - Documentos próximos a vencer

## Características Implementadas

✓ CRUD de Proveedores con validación de NIT único
✓ Gestión de Contratos con detección auto de vigencia
✓ Evaluaciones periódicas con cálculo de promedio automático
✓ Cotizaciones con capacidad de comparación
✓ Documentos legales con control de vigencia
✓ Request ID único para trazabilidad (formato: PRV-{timestamp}-{random})
✓ Respuestas estándar JSON
✓ Desactivación lógica de registros
✓ Validaciones de integridad de datos
