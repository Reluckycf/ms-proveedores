from datetime import datetime, date, timedelta
from app.models.models import Proveedor, Contrato, Evaluacion, Cotizacion, DocumentoProveedor
from app.config import db, init_db

def seed_data():
    init_db()
    
    # Crear tablas si no existen
    db.create_tables([
        Proveedor, Contrato, Evaluacion, Cotizacion, DocumentoProveedor
    ])
    
    if Proveedor.select().count() > 0:
        print("La base de datos ya tiene datos. Omitiendo seed.")
        return

    print("Iniciando carga de datos de prueba...")
    
    # 1. Proveedores
    p1 = Proveedor.create(
        nit="900.123.456-1",
        razon_social="Tecnología Avanzada S.A.S.",
        nombre_contacto="Carlos Pérez",
        email="ventas@tecavanzada.com",
        telefono="3001234567",
        direccion="Calle 100 # 15-20",
        ciudad="Bogotá",
        puntaje_evaluacion=4.5
    )
    
    p2 = Proveedor.create(
        nit="800.987.654-2",
        razon_social="Suministros Globales Ltda.",
        nombre_contacto="Marta Gómez",
        email="contacto@sumiglobal.com",
        telefono="6014445566",
        direccion="Carrera 50 # 80-10",
        ciudad="Medellín",
        puntaje_evaluacion=3.8
    )

    # 2. Contratos
    c1 = Contrato.create(
        proveedor=p1,
        numero_contrato="CONTR-2024-001",
        objeto_contrato="Suministro de equipos de computación para laboratorios",
        monto_total=150000000.00,
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2025, 1, 1),
        estado="vigente"
    )
    
    c2 = Contrato.create(
        proveedor=p2,
        numero_contrato="CONTR-2024-002",
        objeto_contrato="Mantenimiento de aires acondicionados",
        monto_total=45000000.00,
        fecha_inicio=date(2024, 2, 1),
        fecha_fin=date(2024, 12, 31),
        estado="vigente"
    )

    # 3. Documentos
    DocumentoProveedor.create(
        proveedor=p1,
        tipo_documento="rut",
        nombre_documento="RUT_2024.pdf",
        url_archivo="https://storage.erp.edu/docs/p1/rut.pdf",
        fecha_emision=date(2024, 1, 1),
        fecha_vencimiento=date(2025, 1, 1),
        estado="vigente"
    )
    
    DocumentoProveedor.create(
        proveedor=p1,
        tipo_documento="camara_comercio",
        nombre_documento="Existencia_Representacion.pdf",
        url_archivo="https://storage.erp.edu/docs/p1/camara.pdf",
        fecha_emision=date(2024, 1, 1),
        fecha_vencimiento=date(2024, 8, 1), # Próximo a vencer
        estado="vigente"
    )

    # 4. Evaluaciones
    Evaluacion.create(
        proveedor=p1,
        contrato=c1,
        periodo_evaluacion="Q1-2024",
        calidad=5,
        cumplimiento_tiempos=4,
        precio_competitivo=4,
        servicio_postventa=5,
        puntaje_total=4.5,
        evaluador_id="USR-ADMIN-01"
    )

    # 5. Cotizaciones
    Cotizacion.create(
        proveedor=p1,
        descripcion="Portátil Intel i7, 16GB RAM, 512GB SSD",
        precio_unitario=3500000.00,
        condiciones_comerciales="Garantía 3 años",
        vigencia_cotizacion=date(2024, 12, 31)
    )
    
    Cotizacion.create(
        proveedor=p2,
        descripcion="Mantenimiento preventivo aire 12000 BTU",
        precio_unitario=150000.00,
        condiciones_comerciales="Pago a 30 días",
        vigencia_cotizacion=date(2024, 11, 30)
    )

    print("Carga de datos completada exitosamente.")

if __name__ == "__main__":
    seed_data()
