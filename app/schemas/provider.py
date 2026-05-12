from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


class ProveedorCreate(BaseModel):
    """Esquema para crear un nuevo proveedor.
    
    Campos requeridos:
        - nit: Número de identificación tributaria único
        - razon_social: Nombre legal de la empresa
        - nombre_contacto: Persona de contacto principal
        - email: Correo electrónico para notificaciones
        - telefono: Número de teléfono de contacto
        - direccion: Dirección física del proveedor
        - ciudad: Ciudad donde opera el proveedor
    """
    nit: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Número de Identificación Tributaria del proveedor",
        example="123456789-1"
    )
    razon_social: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Razón social o nombre legal de la empresa",
        example="Empresa XYZ S.A."
    )
    nombre_contacto: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Nombre completo del contacto principal",
        example="Juan Pérez García"
    )
    email: str = Field(
        ...,
        max_length=100,
        description="Correo electrónico para contacto y notificaciones",
        example="contacto@empresa.com"
    )
    telefono: str = Field(
        ...,
        max_length=20,
        description="Número de teléfono del proveedor",
        example="+34 91 234 56 78"
    )
    direccion: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Dirección física completa del proveedor",
        example="Calle Principal 123, Piso 2"
    )
    ciudad: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Ciudad o municipio donde está ubicado el proveedor",
        example="Madrid"
    )


class ProveedorUpdate(BaseModel):
    """Esquema para actualizar información de un proveedor existente.
    
    Todos los campos son opcionales. Solo se actualizan los campos proporcionados.
    """
    razon_social: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Nueva razón social de la empresa"
    )
    nombre_contacto: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Nuevo nombre del contacto principal"
    )
    email: Optional[str] = Field(
        None,
        max_length=100,
        description="Nuevo correo electrónico de contacto"
    )
    telefono: Optional[str] = Field(
        None,
        max_length=20,
        description="Nuevo número de teléfono"
    )
    direccion: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Nueva dirección física"
    )
    ciudad: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Nueva ciudad de ubicación"
    )
    estado: Optional[str] = Field(
        None,
        description="Nuevo estado del proveedor: activo, inactivo, suspendido"
    )


class ProveedorResponse(BaseModel):
    """Esquema de respuesta con información completa de un proveedor.
    
    Incluye todos los datos del proveedor almacenados en la base de datos.
    """
    id: int = Field(..., description="Identificador único del proveedor")
    nit: str = Field(..., description="Número de Identificación Tributaria")
    razon_social: str = Field(..., description="Razón social de la empresa")
    nombre_contacto: str = Field(..., description="Nombre del contacto principal")
    email: str = Field(..., description="Correo electrónico")
    telefono: str = Field(..., description="Número de teléfono")
    direccion: str = Field(..., description="Dirección física")
    ciudad: str = Field(..., description="Ciudad de ubicación")
    estado: str = Field(..., description="Estado actual: activo, inactivo, suspendido")
    fecha_registro: date = Field(..., description="Fecha de registro en el sistema")
    puntaje_evaluacion: float = Field(..., description="Puntaje de evaluación del proveedor (0-5)")
    contrato_vigente: Optional[bool] = Field(None, description="Indica si el proveedor tiene contrato vigente")

    class Config:
        from_attributes = True


class ContratoCreate(BaseModel):
    """Esquema para crear un nuevo contrato con un proveedor.
    
    Contiene la información esencial del contrato a celebrar.
    """
    proveedor_id: int = Field(
        ...,
        gt=0,
        description="ID del proveedor con el que se celebra el contrato",
        example=1
    )
    numero_contrato: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Número único de identificación del contrato",
        example="CT-2024-001"
    )
    objeto_contrato: str = Field(
        ...,
        min_length=10,
        description="Descripción del objeto y alcance del contrato",
        example="Suministro de materiales de oficina por 12 meses"
    )
    monto_total: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Monto total del contrato en moneda local",
        example="50000.00"
    )
    fecha_inicio: date = Field(
        ...,
        description="Fecha de inicio de vigencia del contrato",
        example="2024-01-01"
    )
    fecha_fin: date = Field(
        ...,
        description="Fecha de vencimiento del contrato",
        example="2024-12-31"
    )
    url_documento: Optional[str] = Field(
        None,
        description="URL o ruta del documento escaneado del contrato"
    )
    observaciones: Optional[str] = Field(
        None,
        description="Observaciones o notas adicionales sobre el contrato"
    )


