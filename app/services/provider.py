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
    """Servicio de lógica de negocio para gestión de proveedores.
    
    Proporciona métodos para crear, actualizar, consultar y desactivar proveedores.
    Maneja la validación de datos y la persistencia en base de datos.
    """
    
    @staticmethod
    def crear_proveedor(data: ProveedorCreate) -> Proveedor:
        """Crea un nuevo proveedor en el sistema.
        
        Valida que el NIT sea único antes de crear el registro.
        
        Parámetros:
            data: Datos del proveedor a crear
        
        Retorna:
            Proveedor: Objeto del proveedor creado con ID asignado
        
        Excepciones:
            ValueError: Si el NIT ya existe en el sistema
        """
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
        """Obtiene un proveedor específico por su ID.
        
        Parámetros:
            proveedor_id: ID del proveedor a consultar
        
        Retorna:
            Proveedor: Objeto del proveedor o None si no existe
        """
        try:
            return Proveedor.get_by_id(proveedor_id)
        except:
            return None

    @staticmethod
    def listar_proveedores() -> List[Proveedor]:
        """Obtiene lista de todos los proveedores registrados.
        
        Retorna:
            List[Proveedor]: Lista de todos los proveedores en el sistema
        """
        return list(Proveedor.select())

    @staticmethod
    def actualizar_proveedor(
        proveedor_id: int, data: ProveedorUpdate
    ) -> Optional[Proveedor]:
        """Actualiza los datos de un proveedor existente.
        
        Solo actualiza los campos proporcionados en data.
        Actualiza automáticamente el timestamp de updated_at.
        
        Parámetros:
            proveedor_id: ID del proveedor a actualizar
            data: Datos a actualizar (todos opcionales)
        
        Retorna:
            Proveedor: Proveedor actualizado o None si no existe
        """
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
        """Desactiva un proveedor estableciendo su estado a 'inactivo'.
        
        Parámetros:
            proveedor_id: ID del proveedor a desactivar
        
        Retorna:
            Proveedor: Proveedor desactivado o None si no existe
        """
        proveedor = ProveedorService.obtener_proveedor(proveedor_id)
        if not proveedor:
            return None
        
        proveedor.estado = "inactivo"
        proveedor.updated_at = datetime.utcnow()
        proveedor.save()
        return proveedor

    @staticmethod
    def verificar_contrato_vigente(proveedor_id: int) -> bool:
        """Verifica si un proveedor tiene al menos un contrato vigente.
        
        Un contrato vigente es aquel con estado 'vigente' y
        fecha de vencimiento igual o superior a hoy.
        
        Parámetros:
            proveedor_id: ID del proveedor a verificar
        
        Retorna:
            bool: True si tiene contrato vigente, False en caso contrario
        """
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
    """Servicio de lógica de negocio para gestión de contratos.
    
    Proporciona métodos para crear, actualizar, consultar contratos
    y detectar contratos próximos a vencer.
    """
    
    @staticmethod
    def crear_contrato(data: ContratoCreate) -> Contrato:
        """Crea un nuevo contrato en el sistema.
        
        Valida que el número de contrato sea único.
        
        Parámetros:
            data: Datos del contrato a crear
        
        Retorna:
            Contrato: Objeto del contrato creado
        
        Excepciones:
            ValueError: Si el número de contrato ya existe
        """
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
        """Obtiene un contrato específico por su ID.
        
        Parámetros:
            contrato_id: ID del contrato a consultar
        
        Retorna:
            Contrato: Objeto del contrato o None si no existe
        """
        try:
            return Contrato.get_by_id(contrato_id)
        except:
            return None

    @staticmethod
    def listar_contratos_proveedor(proveedor_id: int) -> List[Contrato]:
        """Obtiene todos los contratos de un proveedor específico.
        
        Parámetros:
            proveedor_id: ID del proveedor
        
        Retorna:
            List[Contrato]: Lista de contratos del proveedor
        """
        return list(Contrato.select().where(Contrato.proveedor_id == proveedor_id))

    @staticmethod
    def actualizar_contrato(
        contrato_id: int, data: ContratoUpdate
    ) -> Optional[Contrato]:
        """Actualiza los datos de un contrato existente.
        
        Solo actualiza los campos proporcionados.
        
        Parámetros:
            contrato_id: ID del contrato a actualizar
            data: Datos a actualizar
        
        Retorna:
            Contrato: Contrato actualizado o None si no existe
        """
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
        """Identifica contratos que vencen dentro de los próximos 30 días.
        
        Busca contratos vigentes con fecha de vencimiento en el rango
        [hoy, hoy + 30 días] y envía notificaciones.
        
        Retorna:
            List[Contrato]: Lista de contratos próximos a vencer
        """
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
    """Servicio de lógica de negocio para gestión de evaluaciones de proveedores.
    
    Proporciona métodos para registrar evaluaciones, calcular puntajes
    y detectar proveedores con bajo desempeño.
    """
    
    @staticmethod
    def registrar_evaluacion(data: EvaluacionCreate) -> Evaluacion:
        """Registra una nueva evaluación de desempeño de un proveedor.
        
        Calcula automáticamente el puntaje total como promedio de las
        cuatro dimensiones evaluadas.
        
        Parámetros:
            data: Datos de la evaluación
        
        Retorna:
            Evaluacion: Objeto de la evaluación creada
        """
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
        """Actualiza el puntaje promedio de un proveedor basado en sus evaluaciones.
        
        Calcula el promedio de todos los puntajes de evaluación del proveedor.
        Si el promedio es inferior a 3.0, envía notificación de bajo desempeño.
        
        Parámetros:
            proveedor_id: ID del proveedor
        """
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
        """Obtiene todas las evaluaciones de un proveedor.
        
        Parámetros:
            proveedor_id: ID del proveedor
        
        Retorna:
            List[Evaluacion]: Lista de evaluaciones del proveedor
        """
        return list(Evaluacion.select().where(Evaluacion.proveedor_id == proveedor_id))


