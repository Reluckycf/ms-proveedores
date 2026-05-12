from peewee import (
    Model, CharField, IntegerField, DecimalField,
    DateTimeField, ForeignKeyField, TextField, FloatField, DateField
)
from datetime import datetime
from app.config import db


class BaseModel(Model):
    """Modelo base para todas las entidades.
    
    Proporciona campos de auditoría automáticos:
    - created_at: Timestamp de creación
    - updated_at: Timestamp de última modificación
    """
    created_at = DateTimeField(default=datetime.utcnow, help_text="Fecha y hora de creación del registro")
    updated_at = DateTimeField(default=datetime.utcnow, help_text="Fecha y hora de última actualización")

    class Meta:
        database = db


class Proveedor(BaseModel):
    """Entidad que representa un proveedor en el sistema.
    
    Un proveedor es una entidad externa que suministra productos o servicios.
    Almacena información de contacto, ubicación y estado del proveedor.
    
    Atributos:
        nit: Número de Identificación Tributaria (único)
        razon_social: Nombre legal de la empresa
        nombre_contacto: Persona de contacto principal
        email: Correo electrónico para comunicaciones
        telefono: Número de contacto
        direccion: Dirección física
        ciudad: Ubicación geográfica
        estado: Estado operativo (activo/inactivo/suspendido)
        fecha_registro: Cuándo se registró el proveedor
        puntaje_evaluacion: Evaluación promedio del desempeño
    """
    nit = CharField(
        unique=True,
        max_length=20,
        help_text="Número de Identificación Tributaria único del proveedor"
    )
    razon_social = CharField(
        max_length=255,
        help_text="Nombre legal completo de la empresa"
    )
    nombre_contacto = CharField(
        max_length=255,
        help_text="Nombre completo del contacto principal"
    )
    email = CharField(
        max_length=100,
        help_text="Correo electrónico para notificaciones"
    )
    telefono = CharField(
        max_length=20,
        help_text="Número de teléfono de contacto"
    )
    direccion = CharField(
        max_length=255,
        help_text="Dirección física completa"
    )
    ciudad = CharField(
        max_length=100,
        help_text="Ciudad o municipio"
    )
    estado = CharField(
        default="activo",
        max_length=20,
        choices=["activo", "inactivo", "suspendido"],
        help_text="Estado actual del proveedor"
    )
    fecha_registro = DateField(
        default=datetime.now,
        help_text="Fecha de registro en el sistema"
    )
    puntaje_evaluacion = FloatField(
        default=0.0,
        help_text="Puntaje de evaluación promedio (0-5)"
    )

    class Meta:
        table_name = "proveedores"
        indexes = (
            (("nit",), True),  # Índice único en NIT
            (("estado",), False),  # Índice en estado para búsquedas frecuentes
        )


class Contrato(BaseModel):
    """Entidad que representa un contrato con un proveedor.
    
    Un contrato define los términos y condiciones de la relación comercial
    con un proveedor, incluyendo monto, vigencia y objeto.
    
    Atributos:
        proveedor: Referencia al proveedor (clave foránea)
        numero_contrato: Identificador único del contrato
        objeto_contrato: Descripción del objeto del contrato
        monto_total: Valor económico total
        fecha_inicio: Cuándo comienza el contrato
        fecha_fin: Cuándo vence el contrato
        estado: Estado del contrato (vigente/vencido/cancelado/en renovación)
        url_documento: URL del documento del contrato
        observaciones: Notas adicionales
    """
    proveedor = ForeignKeyField(
        Proveedor,
        backref="contratos",
        help_text="Referencia al proveedor del contrato"
    )
    numero_contrato = CharField(
        unique=True,
        max_length=50,
        help_text="Número único de identificación del contrato"
    )
    objeto_contrato = TextField(
        help_text="Descripción detallada del objeto del contrato"
    )
    monto_total = DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Monto total en moneda local"
    )
    fecha_inicio = DateField(
        help_text="Fecha de inicio de vigencia"
    )
    fecha_fin = DateField(
        help_text="Fecha de vencimiento"
    )
    estado = CharField(
        default="vigente",
        max_length=20,
        choices=["vigente", "vencido", "cancelado", "en renovacion"],
        help_text="Estado actual del contrato"
    )
    url_documento = TextField(
        null=True,
        help_text="URL o ruta del documento escaneado"
    )
    observaciones = TextField(
        null=True,
        help_text="Observaciones o notas adicionales"
    )

    class Meta:
        table_name = "contratos"
        indexes = (
            (("proveedor_id",), False),  # Índice para búsquedas por proveedor
            (("estado",), False),  # Índice para búsquedas de estado
            (("fecha_fin",), False),  # Índice para búsquedas por vigencia
        )


