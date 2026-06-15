from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from app.utils.core import StandardResponse
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
import time

router = APIRouter(prefix="/api/v1", tags=["proveedores"])

# ============= PROVEEDORES =============
@router.post("/proveedores")
async def crear_proveedor(
    proveedor: ProveedorCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_CREATE_PROVEEDOR"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        nuevo = await ProveedorService.crear_proveedor(proveedor)

        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "CREAR_PROVEEDOR", "POST", 201, duration_ms,
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
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "CREAR_PROVEEDOR", "POST", 400, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error al crear proveedor: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "CREAR_PROVEEDOR", "POST", 500, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error interno al crear proveedor: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/proveedores/{proveedor_id}")
async def obtener_proveedor(
    proveedor_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin", "Empleado"], permission_code="PRV_READ_PROVEEDOR"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    proveedor = await ProveedorService.obtener_proveedor(proveedor_id)
    if not proveedor:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "OBTENER_PROVEEDOR", "GET", 404, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Proveedor ID {proveedor_id} no encontrado"
        )
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    contrato_vigente = await ProveedorService.verificar_contrato_vigente(proveedor_id)
    
    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "OBTENER_PROVEEDOR", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Información del proveedor {proveedor.razon_social} consultada"
    )
    
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
async def validar_contrato_vigente(
    proveedor_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    vigente = await ProveedorService.verificar_contrato_vigente(proveedor_id)
    
    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "VALIDAR_CONTRATO_VIGENTE", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Verificación de contrato vigente para proveedor ID {proveedor_id}: {vigente}"
    )
    
    return response.success({
        "proveedor_id": proveedor_id,
        "contrato_vigente": vigente
    })

@router.get("/proveedores")
async def listar_proveedores(
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin", "Empleado"], permission_code="PRV_READ_PROVEEDOR"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    proveedores = await ProveedorService.listar_proveedores()
    
    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "LISTAR_PROVEEDORES", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Se listaron {len(proveedores)} proveedores"
    )
    
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
async def actualizar_proveedor(
    proveedor_id: int, 
    datos: ProveedorUpdate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_UPDATE_PROVEEDOR"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    actualizado = await ProveedorService.actualizar_proveedor(proveedor_id, datos)
    if not actualizado:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "ACTUALIZAR_PROVEEDOR", "PUT", 404, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Proveedor ID {proveedor_id} no encontrado"
        )
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "ACTUALIZAR_PROVEEDOR", "PUT", 200, duration_ms,
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

@router.post("/proveedores/{proveedor_id}/desactivar")
async def desactivar_proveedor(
    proveedor_id: int, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_DELETE_PROVEEDOR"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    desactivado = await ProveedorService.desactivar_proveedor(proveedor_id)
    if not desactivado:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "DESACTIVAR_PROVEEDOR", "POST", 404, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Proveedor ID {proveedor_id} no encontrado"
        )
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "DESACTIVAR_PROVEEDOR", "POST", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Proveedor desactivado: {desactivado.razon_social}"
    )
    
    return response.success(
        {"id": desactivado.id},
        "Proveedor desactivado exitosamente"
    )

# ============= CONTRATOS =============
@router.post("/contratos")
async def crear_contrato(
    contrato: ContratoCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_CREATE_CONTRATO"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        nuevo = await ContratoService.crear_contrato(contrato)
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "CREAR_CONTRATO", "POST", 201, duration_ms,
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
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "CREAR_CONTRATO", "POST", 400, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error al crear contrato: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "CREAR_CONTRATO", "POST", 500, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error interno al crear contrato: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contratos/{contrato_id}")
async def obtener_contrato(
    contrato_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_READ_CONTRATO"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)

    contrato = await ContratoService.obtener_contrato(contrato_id)
    if not contrato:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "OBTENER_CONTRATO", "GET", 404, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Contrato ID {contrato_id} no encontrado"
        )
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "OBTENER_CONTRATO", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Contrato {contrato.numero_contrato} consultado"
    )

    return response.success({
        "id": contrato.id,
        "proveedor_id": contrato.proveedor_id,
        "numero_contrato": contrato.numero_contrato,
        "objeto_contrato": contrato.objeto_contrato,
        "monto_total": float(contrato.monto_total),
        "fecha_inicio": str(contrato.fecha_inicio),
        "fecha_fin": str(contrato.fecha_fin),
        "estado": contrato.estado,
        "url_documento": contrato.url_documento,
        "observaciones": contrato.observaciones,
    })

