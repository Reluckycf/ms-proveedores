#!/usr/bin/env python3

import sys

try:
    print("Verificando imports...")
    
    from app.config import db, init_db
    print("✓ Configuración")
    
    from app.models.models import (
        Proveedor, Contrato, Evaluacion, Cotizacion, DocumentoProveedor
    )
    print("✓ Modelos")
    
    from app.schemas.provider import (
        ProveedorCreate, ProveedorResponse, ContratoCreate
    )
    print("✓ Esquemas")
    
    from app.services.provider import (
        ProveedorService, ContratoService, EvaluacionService
    )
    print("✓ Servicios")
    
    from app.routes.provider import router
    print("✓ Rutas")
    
    from app.utils.core import generate_request_id, StandardResponse
    print("✓ Utilidades")
    
    from app.middleware import RequestIDMiddleware, LoggingMiddleware
    print("✓ Middleware")
    
    from main import app
    print("✓ Aplicación FastAPI")
    
    print("\n✅ Todos los imports exitosos!")
    print("Estructura del proyecto lista para ejecutar.")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