class ContratoUpdate(BaseModel):
    """Esquema para actualizar información de un contrato existente."""
    objeto_contrato: Optional[str] = Field(
        None,
        description="Nuevo objeto del contrato"
    )
    monto_total: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Nuevo monto total"
    )
    fecha_fin: Optional[date] = Field(
        None,
        description="Nueva fecha de vencimiento"
    )
    estado: Optional[str] = Field(
        None,
        description="Nuevo estado: vigente, vencido, cancelado, en renovación"
    )
    observaciones: Optional[str] = Field(
        None,
        description="Nuevas observaciones"
    )


class ContratoResponse(BaseModel):
    """Esquema de respuesta con información completa de un contrato."""
    id: int = Field(..., description="Identificador único del contrato")
    proveedor_id: int = Field(..., description="ID del proveedor asociado")
    numero_contrato: str = Field(..., description="Número del contrato")
    objeto_contrato: str = Field(..., description="Objeto del contrato")
    monto_total: float = Field(..., description="Monto total del contrato")
    fecha_inicio: date = Field(..., description="Fecha de inicio")
    fecha_fin: date = Field(..., description="Fecha de vencimiento")
    estado: str = Field(..., description="Estado actual del contrato")
    url_documento: Optional[str] = Field(None, description="URL del documento")
    observaciones: Optional[str] = Field(None, description="Observaciones")

    class Config:
        from_attributes = True


class EvaluacionCreate(BaseModel):
    """Esquema para crear una evaluación de desempeño de un proveedor.
    
    Evalúa múltiples dimensiones del desempeño del proveedor en escala 1-5.
    """
    proveedor_id: int = Field(
        ...,
        gt=0,
        description="ID del proveedor a evaluar",
        example=1
    )
    contrato_id: int = Field(
        ...,
        gt=0,
        description="ID del contrato bajo el cual se realiza la evaluación",
        example=1
    )
    periodo_evaluacion: str = Field(
        ...,
        description="Período evaluado (ej: 'Q1 2024', 'Enero 2024')",
        example="Q1 2024"
    )
    calidad: int = Field(
        ...,
        ge=1,
        le=5,
        description="Evaluación de calidad de los productos/servicios (1=Deficiente, 5=Excelente)",
        example=5
    )
    cumplimiento_tiempos: int = Field(
        ...,
        ge=1,
        le=5,
        description="Evaluación de cumplimiento de tiempos de entrega (1=Deficiente, 5=Excelente)",
        example=4
    )
    precio_competitivo: int = Field(
        ...,
        ge=1,
        le=5,
        description="Evaluación de competitividad de precios (1=No competitivo, 5=Muy competitivo)",
        example=4
    )
    servicio_postventa: int = Field(
        ...,
        ge=1,
        le=5,
        description="Evaluación del servicio post-venta (1=Deficiente, 5=Excelente)",
        example=5
    )
    evaluador_id: str = Field(
        ...,
        min_length=3,
        description="ID o nombre del evaluador",
        example="emp_001"
    )


class EvaluacionResponse(BaseModel):
    """Esquema de respuesta con resultados de la evaluación completa."""
    id: int = Field(..., description="Identificador único de la evaluación")
    proveedor_id: int = Field(..., description="ID del proveedor evaluado")
    contrato_id: int = Field(..., description="ID del contrato")
    periodo_evaluacion: str = Field(..., description="Período de evaluación")
    calidad: int = Field(..., description="Puntaje de calidad")
    cumplimiento_tiempos: int = Field(..., description="Puntaje de cumplimiento")
    precio_competitivo: int = Field(..., description="Puntaje de precio")
    servicio_postventa: int = Field(..., description="Puntaje de post-venta")
    puntaje_total: float = Field(..., description="Puntaje total calculado (promedio)")
    evaluador_id: str = Field(..., description="ID del evaluador")
    fecha_evaluacion: date = Field(..., description="Fecha de la evaluación")

    class Config:
        from_attributes = True