@router.get("/proveedores/{proveedor_id}/contratos")
async def listar_contratos_proveedor(
    proveedor_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin", "Empleado"], permission_code="PRV_READ_CONTRATO"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)

    contratos = await ContratoService.listar_contratos_proveedor(proveedor_id)

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "LISTAR_CONTRATOS_PROVEEDOR", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Se listaron {len(contratos)} contratos del proveedor ID {proveedor_id}"
    )

    return response.success(
        [
            {
                "id": c.id,
                "numero_contrato": c.numero_contrato,
                "objeto_contrato": c.objeto_contrato,
                "monto_total": float(c.monto_total),
                "fecha_inicio": str(c.fecha_inicio),
                "fecha_fin": str(c.fecha_fin),
                "estado": c.estado,
            }
            for c in contratos
        ]
    )

@router.put("/contratos/{contrato_id}")
async def actualizar_contrato(
    contrato_id: int,
    datos: ContratoUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_UPDATE_CONTRATO"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)

    actualizado = await ContratoService.actualizar_contrato(contrato_id, datos)
    if not actualizado:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "ACTUALIZAR_CONTRATO", "PUT", 404, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Contrato ID {contrato_id} no encontrado"
        )
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "ACTUALIZAR_CONTRATO", "PUT", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Contrato {actualizado.numero_contrato} actualizado"
    )

    return response.success(
        {"id": actualizado.id},
        "Contrato actualizado exitosamente"
    )

@router.get("/contratos/proximos-vencer")
async def listar_contratos_proximos_vencer(
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_READ_CONTRATO"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    contratos = await ContratoService.listar_contratos_proximos_vencer()

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "LISTAR_CONTRATOS_PROXIMOS_VENCER", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Se consultaron {len(contratos)} contratos próximos a vencer"
    )
    
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
async def registrar_evaluacion(
    evaluacion: EvaluacionCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_CREATE_EVALUACION"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        evaluacion.evaluador_id = user.get("user_id", "sistema")
        nueva = await EvaluacionService.registrar_evaluacion(evaluacion)
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_EVALUACION", "POST", 201, duration_ms,
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
    except ValueError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_EVALUACION", "POST", 400, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error al registrar evaluación: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_EVALUACION", "POST", 500, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error interno al registrar evaluación: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/proveedores/{proveedor_id}/evaluaciones")
async def listar_evaluaciones_proveedor(
    proveedor_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin", "Empleado"], permission_code="PRV_READ_EVALUACION"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)

    evaluaciones = await EvaluacionService.listar_evaluaciones_proveedor(proveedor_id)

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "LISTAR_EVALUACIONES", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Se listaron {len(evaluaciones)} evaluaciones del proveedor ID {proveedor_id}"
    )

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
async def registrar_cotizacion(
    cotizacion: CotizacionCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_CREATE_COTIZACION"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        nueva = await CotizacionService.registrar_cotizacion(cotizacion)
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_COTIZACION", "POST", 201, duration_ms,
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
    except ValueError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_COTIZACION", "POST", 400, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error al registrar cotización: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_COTIZACION", "POST", 500, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error interno al registrar cotización: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cotizaciones/{cotizacion_id}")
async def obtener_cotizacion(
    cotizacion_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin", "Empleado"], permission_code="PRV_READ_COTIZACION"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)

    cotizacion = await CotizacionService.obtener_cotizacion(cotizacion_id)
    if not cotizacion:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "OBTENER_COTIZACION", "GET", 404, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Cotización ID {cotizacion_id} no encontrada"
        )
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "OBTENER_COTIZACION", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Cotización ID {cotizacion_id} consultada"
    )

    return response.success({
        "id": cotizacion.id,
        "proveedor_id": cotizacion.proveedor_id,
        "descripcion": cotizacion.descripcion,
        "precio_unitario": float(cotizacion.precio_unitario),
        "cantidad": cotizacion.cantidad,
        "unidad_medida": cotizacion.unidad_medida,
        "plazo_entrega": cotizacion.plazo_entrega,
        "condiciones_pago": cotizacion.condiciones_pago,
        "validez_oferta": cotizacion.validez_oferta,
        "estado": cotizacion.estado,
        "fecha_cotizacion": str(cotizacion.fecha_cotizacion),
    })

@router.put("/cotizaciones/{cotizacion_id}")
async def actualizar_cotizacion(
    cotizacion_id: int,
    datos: CotizacionUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_UPDATE_COTIZACION"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)

    actualizada = await CotizacionService.actualizar_cotizacion(cotizacion_id, datos)
    if not actualizada:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "ACTUALIZAR_COTIZACION", "PUT", 404, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Cotización ID {cotizacion_id} no encontrada"
        )
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "ACTUALIZAR_COTIZACION", "PUT", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Cotización ID {cotizacion_id} actualizada a estado {actualizada.estado}"
    )

    return response.success(
        {"id": actualizada.id, "estado": actualizada.estado},
        "Cotización actualizada exitosamente"
    )

