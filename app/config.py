import os
from dotenv import load_dotenv
from peewee import PostgresqlDatabase

load_dotenv()

DB_PATH = os.getenv(
    "DATABASE_URL", 
    "postgresql://proveedor_user:proveedor_pass@postgres:5432/ms_proveedores"
)
print(DB_PATH)

db = PostgresqlDatabase(
    None,
    #init_unknown_fields=False,
)


def init_db():
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