class CotizacionService:
    """Servicio de lógica de negocio para gestión de cotizaciones.
    
    Proporciona métodos para registrar cotizaciones, actualizarlas,
    obtenerlas y compararlas entre proveedores.
    """
    
    @staticmethod
    def registrar_cotizacion(data: CotizacionCreate) -> Cotizacion:
        """Registra una nueva cotización en el sistema.
        
        Parámetros:
            data: Datos de la cotización
        
        Retorna:
            Cotizacion: Objeto de la cotización creada
        """
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
        """Obtiene una cotización específica por su ID.
        
        Parámetros:
            cotizacion_id: ID de la cotización
        
        Retorna:
            Cotizacion: Objeto de la cotización o None si no existe
        """
        try:
            return Cotizacion.get_by_id(cotizacion_id)
        except:
            return None

    @staticmethod
    def actualizar_cotizacion(
        cotizacion_id: int, data: CotizacionUpdate
    ) -> Optional[Cotizacion]:
        """Actualiza el estado de una cotización.
        
        Parámetros:
            cotizacion_id: ID de la cotización
            data: Datos a actualizar
        
        Retorna:
            Cotizacion: Cotización actualizada o None si no existe
        """
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
        """Compara cotizaciones de múltiples proveedores para un mismo producto/servicio.
        
        Retorna información normalizada para facilitar la comparación de precios
        y condiciones.
        
        Parámetros:
            descripcion: Descripción del producto/servicio a comparar
        
        Retorna:
            List[CotizacionComparacion]: Lista de cotizaciones comparables
        """
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
    """Servicio de lógica de negocio para gestión de documentos de proveedores.
    
    Proporciona métodos para registrar, consultar y monitorear documentos,
    detectando documentos próximos a vencer.
    """
    
    @staticmethod
    def registrar_documento(data: DocumentoProveedorCreate) -> DocumentoProveedor:
        """Registra un nuevo documento de un proveedor.
        
        Calcula automáticamente el estado del documento basado en su fecha
        de vencimiento.
        
        Parámetros:
            data: Datos del documento
        
        Retorna:
            DocumentoProveedor: Objeto del documento creado
        """
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
        """Obtiene un documento específico por su ID.
        
        Parámetros:
            documento_id: ID del documento
        
        Retorna:
            DocumentoProveedor: Objeto del documento o None si no existe
        """
        try:
            return DocumentoProveedor.get_by_id(documento_id)
        except:
            return None

    @staticmethod
    def listar_documentos_proveedor(proveedor_id: int) -> List[DocumentoProveedor]:
        """Obtiene todos los documentos de un proveedor específico.
        
        Parámetros:
            proveedor_id: ID del proveedor
        
        Retorna:
            List[DocumentoProveedor]: Lista de documentos del proveedor
        """
        return list(
            DocumentoProveedor.select().where(
                DocumentoProveedor.proveedor_id == proveedor_id
            )
        )

    @staticmethod
    def listar_documentos_proximos_vencer() -> List[DocumentoProveedor]:
        """Identifica documentos que vencen dentro de los próximos 30 días.
        
        Busca documentos vigentes o por vencer con fecha de vencimiento
        dentro de los próximos 30 días y envía notificaciones.
        
        Retorna:
            List[DocumentoProveedor]: Lista de documentos próximos a vencer
        """
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