@router.get("/cotizaciones/comparar")
async def comparar_cotizaciones(
    descripcion: str,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    comparacion = await CotizacionService.comparar_cotizaciones(descripcion)

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "COMPARAR_COTIZACIONES", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Comparación de cotizaciones para '{descripcion}': {len(comparacion)} resultados"
    )
    
    return response.success(
        [c.model_dump() for c in comparacion],
        f"Se encontraron {len(comparacion)} cotizaciones"
    )

# ============= DOCUMENTOS =============
@router.post("/documentos")
async def registrar_documento(
    documento: DocumentoProveedorCreate, 
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_CREATE_DOCUMENTO"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    try:
        nuevo = await DocumentoService.registrar_documento(documento)
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_DOCUMENTO", "POST", 201, duration_ms,
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
    except ValueError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_DOCUMENTO", "POST", 400, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error al registrar documento: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "REGISTRAR_DOCUMENTO", "POST", 500, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Error interno al registrar documento: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/proveedores/{proveedor_id}/documentos")
async def listar_documentos_proveedor(
    proveedor_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin", "Empleado"], permission_code="PRV_READ_DOCUMENTO"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)

    documentos = await DocumentoService.listar_documentos_proveedor(proveedor_id)

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "LISTAR_DOCUMENTOS_PROVEEDOR", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Se listaron {len(documentos)} documentos del proveedor ID {proveedor_id}"
    )

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

@router.get("/documentos/{documento_id}")
async def obtener_documento(
    documento_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin", "Empleado"], permission_code="PRV_READ_DOCUMENTO"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)

    documento = await DocumentoService.obtener_documento(documento_id)
    if not documento:
        duration_ms = int((time.time() - start_time) * 1000)
        await registrar_auditoria_bg(
            background_tasks, trace_id, "OBTENER_DOCUMENTO", "GET", 404, duration_ms,
            user_id=user.get("user_id", "sistema"),
            detail=f"Documento ID {documento_id} no encontrado"
        )
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "OBTENER_DOCUMENTO", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Documento {documento.tipo_documento} consultado"
    )

    return response.success({
        "id": documento.id,
        "proveedor_id": documento.proveedor_id,
        "tipo": documento.tipo_documento,
        "nombre": documento.nombre_documento,
        "url": documento.url_documento,
        "fecha_emision": str(documento.fecha_emision),
        "fecha_vencimiento": str(documento.fecha_vencimiento),
        "estado": documento.estado,
    })

@router.get("/documentos/proximos-vencer")
async def listar_documentos_proximos_vencer(
    request: Request,
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_READ_DOCUMENTO"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    documentos = await DocumentoService.listar_documentos_proximos_vencer()

    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "LISTAR_DOCUMENTOS_PROXIMOS_VENCER", "GET", 200, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail=f"Se consultaron {len(documentos)} documentos próximos a vencer"
    )
    
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
@router.post("/admin/revision-diaria")
async def disparar_revision_diaria(
    request: Request, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(RoleChecker(allowed_roles=["Administrador", "Admin"], permission_code="PRV_UPDATE_PROVEEDOR"))
):
    start_time = time.time()
    trace_id = request.state.request_id
    response = StandardResponse(trace_id)
    
    # Se ejecuta en background para no bloquear
    background_tasks.add_task(DocumentoService.ejecutar_revision_diaria)
    
    duration_ms = int((time.time() - start_time) * 1000)
    await registrar_auditoria_bg(
        background_tasks, trace_id, "DISPARAR_REVISION_DIARIA", "POST", 202, duration_ms,
        user_id=user.get("user_id", "sistema"),
        detail="Se disparó la revisión manual de vencimientos"
    )
    
    return JSONResponse(
        content=response.success(None, "Revisión diaria disparada en segundo plano", 202),
        status_code=202
    )
