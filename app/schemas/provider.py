from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


class ProveedorCreate(BaseModel):
    nit: str
    razon_social: str
    nombre_contacto: str
    email: str
    telefono: str
    direccion: str
    ciudad: str


class ProveedorUpdate(BaseModel):
    razon_social: Optional[str] = None
    nombre_contacto: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None


class ProveedorResponse(BaseModel):
    id: int
    nit: str
    razon_social: str
    nombre_contacto: str
    email: str
    telefono: str
    direccion: str
    ciudad: str
    estado: str
    fecha_registro: date
    puntaje_evaluacion: float
    contrato_vigente: Optional[bool] = None

    class Config:
        from_attributes = True


class ContratoCreate(BaseModel):
    proveedor_id: int
    numero_contrato: str
    objeto_contrato: str
    monto_total: Decimal
    fecha_inicio: date
    fecha_fin: date
    url_documento: Optional[str] = None
    observaciones: Optional[str] = None


class ContratoUpdate(BaseModel):
    objeto_contrato: Optional[str] = None
    monto_total: Optional[Decimal] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None


class ContratoResponse(BaseModel):
    id: int
    proveedor_id: int
    numero_contrato: str
    objeto_contrato: str
    monto_total: float
    fecha_inicio: date
    fecha_fin: date
    estado: str
    url_documento: Optional[str] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class EvaluacionCreate(BaseModel):
    proveedor_id: int
    contrato_id: int
    periodo_evaluacion: str
    calidad: int = Field(ge=1, le=5)
    cumplimiento_tiempos: int = Field(ge=1, le=5)
    precio_competitivo: int = Field(ge=1, le=5)
    servicio_postventa: int = Field(ge=1, le=5)
    evaluador_id: str


class EvaluacionResponse(BaseModel):
    id: int
    proveedor_id: int
    contrato_id: int
    periodo_evaluacion: str
    calidad: int
    cumplimiento_tiempos: int
    precio_competitivo: int
    servicio_postventa: int
    puntaje_total: float
    evaluador_id: str
    fecha_evaluacion: date

    class Config:
        from_attributes = True


class CotizacionCreate(BaseModel):
    proveedor_id: int
    descripcion: str
    precio_unitario: Decimal
    condiciones_comerciales: Optional[str] = None
    vigencia_cotizacion: date


class CotizacionUpdate(BaseModel):
    estado: Optional[str] = None


class CotizacionResponse(BaseModel):
    id: int
    proveedor_id: int
    descripcion: str
    precio_unitario: float
    condiciones_comerciales: Optional[str] = None
    vigencia_cotizacion: date
    fecha_cotizacion: date
    estado: str

    class Config:
        from_attributes = True


class DocumentoProveedorCreate(BaseModel):
    proveedor_id: int
    tipo_documento: str
    nombre_documento: str
    url_archivo: str
    fecha_emision: date
    fecha_vencimiento: date


class DocumentoProveedorResponse(BaseModel):
    id: int
    proveedor_id: int
    tipo_documento: str
    nombre_documento: str
    url_archivo: str
    fecha_emision: date
    fecha_vencimiento: date
    estado: str
    fecha_carga: datetime

    class Config:
        from_attributes = True


class CotizacionComparacion(BaseModel):
    proveedor: str
    precio_unitario: float
    condiciones: Optional[str] = None
    vigencia: date
