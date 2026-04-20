from fastapi import APIRouter, HTTPException
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


router = APIRouter(prefix="/api/v1", tags=["proveedores"])


# ============= PROVEEDORES =============
@router.post("/proveedores")
def crear_proveedor(proveedor: ProveedorCreate):
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


@router.get("/proveedores/{proveedor_id}")
def obtener_proveedor(proveedor_id: int):
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


@router.get("/proveedores")
def listar_proveedores():
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


@router.put("/proveedores/{proveedor_id}")
def actualizar_proveedor(proveedor_id: int, datos: ProveedorUpdate):
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


@router.post("/proveedores/{proveedor_id}/desactivar")
def desactivar_proveedor(proveedor_id: int):
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
@router.post("/contratos")
def crear_contrato(contrato: ContratoCreate):
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


@router.get("/contratos/{contrato_id}")
def obtener_contrato(contrato_id: int):
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


@router.get("/proveedores/{proveedor_id}/contratos")
def listar_contratos_proveedor(proveedor_id: int):
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


@router.put("/contratos/{contrato_id}")
def actualizar_contrato(contrato_id: int, datos: ContratoUpdate):
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    actualizado = ContratoService.actualizar_contrato(contrato_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    return response.success(
        {"id": actualizado.id},
        "Contrato actualizado exitosamente"
    )


@router.get("/contratos/proximos-vencer")
def listar_contratos_proximos_vencer():
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
@router.post("/evaluaciones")
def registrar_evaluacion(evaluacion: EvaluacionCreate):
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


@router.get("/proveedores/{proveedor_id}/evaluaciones")
def listar_evaluaciones_proveedor(proveedor_id: int):
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
@router.post("/cotizaciones")
def registrar_cotizacion(cotizacion: CotizacionCreate):
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


@router.put("/cotizaciones/{cotizacion_id}")
def actualizar_cotizacion(cotizacion_id: int, datos: CotizacionUpdate):
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    actualizada = CotizacionService.actualizar_cotizacion(cotizacion_id, datos)
    if not actualizada:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    return response.success(
        {"id": actualizada.id},
        "Cotización actualizada exitosamente"
    )


@router.get("/cotizaciones/comparar")
def comparar_cotizaciones(descripcion: str):
    request_id = generate_request_id()
    response = StandardResponse(request_id)
    
    comparacion = CotizacionService.comparar_cotizaciones(descripcion)
    
    return response.success(
        [c.model_dump() for c in comparacion],
        f"Se encontraron {len(comparacion)} cotizaciones"
    )


# ============= DOCUMENTOS =============
@router.post("/documentos")
def registrar_documento(documento: DocumentoProveedorCreate):
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


@router.get("/proveedores/{proveedor_id}/documentos")
def listar_documentos_proveedor(proveedor_id: int):
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


@router.get("/documentos/proximos-vencer")
def listar_documentos_proximos_vencer():
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
