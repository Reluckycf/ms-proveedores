from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any
from decimal import Decimal
import asyncio
from app.models.models import (
    Proveedor, Contrato, Evaluacion, Cotizacion, DocumentoProveedor
)
from app.schemas.provider import (
    ProveedorCreate, ProveedorUpdate, ContratoCreate, ContratoUpdate,
    EvaluacionCreate, CotizacionCreate, CotizacionUpdate, DocumentoProveedorCreate,
    CotizacionComparacion
)
from app.clients import NotificacionesClient


class ProveedorService:
    @staticmethod
    def crear_proveedor(data: ProveedorCreate) -> Proveedor:
        if Proveedor.select().where(Proveedor.nit == data.nit).exists():
            raise ValueError("NIT duplicado")
        
        proveedor = Proveedor.create(
            nit=data.nit,
            razon_social=data.razon_social,
            nombre_contacto=data.nombre_contacto,
            email=data.email,
            telefono=data.telefono,
            direccion=data.direccion,
            ciudad=data.ciudad,
        )
        return proveedor

    @staticmethod
    def obtener_proveedor(proveedor_id: int) -> Optional[Proveedor]:
        try:
            return Proveedor.get_by_id(proveedor_id)
        except:
            return None

    @staticmethod
    def listar_proveedores() -> List[Proveedor]:
        return list(Proveedor.select())

    @staticmethod
    def actualizar_proveedor(
        proveedor_id: int, data: ProveedorUpdate
    ) -> Optional[Proveedor]:
        proveedor = ProveedorService.obtener_proveedor(proveedor_id)
        if not proveedor:
            return None

        actualizar_campos = data.model_dump(exclude_unset=True)
        for campo, valor in actualizar_campos.items():
            setattr(proveedor, campo, valor)
        
        proveedor.updated_at = datetime.utcnow()
        proveedor.save()
        return proveedor

    @staticmethod
    def desactivar_proveedor(proveedor_id: int) -> Optional[Proveedor]:
        proveedor = ProveedorService.obtener_proveedor(proveedor_id)
        if not proveedor:
            return None
        
        proveedor.estado = "inactivo"
        proveedor.updated_at = datetime.utcnow()
        proveedor.save()
        return proveedor

    @staticmethod
    def verificar_contrato_vigente(proveedor_id: int) -> bool:
        hoy = date.today()
        contrato = (
            Contrato.select()
            .where(
                (Contrato.proveedor_id == proveedor_id) &
                (Contrato.estado == "vigente") &
                (Contrato.fecha_fin >= hoy)
            )
            .first()
        )
        return contrato is not None


class ContratoService:
    @staticmethod
    def crear_contrato(data: ContratoCreate) -> Contrato:
        if Contrato.select().where(
            Contrato.numero_contrato == data.numero_contrato
        ).exists():
            raise ValueError("Número de contrato duplicado")
        
        contrato = Contrato.create(
            proveedor_id=data.proveedor_id,
            numero_contrato=data.numero_contrato,
            objeto_contrato=data.objeto_contrato,
            monto_total=data.monto_total,
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            url_documento=data.url_documento,
            observaciones=data.observaciones,
        )
        return contrato

    @staticmethod
    def obtener_contrato(contrato_id: int) -> Optional[Contrato]:
        try:
            return Contrato.get_by_id(contrato_id)
        except:
            return None

    @staticmethod
    def listar_contratos_proveedor(proveedor_id: int) -> List[Contrato]:
        return list(Contrato.select().where(Contrato.proveedor_id == proveedor_id))

    @staticmethod
    def actualizar_contrato(
        contrato_id: int, data: ContratoUpdate
    ) -> Optional[Contrato]:
        contrato = ContratoService.obtener_contrato(contrato_id)
        if not contrato:
            return None

        actualizar_campos = data.model_dump(exclude_unset=True)
        for campo, valor in actualizar_campos.items():
            setattr(contrato, campo, valor)
        
        contrato.updated_at = datetime.utcnow()
        contrato.save()
        return contrato

    @staticmethod
    def listar_contratos_proximos_vencer() -> List[Contrato]:
        ahora = date.today()
        dentro_30_dias = ahora + timedelta(days=30)
        
        contratos = list(
            Contrato.select().where(
                (Contrato.fecha_fin >= ahora) &
                (Contrato.fecha_fin <= dentro_30_dias) &
                (Contrato.estado == "vigente")
            )
        )
        
        for contrato in contratos:
            asyncio.run(
                NotificacionesClient.enviar_contrato_vencimiento(
                    contrato.numero_contrato,
                    contrato.proveedor.razon_social,
                    str(contrato.fecha_fin)
                )
            )
        
        return contratos


