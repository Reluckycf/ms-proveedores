from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
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
from app.dependencies import RoleChecker, registrar_auditoria_bg, get_current_user

router = APIRouter(prefix="/api/v1", tags=["proveedores"])

# Dependencia para administrador
admin_only = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"]))

# ============= PROVEEDORES =============
@router.post("/proveedores", dependencies=[admin_only])
async def crear_proveedor(
    proveedor: ProveedorCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = admin_only
):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        nuevo = await ProveedorService.crear_proveedor(proveedor)
        
        await registrar_auditoria_bg(
            background_tasks, trace_id, "CREAR_PROVEEDOR", "POST", 201, 0,
            user_id=user.get("user_id", "sistema"),
            detail=f"Proveedor creado: {nuevo.razon_social} (NIT: {nuevo.nit})"
        )
        
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
async def obtener_proveedor(proveedor_id: int, request: Request, user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin", "Empleado"]))):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    proveedor = await ProveedorService.obtener_proveedor(proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    contrato_vigente = await ProveedorService.verificar_contrato_vigente(proveedor_id)
    
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

@router.get("/proveedores/{proveedor_id}/contrato/vigente")
async def validar_contrato_vigente(proveedor_id: int, request: Request):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    vigente = await ProveedorService.verificar_contrato_vigente(proveedor_id)
    
    return response.success({
        "proveedor_id": proveedor_id,
        "contrato_vigente": vigente
    })

@router.get("/proveedores")
async def listar_proveedores(request: Request, user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin", "Empleado"]))):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    proveedores = await ProveedorService.listar_proveedores()
    
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

@router.put("/proveedores/{proveedor_id}", dependencies=[admin_only])
async def actualizar_proveedor(
    proveedor_id: int, 
    datos: ProveedorUpdate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = admin_only
):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    actualizado = await ProveedorService.actualizar_proveedor(proveedor_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    await registrar_auditoria_bg(
        background_tasks, trace_id, "ACTUALIZAR_PROVEEDOR", "PUT", 200, 0,
        user_id=user.get("user_id", "sistema"),
        detail=f"Proveedor actualizado: {actualizado.razon_social}"
    )
    
    return response.success(
        {
            "id": actualizado.id,
            "razon_social": actualizado.razon_social,
        },
        "Proveedor actualizado exitosamente"
    )

@router.post("/proveedores/{proveedor_id}/desactivar", dependencies=[admin_only])
async def desactivar_proveedor(
    proveedor_id: int, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = admin_only
):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    desactivado = await ProveedorService.desactivar_proveedor(proveedor_id)
    if not desactivado:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    await registrar_auditoria_bg(
        background_tasks, trace_id, "DESACTIVAR_PROVEEDOR", "POST", 200, 0,
        user_id=user.get("user_id", "sistema"),
        detail=f"Proveedor desactivado: {desactivado.razon_social}"
    )
    
    return response.success(
        {"id": desactivado.id},
        "Proveedor desactivado exitosamente"
    )

# ============= CONTRATOS =============
@router.post("/contratos", dependencies=[admin_only])
async def crear_contrato(
    contrato: ContratoCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = admin_only
):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        nuevo = await ContratoService.crear_contrato(contrato)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "CREAR_CONTRATO", "POST", 201, 0,
            user_id=user.get("user_id", "sistema"),
            detail=f"Contrato creado: {nuevo.numero_contrato} para proveedor ID {nuevo.proveedor_id}"
        )
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

@router.get("/contratos/proximos-vencer")
async def listar_contratos_proximos_vencer(request: Request, user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"]))):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    contratos = await ContratoService.listar_contratos_proximos_vencer()
    
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
@router.post("/evaluaciones", dependencies=[admin_only])
async def registrar_evaluacion(
    evaluacion: EvaluacionCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = admin_only
):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        evaluacion.evaluador_id = user.get("user_id", "sistema")
        nueva = await EvaluacionService.registrar_evaluacion(evaluacion)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_EVALUACION", "POST", 201, 0,
            user_id=user.get("user_id", "sistema"),
            detail=f"Evaluación registrada para proveedor ID {nueva.proveedor_id}. Puntaje: {nueva.puntaje_total}"
        )
        return response.success(
            {
                "id": nueva.id,
                "puntaje_total": nueva.puntaje_total,
            },
            "Evaluación registrada exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= COTIZACIONES =============
@router.post("/cotizaciones", dependencies=[admin_only])
async def registrar_cotizacion(
    cotizacion: CotizacionCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = admin_only
):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        nueva = await CotizacionService.registrar_cotizacion(cotizacion)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_COTIZACION", "POST", 201, 0,
            user_id=user.get("user_id", "sistema"),
            detail=f"Cotización registrada para proveedor ID {nueva.proveedor_id}"
        )
        return response.success(
            {
                "id": nueva.id,
                "precio_unitario": float(nueva.precio_unitario),
            },
            "Cotización registrada exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cotizaciones/comparar")
async def comparar_cotizaciones(descripcion: str, request: Request, user: dict = Depends(get_current_user)):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    comparacion = await CotizacionService.comparar_cotizaciones(descripcion)
    
    return response.success(
        [c.model_dump() for c in comparacion],
        f"Se encontraron {len(comparacion)} cotizaciones"
    )

# ============= DOCUMENTOS =============
@router.post("/documentos", dependencies=[admin_only])
async def registrar_documento(
    documento: DocumentoProveedorCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = admin_only
):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        nuevo = await DocumentoService.registrar_documento(documento)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_DOCUMENTO", "POST", 201, 0,
            user_id=user.get("user_id", "sistema"),
            detail=f"Documento {nuevo.tipo_documento} registrado para proveedor ID {nuevo.proveedor_id}"
        )
        return response.success(
            {
                "id": nuevo.id,
                "tipo_documento": nuevo.tipo_documento,
            },
            "Documento registrado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documentos/proximos-vencer")
async def listar_documentos_proximos_vencer(request: Request, user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"]))):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    documentos = await DocumentoService.listar_documentos_proximos_vencer()
    
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

# ============= ADMIN / AUTOMATIZACIÓN =============
@router.post("/admin/revision-diaria", dependencies=[admin_only])
async def disparar_revision_diaria(
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = admin_only
):
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    # Se ejecuta en background para no bloquear
    background_tasks.add_task(DocumentoService.ejecutar_revision_diaria)
    
    await registrar_auditoria_bg(
        background_tasks, trace_id, "DISPARAR_REVISION_DIARIA", "POST", 202, 0,
        user_id=user.get("user_id", "sistema"),
        detail="Se disparó la revisión manual de vencimientos"
    )
    
    return JSONResponse(
        content=response.success(None, "Revisión diaria disparada en segundo plano", 202),
        status_code=202
    )