class CotizacionCreate(BaseModel):
    """Esquema para crear una cotización de un proveedor.
    
    Registra una propuesta de precio y condiciones comerciales.
    """
    proveedor_id: int = Field(
        ...,
        gt=0,
        description="ID del proveedor que presenta la cotización",
        example=1
    )
    descripcion: str = Field(
        ...,
        min_length=5,
        description="Descripción del producto o servicio cotizado",
        example="Suministro de papel bond tamaño carta, 75 gramos"
    )
    precio_unitario: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Precio unitario en moneda local",
        example="2.50"
    )
    condiciones_comerciales: Optional[str] = Field(
        None,
        description="Condiciones comerciales (forma de pago, descuentos, etc.)"
    )
    vigencia_cotizacion: date = Field(
        ...,
        description="Fecha hasta la cual la cotización es válida",
        example="2024-12-31"
    )


class CotizacionUpdate(BaseModel):
    """Esquema para actualizar el estado de una cotización."""
    estado: Optional[str] = Field(
        None,
        description="Nuevo estado: activa, expirada, aceptada, rechazada"
    )


class CotizacionResponse(BaseModel):
    """Esquema de respuesta con información completa de una cotización."""
    id: int = Field(..., description="Identificador único de la cotización")
    proveedor_id: int = Field(..., description="ID del proveedor")
    descripcion: str = Field(..., description="Descripción del producto/servicio")
    precio_unitario: float = Field(..., description="Precio unitario")
    condiciones_comerciales: Optional[str] = Field(None, description="Condiciones comerciales")
    vigencia_cotizacion: date = Field(..., description="Fecha de vigencia")
    fecha_cotizacion: date = Field(..., description="Fecha de creación de la cotización")
    estado: str = Field(..., description="Estado actual")

    class Config:
        from_attributes = True


class DocumentoProveedorCreate(BaseModel):
    """Esquema para cargar un documento de un proveedor.
    
    Registra documentos como RUT, cámara de comercio, certificaciones, etc.
    """
    proveedor_id: int = Field(
        ...,
        gt=0,
        description="ID del proveedor propietario del documento",
        example=1
    )
    tipo_documento: str = Field(
        ...,
        description="Tipo de documento: rut, camara_comercio, certificacion, poliza",
        example="rut"
    )
    nombre_documento: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Nombre descriptivo del documento",
        example="RUT 2024"
    )
    url_archivo: str = Field(
        ...,
        description="URL o ruta del archivo del documento",
        example="https://storage.ejemplo.com/documentos/123_rut.pdf"
    )
    fecha_emision: date = Field(
        ...,
        description="Fecha de emisión del documento",
        example="2024-01-15"
    )
    fecha_vencimiento: date = Field(
        ...,
        description="Fecha de vencimiento del documento",
        example="2025-01-15"
    )


class DocumentoProveedorResponse(BaseModel):
    """Esquema de respuesta con información completa de un documento."""
    id: int = Field(..., description="Identificador único del documento")
    proveedor_id: int = Field(..., description="ID del proveedor")
    tipo_documento: str = Field(..., description="Tipo de documento")
    nombre_documento: str = Field(..., description="Nombre del documento")
    url_archivo: str = Field(..., description="URL del archivo")
    fecha_emision: date = Field(..., description="Fecha de emisión")
    fecha_vencimiento: date = Field(..., description="Fecha de vencimiento")
    estado: str = Field(..., description="Estado: vigente, vencido, por_vencer")
    fecha_carga: datetime = Field(..., description="Fecha de carga en el sistema")

    class Config:
        from_attributes = True


class CotizacionComparacion(BaseModel):
    """Esquema para comparación de cotizaciones de múltiples proveedores."""
    proveedor: str = Field(
        ...,
        description="Nombre o razón social del proveedor"
    )
    precio_unitario: float = Field(
        ...,
        description="Precio unitario de la cotización"
    )
    condiciones: Optional[str] = Field(
        None,
        description="Condiciones comerciales del proveedor"
    )
    vigencia: date = Field(
        ...,
        description="Fecha de vigencia de la cotización"
    )