class EvaluacionService:
    @staticmethod
    def registrar_evaluacion(data: EvaluacionCreate) -> Evaluacion:
        puntaje_total = (
            data.calidad + data.cumplimiento_tiempos +
            data.precio_competitivo + data.servicio_postventa
        ) / 4.0

        evaluacion = Evaluacion.create(
            proveedor_id=data.proveedor_id,
            contrato_id=data.contrato_id,
            periodo_evaluacion=data.periodo_evaluacion,
            calidad=data.calidad,
            cumplimiento_tiempos=data.cumplimiento_tiempos,
            precio_competitivo=data.precio_competitivo,
            servicio_postventa=data.servicio_postventa,
            puntaje_total=puntaje_total,
            evaluador_id=data.evaluador_id,
        )

        EvaluacionService.actualizar_puntaje_proveedor(data.proveedor_id)
        return evaluacion

    @staticmethod
    def actualizar_puntaje_proveedor(proveedor_id: int):
        evaluaciones = list(
            Evaluacion.select().where(Evaluacion.proveedor_id == proveedor_id)
        )
        if not evaluaciones:
            return

        promedio = sum(e.puntaje_total for e in evaluaciones) / len(evaluaciones)
        proveedor = Proveedor.get_by_id(proveedor_id)
        proveedor.puntaje_evaluacion = promedio
        proveedor.updated_at = datetime.utcnow()
        proveedor.save()
        
        if promedio < 3.0:
            asyncio.run(
                NotificacionesClient.enviar_puntaje_bajo(
                    proveedor.razon_social,
                    promedio
                )
            )

    @staticmethod
    def listar_evaluaciones_proveedor(proveedor_id: int) -> List[Evaluacion]:
        return list(Evaluacion.select().where(Evaluacion.proveedor_id == proveedor_id))


class CotizacionService:
    @staticmethod
    def registrar_cotizacion(data: CotizacionCreate) -> Cotizacion:
        cotizacion = Cotizacion.create(
            proveedor_id=data.proveedor_id,
            descripcion=data.descripcion,
            precio_unitario=data.precio_unitario,
            condiciones_comerciales=data.condiciones_comerciales,
            vigencia_cotizacion=data.vigencia_cotizacion,
        )
        return cotizacion

    @staticmethod
    def obtener_cotizacion(cotizacion_id: int) -> Optional[Cotizacion]:
        try:
            return Cotizacion.get_by_id(cotizacion_id)
        except:
            return None

    @staticmethod
    def actualizar_cotizacion(
        cotizacion_id: int, data: CotizacionUpdate
    ) -> Optional[Cotizacion]:
        cotizacion = CotizacionService.obtener_cotizacion(cotizacion_id)
        if not cotizacion:
            return None

        if data.estado:
            cotizacion.estado = data.estado
        cotizacion.updated_at = datetime.utcnow()
        cotizacion.save()
        return cotizacion

    @staticmethod
    def comparar_cotizaciones(descripcion: str) -> List[CotizacionComparacion]:
        cotizaciones = list(
            Cotizacion.select()
            .where(Cotizacion.descripcion == descripcion)
            .join(Proveedor)
        )
        return [
            CotizacionComparacion(
                proveedor=c.proveedor.razon_social,
                precio_unitario=float(c.precio_unitario),
                condiciones=c.condiciones_comerciales,
                vigencia=c.vigencia_cotizacion,
            )
            for c in cotizaciones
        ]


class DocumentoService:
    @staticmethod
    def registrar_documento(data: DocumentoProveedorCreate) -> DocumentoProveedor:
        hoy = date.today()
        estado = (
            "vigente" if data.fecha_vencimiento > hoy
            else "vencido" if data.fecha_vencimiento < hoy
            else "por_vencer"
        )

        documento = DocumentoProveedor.create(
            proveedor_id=data.proveedor_id,
            tipo_documento=data.tipo_documento,
            nombre_documento=data.nombre_documento,
            url_archivo=data.url_archivo,
            fecha_emision=data.fecha_emision,
            fecha_vencimiento=data.fecha_vencimiento,
            estado=estado,
        )
        return documento

    @staticmethod
    def obtener_documento(documento_id: int) -> Optional[DocumentoProveedor]:
        try:
            return DocumentoProveedor.get_by_id(documento_id)
        except:
            return None

    @staticmethod
    def listar_documentos_proveedor(proveedor_id: int) -> List[DocumentoProveedor]:
        return list(
            DocumentoProveedor.select().where(
                DocumentoProveedor.proveedor_id == proveedor_id
            )
        )

    @staticmethod
    def listar_documentos_proximos_vencer() -> List[DocumentoProveedor]:
        ahora = date.today()
        dentro_30_dias = ahora + timedelta(days=30)
        
        documentos = list(
            DocumentoProveedor.select().where(
                (DocumentoProveedor.fecha_vencimiento >= ahora) &
                (DocumentoProveedor.fecha_vencimiento <= dentro_30_dias) &
                (DocumentoProveedor.estado.in_(["vigente", "por_vencer"]))
            )
        )
        
        for documento in documentos:
            asyncio.run(
                NotificacionesClient.enviar_documento_vencimiento(
                    documento.proveedor.razon_social,
                    documento.tipo_documento,
                    str(documento.fecha_vencimiento)
                )
            )
        
        return documentos
