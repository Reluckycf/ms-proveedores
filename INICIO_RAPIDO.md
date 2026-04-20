# GUÍA RÁPIDA DE INICIO - ms-proveedores [PRV]

## ⚡ Início Rápido (5 minutos)

### Requisitos
- Python 3.8+
- PostgreSQL 12+
- Git (opcional)

### 1️⃣ Preparar Base de Datos

```bash
# Opción A: Linux/Mac con sudo
chmod +x init_db.sh
./init_db.sh

# Opción B: Manual con psql
psql -U postgres
CREATE USER proveedor_user WITH PASSWORD 'proveedor_pass';
CREATE DATABASE ms_proveedores OWNER proveedor_user;
ALTER USER proveedor_user CREATEDB;
\q
```

### 2️⃣ Instalar y Ejecutar

```bash
# Crear virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

El servicio estará en: **http://localhost:8001**

### 3️⃣ Probar API

```bash
# Swagger UI
curl http://localhost:8001/docs

# Health check
curl http://localhost:8001/health

# Crear proveedor
curl -X POST http://localhost:8001/api/v1/proveedores \
  -H "Content-Type: application/json" \
  -d '{
    "nit": "123456789",
    "razon_social": "Empresa XYZ S.A.",
    "nombre_contacto": "Juan Pérez",
    "email": "juan@empresa.com",
    "telefono": "3218765432",
    "direccion": "Calle 123 #45-67",
    "ciudad": "Cali"
  }'
```

---

## 📁 Estructura del Proyecto

```
ms-proveedores/
├── app/
│   ├── models/
│   │   └── models.py              # BD: Proveedor, Contrato, etc
│   ├── routes/provider.py         # Endpoints REST
│   ├── schemas/provider.py        # Validación Pydantic
│   ├── services/provider.py       # Lógica empresarial
│   ├── utils/core.py              # Request ID, respuestas
│   ├── config.py                  # PostgreSQL config
│   ├── middleware.py              # Request/Logging
│   └── logging.py                 # Formato JSON logs
├── main.py                        # FastAPI app
├── requirements.txt               # Dependencias
├── .env                           # Variables entorno
├── install.sh                     # Script instalación
├── init_db.sh                     # Script BD
└── README.md                      # Documentación
```

---

## 🔗 Endpoints Principales

### **Proveedores** 🏢
```
POST   /api/v1/proveedores              Crear
GET    /api/v1/proveedores              Listar todos
GET    /api/v1/proveedores/{id}         Obtener uno
PUT    /api/v1/proveedores/{id}         Actualizar
POST   /api/v1/proveedores/{id}/desactivar
```

### **Contratos** 📋
```
POST   /api/v1/contratos                Crear
GET    /api/v1/contratos/{id}           Obtener
GET    /api/v1/proveedores/{id}/contratos
GET    /api/v1/contratos/proximos-vencer
PUT    /api/v1/contratos/{id}           Actualizar
```

### **Evaluaciones** ⭐
```
POST   /api/v1/evaluaciones             Registrar
GET    /api/v1/proveedores/{id}/evaluaciones
```

### **Cotizaciones** 💰
```
POST   /api/v1/cotizaciones             Registrar
PUT    /api/v1/cotizaciones/{id}        Actualizar
GET    /api/v1/cotizaciones/comparar?descripcion=X
```

### **Documentos** 📄
```
POST   /api/v1/documentos               Registrar
GET    /api/v1/proveedores/{id}/documentos
GET    /api/v1/documentos/proximos-vencer
```

---

## ✔️ Reglas Implementadas

| Código | Regla |
|--------|-------|
| RE-01 | ✅ NIT único por proveedor |
| RE-02 | ✅ Desactivación lógica (no física) |
| RE-03 | ✅ Número contrato único |
| RE-04 | ✅ Puntaje = promedio evaluaciones |
| RE-05 | ✅ Calificaciones 1-5 validadas |
| RE-06 | ✅ Contratos < 30 días detectados |
| RE-07 | ✅ Documentos próximos a vencer |
| RE-08 | ✅ Alertas a ms-notificaciones |
| RE-09 | ✅ Vigencia contrato en respuesta |
| RE-10 | ✅ Comparación lado a lado |

---

## 🔐 Seguridad

- ✅ Request ID único: formato `PRV-{timestamp}-{random}`
- ✅ Respuesta estándar JSON
- ✅ Middleware de trazabilidad
- ✅ Validación Pydantic en entrada
- ✅ Formato ISO 8601 para fechas

---

## 🚀 Próximos Pasos

1. Integrar con **ms-autenticacion** para validar sesiones
2. Conectar con **ms-roles** para permisos
3. Enviar logs a **ms-auditoria**
4. Alertas a **ms-notificaciones**
5. Tests unitarios e integración

---

## 📝 Notas

- La BD se crea automáticamente al startup
- Las credenciales en .env son de desarrollo
- Para producción: cambiar host, usuario y contraseña
- FastAPI genera Swagger automáticamente en `/docs`

---

## 💡 Troubleshooting

**Error: `ModuleNotFoundError: No module named 'dotenv'`**
```bash
pip install python-dotenv
```

**Error: conexión a PostgreSQL rechazada**
```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# O con brew en Mac
brew services start postgresql
```

**Error: puerto 8001 ocupado**
```bash
# Ver qué usa el puerto
lsof -i :8001

# O cambiar en main.py
uvicorn.run(..., port=8002)
```

---

¡El microservicio está listo para desarrollo! 🎉
