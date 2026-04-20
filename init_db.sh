#!/bin/bash

DB_USER="proveedor_user"
DB_PASS="proveedor_pass"
DB_NAME="ms_proveedores"
DB_HOST="localhost"

echo "Creando usuario PostgreSQL..."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>/dev/null || echo "Usuario ya existe"

echo "Creando base de datos..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || echo "Base de datos ya existe"

echo "Otorgando permisos..."
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;" 2>/dev/null

echo "Base de datos lista en postgresql://$DB_USER:$DB_PASS@$DB_HOST:5432/$DB_NAME"
