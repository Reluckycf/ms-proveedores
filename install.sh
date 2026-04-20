#!/bin/bash
set -e

echo "================================"
echo "Instalación de ms-proveedores"
echo "================================"

echo ""
echo "1. Creando virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "2. Actualizando pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

echo "3. Instalando dependencias..."
pip install -r requirements.txt > /dev/null 2>&1

echo "4. Verificando imports..."
python test_imports.py

echo ""
echo "================================"
echo "✅ Instalación completada"
echo "================================"
echo ""
echo "Próximos pasos:"
echo "1. Inicializar base de datos PostgreSQL:"
echo "   chmod +x init_db.sh && ./init_db.sh"
echo ""
echo "2. Activar virtual environment y ejecutar:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. Acceder a la documentación API:"
echo "   http://localhost:8001/docs"
