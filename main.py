from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from app.config import init_db
from app.models.models import create_tables
from app.routes.provider import router as proveedor_router
from app.middleware import RequestIDMiddleware, LoggingMiddleware

app = FastAPI(
    title="ms-proveedores [PRV]",
    description="Microservicio de gestión de proveedores",
    version="1.0.0"
)

# Agregar middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.on_event("startup")
def startup_event():
    init_db()
    create_tables()
    print("Base de datos inicializada")


@app.get("/")
def root():
    return {
        "servicio": "ms-proveedores",
        "codigo": "PRV",
        "version": "1.0.0",
        "estado": "activo"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(proveedor_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
