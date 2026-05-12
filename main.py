from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import uvicorn
from app.config import init_db
from app.models.models import create_tables
from app.routes.provider import router as proveedor_router
from app.middleware import RequestIDMiddleware, LoggingMiddleware

app = FastAPI(
    title="ms-proveedores [PRV]",
    description="Microservicio de gestión de proveedores. API RESTful para la administración integral de proveedores, contratos, evaluaciones, cotizaciones y documentos.",
    version="1.0.0",
    contact={
        "name": "Equipo de Proveedores",
        "email": "proveedores@empresa.com"
    },
    license_info={
        "name": "Privado",
    }
)

# Agregar middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.on_event("startup")
def startup_event():
    """Evento de inicio: inicializa la base de datos y crea las tablas necesarias."""
    init_db()
    create_tables()
    print("Base de datos inicializada")


@app.get(
    "/",
    tags=["Health Check"],
    summary="Información del servicio",
    responses={
        200: {
            "description": "Información del servicio",
            "content": {
                "application/json": {
                    "example": {
                        "servicio": "ms-proveedores",
                        "codigo": "PRV",
                        "version": "1.0.0",
                        "estado": "activo"
                    }
                }
            }
        }
    }
)
def root():
    """
    Endpoint raíz que retorna la información básica del microservicio.
    
    Retorna:
        - servicio: Nombre del microservicio
        - codigo: Código identificador del servicio
        - version: Versión actual del API
        - estado: Estado operativo del servicio
    """
    return {
        "servicio": "ms-proveedores",
        "codigo": "PRV",
        "version": "1.0.0",
        "estado": "activo"
    }


@app.get(
    "/health",
    tags=["Health Check"],
    summary="Verificar estado del servicio",
    responses={
        200: {
            "description": "Servicio activo y funcionando correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok"
                    }
                }
            }
        }
    }
)
def health():
    """
    Endpoint de health check para verificar que el servicio está disponible.
    
    Útil para:
    - Verificar disponibilidad del servicio
    - Monitoreo y alertas
    - Balanceadores de carga
    
    Retorna:
        - status: Estado del servicio (ok)
    """
    return {"status": "ok"}


app.include_router(proveedor_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
