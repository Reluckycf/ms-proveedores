from peewee import (
    Model, CharField, IntegerField, DecimalField,
    DateTimeField, ForeignKeyField, TextField, FloatField, DateField
)
from datetime import datetime
from app.config import db


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = db


class Proveedor(BaseModel):
    nit = CharField(unique=True, max_length=20)
    razon_social = CharField(max_length=255)
    nombre_contacto = CharField(max_length=255)
    email = CharField(max_length=100)
    telefono = CharField(max_length=20)
    direccion = CharField(max_length=255)
    ciudad = CharField(max_length=100)
    estado = CharField(
        default="activo",
        choices=["activo", "inactivo", "suspendido"]
    )
    fecha_registro = DateField(default=datetime.now)
    puntaje_evaluacion = FloatField(default=0.0)

    class Meta:
        table_name = "proveedores"


class Contrato(BaseModel):
    proveedor = ForeignKeyField(Proveedor, backref="contratos")
    numero_contrato = CharField(unique=True, max_length=50)
    objeto_contrato = TextField()
    monto_total = DecimalField(max_digits=15, decimal_places=2)
    fecha_inicio = DateField()
    fecha_fin = DateField()
    estado = CharField(
        default="vigente",
        choices=["vigente", "vencido", "cancelado", "en renovacion"]
    )
    url_documento = TextField(null=True)
    observaciones = TextField(null=True)

    class Meta:
        table_name = "contratos"


class Evaluacion(BaseModel):
    proveedor = ForeignKeyField(Proveedor, backref="evaluaciones")
    contrato = ForeignKeyField(Contrato, backref="evaluaciones")
    periodo_evaluacion = CharField(max_length=50)
    calidad = IntegerField()
    cumplimiento_tiempos = IntegerField()
    precio_competitivo = IntegerField()
    servicio_postventa = IntegerField()
    puntaje_total = FloatField()
    evaluador_id = CharField(max_length=100)
    fecha_evaluacion = DateField(default=datetime.now)

    class Meta:
        table_name = "evaluaciones"


class Cotizacion(BaseModel):
    proveedor = ForeignKeyField(Proveedor, backref="cotizaciones")
    descripcion = TextField()
    precio_unitario = DecimalField(max_digits=15, decimal_places=2)
    condiciones_comerciales = TextField(null=True)
    vigencia_cotizacion = DateField()
    fecha_cotizacion = DateField(default=datetime.now)
    estado = CharField(
        default="activa",
        choices=["activa", "expirada", "aceptada", "rechazada"]
    )

    class Meta:
        table_name = "cotizaciones"


class DocumentoProveedor(BaseModel):
    proveedor = ForeignKeyField(Proveedor, backref="documentos")
    tipo_documento = CharField(
        choices=["rut", "camara_comercio", "certificacion", "poliza"]
    )
    nombre_documento = CharField(max_length=255)
    url_archivo = TextField()
    fecha_emision = DateField()
    fecha_vencimiento = DateField()
    estado = CharField(
        default="vigente",
        choices=["vigente", "vencido", "por_vencer"]
    )
    fecha_carga = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "documentos_proveedor"


def create_tables():
    db.create_tables([
        Proveedor, Contrato, Evaluacion, Cotizacion, DocumentoProveedor
    ])