class Evaluacion(BaseModel):
    """Entidad que registra la evaluación de desempeño de un proveedor.
    
    Almacena evaluaciones periódicas del desempeño del proveedor en múltiples
    dimensiones: calidad, cumplimiento de tiempos, precio y post-venta.
    
    Atributos:
        proveedor: Referencia al proveedor evaluado
        contrato: Referencia al contrato bajo el cual se evalúa
        periodo_evaluacion: Período evaluado (ej: Q1 2024)
        calidad: Evaluación de calidad (1-5)
        cumplimiento_tiempos: Evaluación de cumplimiento (1-5)
        precio_competitivo: Evaluación de competitividad (1-5)
        servicio_postventa: Evaluación de post-venta (1-5)
        puntaje_total: Promedio de todas las evaluaciones
        evaluador_id: Identificación de quien evalúa
        fecha_evaluacion: Cuándo se realizó la evaluación
    """
    proveedor = ForeignKeyField(
        Proveedor,
        backref="evaluaciones",
        help_text="Referencia al proveedor evaluado"
    )
    contrato = ForeignKeyField(
        Contrato,
        backref="evaluaciones",
        help_text="Referencia al contrato asociado"
    )
    periodo_evaluacion = CharField(
        max_length=50,
        help_text="Período evaluado (ej: Q1 2024)"
    )
    calidad = IntegerField(
        help_text="Evaluación de calidad en escala 1-5"
    )
    cumplimiento_tiempos = IntegerField(
        help_text="Evaluación de cumplimiento de tiempos en escala 1-5"
    )
    precio_competitivo = IntegerField(
        help_text="Evaluación de competitividad de precios en escala 1-5"
    )
    servicio_postventa = IntegerField(
        help_text="Evaluación de servicio post-venta en escala 1-5"
    )
    puntaje_total = FloatField(
        help_text="Puntaje total (promedio de todas las evaluaciones)"
    )
    evaluador_id = CharField(
        max_length=100,
        help_text="Identificación del evaluador"
    )
    fecha_evaluacion = DateField(
        default=datetime.now,
        help_text="Fecha de la evaluación"
    )

    class Meta:
        table_name = "evaluaciones"
        indexes = (
            (("proveedor_id",), False),
            (("contrato_id",), False),
            (("fecha_evaluacion",), False),
        )


class Cotizacion(BaseModel):
    """Entidad que registra cotizaciones de proveedores.
    
    Una cotización es una propuesta de precio y condiciones comerciales
    para un producto o servicio específico.
    
    Atributos:
        proveedor: Referencia al proveedor
        descripcion: Descripción del producto/servicio
        precio_unitario: Precio unitario ofertado
        condiciones_comerciales: Términos comerciales (forma de pago, descuentos)
        vigencia_cotizacion: Hasta cuándo es válida la cotización
        fecha_cotizacion: Cuándo se creó la cotización
        estado: Estado (activa/expirada/aceptada/rechazada)
    """
    proveedor = ForeignKeyField(
        Proveedor,
        backref="cotizaciones",
        help_text="Referencia al proveedor"
    )
    descripcion = TextField(
        help_text="Descripción detallada del producto o servicio"
    )
    precio_unitario = DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Precio unitario en moneda local"
    )
    condiciones_comerciales = TextField(
        null=True,
        help_text="Términos comerciales (forma de pago, descuentos, etc.)"
    )
    vigencia_cotizacion = DateField(
        help_text="Fecha hasta la cual es válida la cotización"
    )
    fecha_cotizacion = DateField(
        default=datetime.now,
        help_text="Fecha de creación de la cotización"
    )
    estado = CharField(
        default="activa",
        max_length=20,
        choices=["activa", "expirada", "aceptada", "rechazada"],
        help_text="Estado actual de la cotización"
    )

    class Meta:
        table_name = "cotizaciones"
        indexes = (
            (("proveedor_id",), False),
            (("estado",), False),
            (("vigencia_cotizacion",), False),
        )


class DocumentoProveedor(BaseModel):
    """Entidad que registra documentos de un proveedor.
    
    Almacena información sobre documentos como RUT, cámara de comercio,
    certificaciones, pólizas, etc., incluyendo vigencia y ubicación.
    
    Atributos:
        proveedor: Referencia al proveedor propietario
        tipo_documento: Tipo de documento (rut/camara_comercio/certificacion/poliza)
        nombre_documento: Nombre descriptivo del documento
        url_archivo: URL o ruta del archivo
        fecha_emision: Cuándo fue emitido
        fecha_vencimiento: Cuándo vence
        estado: Estado (vigente/vencido/por_vencer)
        fecha_carga: Cuándo se cargó el documento
    """
    proveedor = ForeignKeyField(
        Proveedor,
        backref="documentos",
        help_text="Referencia al proveedor propietario del documento"
    )
    tipo_documento = CharField(
        max_length=50,
        choices=["rut", "camara_comercio", "certificacion", "poliza"],
        help_text="Tipo de documento"
    )
    nombre_documento = CharField(
        max_length=255,
        help_text="Nombre descriptivo del documento"
    )
    url_archivo = TextField(
        help_text="URL o ruta del archivo almacenado"
    )
    fecha_emision = DateField(
        help_text="Fecha de emisión del documento"
    )
    fecha_vencimiento = DateField(
        help_text="Fecha de vencimiento"
    )
    estado = CharField(
        default="vigente",
        max_length=20,
        choices=["vigente", "vencido", "por_vencer"],
        help_text="Estado del documento"
    )
    fecha_carga = DateTimeField(
        default=datetime.utcnow,
        help_text="Fecha y hora de carga en el sistema"
    )

    class Meta:
        table_name = "documentos_proveedor"
        indexes = (
            (("proveedor_id",), False),
            (("tipo_documento",), False),
            (("fecha_vencimiento",), False),
        )


def create_tables():
    """Crea todas las tablas en la base de datos.
    
    Se ejecuta durante el inicio de la aplicación.
    Las tablas se crean en orden respetando las dependencias de claves foráneas.
    """
    db.create_tables(
        [Proveedor, Contrato, Evaluacion, Cotizacion, DocumentoProveedor],
        safe=True
    )

    class Meta:
        table_name = "documentos_proveedor"


def create_tables():
    db.create_tables([
        Proveedor, Contrato, Evaluacion, Cotizacion, DocumentoProveedor
    ])
