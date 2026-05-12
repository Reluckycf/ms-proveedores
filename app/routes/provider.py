from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.utils.core import generate_request_id, StandardResponse
from app.schemas.provider import (
    ProveedorCreate, ProveedorUpdate, ProveedorResponse,
    ContratoCreate, ContratoUpdate, ContratoResponse,
    EvaluacionCreate, EvaluacionResponse,
    CotizacionCreate, CotizacionUpdate, CotizacionResponse,
    DocumentoProveedorCreate, DocumentoProveedorResponse
)
from app.services.provider import (
    ProveedorService, ContratoService, EvaluacionService,
    CotizacionService, DocumentoService
)
from app.models.models import (
    Proveedor, Contrato, Evaluacion, Cotizacion, DocumentoProveedor
)


router = APIRouter(prefix="/api/v1", tags=["Proveedores"])


# ============= PROVEEDORES =============
@router.post(
    "/proveedores",
    summary="Crear nuevo proveedor",
    tags=["Proveedores"],
    status_code=200,
    responses={
        200: {
            "description": "Proveedor creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "request_id": "PRV-1704067200-a1b2c3",
                        "success": True,
                        "data": {
                            "id": 1,
                            "nit": "123456789-1",
                            "razon_social": "Empresa XYZ S.A."
                        },
                        "message": "Proveedor creado exitosamente",
                        "timestamp": "2024-01-01T12:00:00.000000"
                    }
                }
            }
        },
        400: {"description": "NIT duplicado o datos inválidos"},
        500: {"description": "Error interno del servidor"}
    }
)
def crear_proveedor(proveedor: ProveedorCreate):
    """
    Crea un nuevo proveedor en el sistema.
    
    Valida que el NIT sea único. Si ya existe un proveedor con ese NIT,
    retorna un error 400.
    
    Parámetros (en body):
        - nit: Número de identificación tributaria (único)
        - razon_social: Nombre legal de la empresa
        - nombre_contacto: Persona de contacto principal
        - email: Correo electrónico
        - telefono: Número de teléfono
        - direccion: Dirección física
        - ciudad: Ciudad de ubicación
    
    Retorna:
        - Proveedor creado con ID asignado
        - Mensaje de confirmación
        - Request ID para trazabilidad
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    try:
        nuevo = ProveedorService.crear_proveedor(proveedor)
        return response.success(
            {
                "id": nuevo.id,
                "nit": nuevo.nit,
                "razon_social": nuevo.razon_social,
            },
            "Proveedor creado exitosamente"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/proveedores/{proveedor_id}",
    summary="Obtener detalles de un proveedor",
    tags=["Proveedores"],
    status_code=200,
    responses={
        200: {"description": "Información completa del proveedor"},
        404: {"description": "Proveedor no encontrado"}
    }
)
def obtener_proveedor(proveedor_id: int):
    """
    Obtiene la información completa de un proveedor específico.
    
    Incluye:
    - Datos de contacto
    - Datos de ubicación
    - Estado del proveedor
    - Puntaje de evaluación
    - Indicador de contratos vigentes
    
    Parámetros:
        - proveedor_id: ID del proveedor (path parameter)
    
    Retorna:
        - Información completa del proveedor
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    proveedor = ProveedorService.obtener_proveedor(proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    contrato_vigente = ProveedorService.verificar_contrato_vigente(proveedor_id)
    
    return response.success({
        "id": proveedor.id,
        "nit": proveedor.nit,
        "razon_social": proveedor.razon_social,
        "nombre_contacto": proveedor.nombre_contacto,
        "email": proveedor.email,
        "telefono": proveedor.telefono,
        "direccion": proveedor.direccion,
        "ciudad": proveedor.ciudad,
        "estado": proveedor.estado,
        "fecha_registro": str(proveedor.fecha_registro),
        "puntaje_evaluacion": proveedor.puntaje_evaluacion,
        "contrato_vigente": contrato_vigente,
    })


@router.get(
    "/proveedores",
    summary="Listar todos los proveedores",
    tags=["Proveedores"],
    status_code=200,
    responses={
        200: {"description": "Lista de proveedores registrados"}
    }
)
def listar_proveedores():
    """
    Obtiene lista de todos los proveedores registrados en el sistema.
    
    Retorna información resumida de cada proveedor:
    - ID
    - NIT
    - Razón social
    - Email
    - Estado
    - Puntaje de evaluación
    
    Retorna:
        - Lista de proveedores con información resumida
        - Cantidad total de proveedores encontrados
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    proveedores = ProveedorService.listar_proveedores()
    
    return response.success(
        [
            {
                "id": p.id,
                "nit": p.nit,
                "razon_social": p.razon_social,
                "email": p.email,
                "estado": p.estado,
                "puntaje_evaluacion": p.puntaje_evaluacion,
            }
            for p in proveedores
        ],
        f"Se encontraron {len(proveedores)} proveedores"
    )


@router.put(
    "/proveedores/{proveedor_id}",
    summary="Actualizar información de un proveedor",
    tags=["Proveedores"],
    status_code=200,
    responses={
        200: {"description": "Proveedor actualizado exitosamente"},
        404: {"description": "Proveedor no encontrado"}
    }
)
def actualizar_proveedor(proveedor_id: int, datos: ProveedorUpdate):
    """
    Actualiza la información de un proveedor existente.
    
    Solo actualiza los campos proporcionados. Los campos no incluidos
    en la solicitud no se modifican.
    
    Parámetros:
        - proveedor_id: ID del proveedor a actualizar
        - datos (body): Campos a actualizar (todos opcionales)
    
    Retorna:
        - Confirmación de actualización con ID del proveedor
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    actualizado = ProveedorService.actualizar_proveedor(proveedor_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    return response.success(
        {
            "id": actualizado.id,
            "razon_social": actualizado.razon_social,
        },
        "Proveedor actualizado exitosamente"
    )


@router.post(
    "/proveedores/{proveedor_id}/desactivar",
    summary="Desactivar un proveedor",
    tags=["Proveedores"],
    status_code=200,
    responses={
        200: {"description": "Proveedor desactivado exitosamente"},
        404: {"description": "Proveedor no encontrado"}
    }
)
def desactivar_proveedor(proveedor_id: int):
    """
    Desactiva un proveedor estableciendo su estado a 'inactivo'.
    
    Un proveedor desactivado no aparecerá en búsquedas normales,
    pero sus datos históricos (contratos, evaluaciones) se conservan.
    
    Parámetros:
        - proveedor_id: ID del proveedor a desactivar
    
    Retorna:
        - Confirmación de desactivación
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    desactivado = ProveedorService.desactivar_proveedor(proveedor_id)
    if not desactivado:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    return response.success(
        {"id": desactivado.id},
        "Proveedor desactivado exitosamente"
    )


# ============= CONTRATOS =============
@router.post(
    "/contratos",
    summary="Crear nuevo contrato",
    tags=["Contratos"],
    status_code=200,
    responses={
        200: {"description": "Contrato creado exitosamente"},
        400: {"description": "Número de contrato duplicado o datos inválidos"},
        500: {"description": "Error interno del servidor"}
    }
)
def crear_contrato(contrato: ContratoCreate):
    """
    Crea un nuevo contrato con un proveedor.
    
    Valida que el número de contrato sea único en el sistema.
    
    Parámetros (en body):
        - proveedor_id: ID del proveedor
        - numero_contrato: Número único del contrato
        - objeto_contrato: Descripción del objeto del contrato
        - monto_total: Valor total en moneda local
        - fecha_inicio: Fecha de inicio
        - fecha_fin: Fecha de vencimiento
        - url_documento: URL del documento (opcional)
        - observaciones: Notas adicionales (opcional)
    
    Retorna:
        - Contrato creado con ID asignado
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    try:
        nuevo = ContratoService.crear_contrato(contrato)
        return response.success(
            {
                "id": nuevo.id,
                "numero_contrato": nuevo.numero_contrato,
            },
            "Contrato creado exitosamente"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/contratos/{contrato_id}",
    summary="Obtener detalles de un contrato",
    tags=["Contratos"],
    status_code=200,
    responses={
        200: {"description": "Información completa del contrato"},
        404: {"description": "Contrato no encontrado"}
    }
)
def obtener_contrato(contrato_id: int):
    """
    Obtiene la información completa de un contrato específico.
    
    Parámetros:
        - contrato_id: ID del contrato
    
    Retorna:
        - Información completa del contrato incluyendo fechas, montos y estado
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    contrato = ContratoService.obtener_contrato(contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    return response.success({
        "id": contrato.id,
        "numero_contrato": contrato.numero_contrato,
        "objeto_contrato": contrato.objeto_contrato,
        "monto_total": float(contrato.monto_total),
        "fecha_inicio": str(contrato.fecha_inicio),
        "fecha_fin": str(contrato.fecha_fin),
        "estado": contrato.estado,
    })


@router.get(
    "/proveedores/{proveedor_id}/contratos",
    summary="Listar contratos de un proveedor",
    tags=["Contratos"],
    status_code=200,
    responses={
        200: {"description": "Lista de contratos del proveedor"}
    }
)
def listar_contratos_proveedor(proveedor_id: int):
    """
    Obtiene lista de todos los contratos de un proveedor específico.
    
    Parámetros:
        - proveedor_id: ID del proveedor
    
    Retorna:
        - Lista de contratos con información resumida
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    contratos = ContratoService.listar_contratos_proveedor(proveedor_id)
    
    return response.success(
        [
            {
                "id": c.id,
                "numero_contrato": c.numero_contrato,
                "estado": c.estado,
                "fecha_fin": str(c.fecha_fin),
            }
            for c in contratos
        ]
    )


@router.put(
    "/contratos/{contrato_id}",
    summary="Actualizar información de un contrato",
    tags=["Contratos"],
    status_code=200,
    responses={
        200: {"description": "Contrato actualizado exitosamente"},
        404: {"description": "Contrato no encontrado"}
    }
)
def actualizar_contrato(contrato_id: int, datos: ContratoUpdate):
    """
    Actualiza la información de un contrato existente.
    
    Solo actualiza los campos proporcionados.
    
    Parámetros:
        - contrato_id: ID del contrato
        - datos (body): Campos a actualizar
    
    Retorna:
        - Confirmación de actualización
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    actualizado = ContratoService.actualizar_contrato(contrato_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    return response.success(
        {"id": actualizado.id},
        "Contrato actualizado exitosamente"
    )


@router.get(
    "/contratos/proximos-vencer",
    summary="Listar contratos próximos a vencer",
    tags=["Contratos"],
    status_code=200,
    responses={
        200: {"description": "Contratos que vencen en los próximos 30 días"}
    }
)
def listar_contratos_proximos_vencer():
    """
    Identifica contratos vigentes que vencen dentro de los próximos 30 días.
    
    Útil para gestión de renovaciones y alertas de vencimiento.
    Envía notificaciones automáticas a los gestores.
    
    Retorna:
        - Lista de contratos próximos a vencer con información del proveedor
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    contratos = ContratoService.listar_contratos_proximos_vencer()
    
    return response.success(
        [
            {
                "id": c.id,
                "numero_contrato": c.numero_contrato,
                "proveedor": c.proveedor.razon_social,
                "fecha_fin": str(c.fecha_fin),
            }
            for c in contratos
        ],
        f"Se encontraron {len(contratos)} contratos próximos a vencer"
    )


# ============= EVALUACIONES =============
@router.post(
    "/evaluaciones",
    summary="Registrar evaluación de proveedor",
    tags=["Evaluaciones"],
    status_code=200,
    responses={
        200: {"description": "Evaluación registrada exitosamente"},
        500: {"description": "Error interno del servidor"}
    }
)
def registrar_evaluacion(evaluacion: EvaluacionCreate):
    """
    Registra una nueva evaluación de desempeño de un proveedor.
    
    Evalúa cuatro dimensiones en escala 1-5:
    - Calidad: Calidad de productos/servicios
    - Cumplimiento de tiempos: Puntualidad en entregas
    - Precio competitivo: Competitividad de precios
    - Servicio post-venta: Calidad del soporte
    
    El puntaje total se calcula como promedio de estas cuatro dimensiones.
    Actualiza automáticamente el puntaje promedio del proveedor.
    
    Parámetros (en body):
        - proveedor_id: ID del proveedor a evaluar
        - contrato_id: ID del contrato asociado
        - periodo_evaluacion: Período evaluado (ej: Q1 2024)
        - calidad: Calificación 1-5
        - cumplimiento_tiempos: Calificación 1-5
        - precio_competitivo: Calificación 1-5
        - servicio_postventa: Calificación 1-5
        - evaluador_id: ID del evaluador
    
    Retorna:
        - Evaluación creada con puntaje total calculado
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    try:
        nueva = EvaluacionService.registrar_evaluacion(evaluacion)
        return response.success(
            {
                "id": nueva.id,
                "puntaje_total": nueva.puntaje_total,
            },
            "Evaluación registrada exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/proveedores/{proveedor_id}/evaluaciones",
    summary="Listar evaluaciones de un proveedor",
    tags=["Evaluaciones"],
    status_code=200,
    responses={
        200: {"description": "Historial de evaluaciones del proveedor"}
    }
)
def listar_evaluaciones_proveedor(proveedor_id: int):
    """
    Obtiene el historial de evaluaciones de un proveedor.
    
    Retorna todas las evaluaciones realizadas al proveedor ordenadas cronológicamente.
    
    Parámetros:
        - proveedor_id: ID del proveedor
    
    Retorna:
        - Lista de evaluaciones con períodos y puntajes
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    evaluaciones = EvaluacionService.listar_evaluaciones_proveedor(proveedor_id)
    
    return response.success(
        [
            {
                "id": e.id,
                "periodo": e.periodo_evaluacion,
                "puntaje_total": e.puntaje_total,
                "fecha": str(e.fecha_evaluacion),
            }
            for e in evaluaciones
        ]
    )


# ============= COTIZACIONES =============
@router.post(
    "/cotizaciones",
    summary="Registrar nueva cotización",
    tags=["Cotizaciones"],
    status_code=200,
    responses={
        200: {"description": "Cotización registrada exitosamente"},
        500: {"description": "Error interno del servidor"}
    }
)
def registrar_cotizacion(cotizacion: CotizacionCreate):
    """
    Registra una nueva cotización de un proveedor.
    
    Una cotización es una propuesta de precio y condiciones comerciales
    para un producto o servicio específico.
    
    Parámetros (en body):
        - proveedor_id: ID del proveedor que cotiza
        - descripcion: Descripción del producto/servicio
        - precio_unitario: Precio unitario ofertado
        - condiciones_comerciales: Términos comerciales (opcional)
        - vigencia_cotizacion: Hasta cuándo es válida la cotización
    
    Retorna:
        - Cotización creada con ID asignado
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    try:
        nueva = CotizacionService.registrar_cotizacion(cotizacion)
        return response.success(
            {
                "id": nueva.id,
                "precio_unitario": float(nueva.precio_unitario),
            },
            "Cotización registrada exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/cotizaciones/{cotizacion_id}",
    summary="Actualizar estado de una cotización",
    tags=["Cotizaciones"],
    status_code=200,
    responses={
        200: {"description": "Cotización actualizada exitosamente"},
        404: {"description": "Cotización no encontrada"}
    }
)
def actualizar_cotizacion(cotizacion_id: int, datos: CotizacionUpdate):
    """
    Actualiza el estado de una cotización.
    
    Estados posibles: activa, expirada, aceptada, rechazada
    
    Parámetros:
        - cotizacion_id: ID de la cotización
        - datos (body): Nuevo estado
    
    Retorna:
        - Confirmación de actualización
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    actualizada = CotizacionService.actualizar_cotizacion(cotizacion_id, datos)
    if not actualizada:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    return response.success(
        {"id": actualizada.id},
        "Cotización actualizada exitosamente"
    )


@router.get(
    "/cotizaciones/comparar",
    summary="Comparar cotizaciones de múltiples proveedores",
    tags=["Cotizaciones"],
    status_code=200,
    responses={
        200: {"description": "Comparativa de cotizaciones"}
    }
)
def comparar_cotizaciones(descripcion: str = Query(..., description="Descripción del producto/servicio")):
    """
    Compara cotizaciones de múltiples proveedores para un mismo producto/servicio.
    
    Facilita la toma de decisiones de compra al mostrar lado a lado
    precios y condiciones de diferentes proveedores.
    
    Parámetros:
        - descripcion: Descripción del producto/servicio a comparar
    
    Retorna:
        - Lista de cotizaciones comparables ordenadas por precio
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    comparacion = CotizacionService.comparar_cotizaciones(descripcion)
    
    return response.success(
        [c.model_dump() for c in comparacion],
        f"Se encontraron {len(comparacion)} cotizaciones"
    )


# ============= DOCUMENTOS =============
@router.post(
    "/documentos",
    summary="Registrar documento de proveedor",
    tags=["Documentos"],
    status_code=200,
    responses={
        200: {"description": "Documento registrado exitosamente"},
        500: {"description": "Error interno del servidor"}
    }
)
def registrar_documento(documento: DocumentoProveedorCreate):
    """
    Registra un documento de un proveedor.
    
    Tipos de documentos soportados:
    - rut: Registro Único Tributario
    - camara_comercio: Certificado de Cámara de Comercio
    - certificacion: Certificaciones o acreditaciones
    - poliza: Pólizas de seguros o garantías
    
    El sistema calcula automáticamente el estado (vigente/vencido/por_vencer)
    basado en la fecha de vencimiento.
    
    Parámetros (en body):
        - proveedor_id: ID del proveedor propietario
        - tipo_documento: Tipo de documento
        - nombre_documento: Nombre descriptivo
        - url_archivo: Ubicación del archivo
        - fecha_emision: Cuándo fue emitido
        - fecha_vencimiento: Cuándo vence
    
    Retorna:
        - Documento creado con estado calculado
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    try:
        nuevo = DocumentoService.registrar_documento(documento)
        return response.success(
            {
                "id": nuevo.id,
                "tipo_documento": nuevo.tipo_documento,
            },
            "Documento registrado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/proveedores/{proveedor_id}/documentos",
    summary="Listar documentos de un proveedor",
    tags=["Documentos"],
    status_code=200,
    responses={
        200: {"description": "Documentos del proveedor"}
    }
)
def listar_documentos_proveedor(proveedor_id: int):
    """
    Obtiene lista de todos los documentos registrados para un proveedor.
    
    Parámetros:
        - proveedor_id: ID del proveedor
    
    Retorna:
        - Lista de documentos con tipo, estado y vigencia
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    documentos = DocumentoService.listar_documentos_proveedor(proveedor_id)
    
    return response.success(
        [
            {
                "id": d.id,
                "tipo": d.tipo_documento,
                "nombre": d.nombre_documento,
                "estado": d.estado,
                "fecha_vencimiento": str(d.fecha_vencimiento),
            }
            for d in documentos
        ]
    )


@router.get(
    "/documentos/proximos-vencer",
    summary="Listar documentos próximos a vencer",
    tags=["Documentos"],
    status_code=200,
    responses={
        200: {"description": "Documentos que vencen en los próximos 30 días"}
    }
)
def listar_documentos_proximos_vencer():
    """
    Identifica documentos que vencen dentro de los próximos 30 días.
    
    Útil para gestión de renovación de documentos y alertas de vencimiento.
    Envía notificaciones automáticas a los gestores.
    
    Retorna:
        - Lista de documentos próximos a vencer con información del proveedor
    """
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    documentos = DocumentoService.listar_documentos_proximos_vencer()
    
    return response.success(
        [
            {
                "id": d.id,
                "proveedor": d.proveedor.razon_social,
                "tipo": d.tipo_documento,
                "fecha_vencimiento": str(d.fecha_vencimiento),
            }
            for d in documentos
        ],
        f"Se encontraron {len(documentos)} documentos próximos a vencer"
    )
