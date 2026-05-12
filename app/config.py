"""Configuración de la aplicación y conexión a base de datos.

Este módulo gestiona:
- Carga de variables de entorno
- Configuración de la conexión a PostgreSQL
- Inicialización de la base de datos

Variables de entorno:
    DATABASE_URL: URL de conexión PostgreSQL
        Formato: postgresql://usuario:contraseña@host:puerto/base_datos
        Default: postgresql://proveedor_user:proveedor_pass@postgres:5432/ms_proveedores
"""

import os
from dotenv import load_dotenv
from peewee import PostgresqlDatabase

# Cargar variables de entorno desde archivo .env
load_dotenv()

DB_PATH = os.getenv(
    "DATABASE_URL", 
    "postgresql://proveedor_user:proveedor_pass@postgres:5432/ms_proveedores"
)
print(DB_PATH)

# Instancia de la base de datos (sin inicializar)
# Se inicializa dinámicamente en init_db()
db = PostgresqlDatabase(
    None,
    #init_unknown_fields=False,
)


def init_db():
    """Inicializa la conexión a la base de datos PostgreSQL.
    
    Parsea la URL de conexión DATABASE_URL y extrae:
    - Usuario y contraseña
    - Host y puerto
    - Nombre de la base de datos
    
    Luego inicializa la conexión Peewee con estos parámetros.
    
    Formato esperado de DATABASE_URL:
        postgresql://usuario:contraseña@host:puerto/nombre_db
    
    Ejemplo:
        postgresql://proveedor_user:proveedor_pass@postgres:5432/ms_proveedores
    
    Raises:
        peewee.OperationalError: Si no puede conectarse a la base de datos
    """
    params = DB_PATH.replace("postgresql://", "").split("@")
    user_pass = params[0].split(":")
    host_db = params[1].split("/")
    
    db.init(
        database=host_db[1],
        user=user_pass[0],
        password=user_pass[1],
        host=host_db[0].split(":")[0],
        port=5432 if ":" not in host_db[0] else int(host_db[0].split(":")[1]),
    )
