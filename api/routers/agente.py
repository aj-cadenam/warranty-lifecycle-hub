from fastapi import APIRouter, Depends, Query, UploadFile, File
from pydantic import BaseModel
from datetime import date
import tempfile
import os
from src.solicitudes.domain.entities import EstadoSolicitud
from config.dependencies import (
    get_llm_adapter,
    get_embedding_adapter,
    get_solicitud_repo,
    get_garantia_repo,
    get_ocr_adapter,
    get_trazabilidad_repo,
    get_borrador_repo,
    get_evento_seguimiento_repo,
    get_vector_store,
    get_email_reader,
    get_orquestar_acciones,
)
from config.settings import settings
from src.agente.application.procesar_documento import ProcesarDocumento
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from src.seguimiento.application.verificar_estado_semanal import VerificarEstadoSemanal

router = APIRouter()


class ProcesarDocumentoRequest(BaseModel):
    pdf_path: str


class SolicitudBrief(BaseModel):
    id: str
    equipo_id: str
    descripcion_falla: str
    estado: EstadoSolicitud
    fecha_reporte: date


def _procesar_pdf(pdf_path: str, ocr, llm, embedding, vector_store, solicitud_repo, garantia_repo):
    crear_solicitud = CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo)
    caso_uso = ProcesarDocumento(
        ocr=ocr, llm=llm, embedding=embedding,
        vector_store=vector_store, crear_solicitud=crear_solicitud,
    )
    return caso_uso.execute(pdf_path=pdf_path)


@router.post("/procesar-documento/upload")
def procesar_documento_upload(
    file: UploadFile = File(...),
    ocr=Depends(get_ocr_adapter),
    llm=Depends(get_llm_adapter),
    embedding=Depends(get_embedding_adapter),
    vector_store=Depends(get_vector_store),
    solicitud_repo=Depends(get_solicitud_repo),
    garantia_repo=Depends(get_garantia_repo),
):
    suffix = os.path.splitext(file.filename or "doc.pdf")[1] or ".pdf"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    try:
        decision, solicitud = _procesar_pdf(
            tmp_path, ocr, llm, embedding, vector_store, solicitud_repo, garantia_repo
        )
    finally:
        os.unlink(tmp_path)
    solicitud_data = None
    if solicitud:
        solicitud_data = SolicitudBrief(
            id=solicitud.id,
            equipo_id=solicitud.equipo_id,
            descripcion_falla=solicitud.descripcion_falla,
            estado=solicitud.estado,
            fecha_reporte=solicitud.fecha_reporte,
        )
    return {
        "accion": decision.accion,
        "confianza": decision.confianza,
        "razonamiento": decision.razonamiento,
        "solicitud_creada": solicitud_data,
    }


@router.post("/procesar-documento")
def procesar_documento(
    data: ProcesarDocumentoRequest,
    ocr=Depends(get_ocr_adapter),
    llm=Depends(get_llm_adapter),
    embedding=Depends(get_embedding_adapter),
    vector_store=Depends(get_vector_store),
    solicitud_repo=Depends(get_solicitud_repo),
    garantia_repo=Depends(get_garantia_repo),
):
    decision, solicitud = _procesar_pdf(
        data.pdf_path, ocr, llm, embedding, vector_store, solicitud_repo, garantia_repo
    )
    solicitud_data = None
    if solicitud:
        solicitud_data = SolicitudBrief(
            id=solicitud.id,
            equipo_id=solicitud.equipo_id,
            descripcion_falla=solicitud.descripcion_falla,
            estado=solicitud.estado,
            fecha_reporte=solicitud.fecha_reporte,
        )
    return {
        "accion": decision.accion,
        "confianza": decision.confianza,
        "razonamiento": decision.razonamiento,
        "solicitud_creada": solicitud_data,
    }


@router.post("/ingestar-fixtures")
def ingestar_fixtures(
    ocr=Depends(get_ocr_adapter),
    llm=Depends(get_llm_adapter),
    embedding=Depends(get_embedding_adapter),
    vector_store=Depends(get_vector_store),
    solicitud_repo=Depends(get_solicitud_repo),
    garantia_repo=Depends(get_garantia_repo),
):
    """Procesa todos los PDFs de fixtures/ e indexa sus chunks en pgvector."""
    from pathlib import Path
    pdfs = list(Path("fixtures/pdfs").glob("*.pdf"))
    resultados = []
    for pdf in pdfs:
        try:
            _, solicitud = _procesar_pdf(
                str(pdf), ocr, llm, embedding, vector_store, solicitud_repo, garantia_repo
            )
            resultados.append({"pdf": pdf.name, "ok": True, "solicitud_id": solicitud.id if solicitud else None})
        except Exception as e:
            resultados.append({"pdf": pdf.name, "ok": False, "error": str(e)})
    return {"ingestados": len([r for r in resultados if r["ok"]]), "detalle": resultados}


@router.post("/verificar-semanal")
def verificar_estado_semanal(
    llm=Depends(get_llm_adapter),
    solicitud_repo=Depends(get_solicitud_repo),
    trazabilidad_repo=Depends(get_trazabilidad_repo),
    borrador_repo=Depends(get_borrador_repo),
    seguimiento_repo=Depends(get_evento_seguimiento_repo),
):
    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=trazabilidad_repo,
        borrador_repo=borrador_repo,
        seguimiento_repo=seguimiento_repo,
        llm=llm,
        timeout_proveedor_dias=settings.TIMEOUT_PROVEEDOR_DIAS,
        timeout_cliente_dias=settings.TIMEOUT_CLIENTE_DIAS,
    )
    return caso_uso.execute()


@router.get("/buscar-similares")
def buscar_similares(
    q: str = Query(default="", min_length=0),
    embedding=Depends(get_embedding_adapter),
    vector_store=Depends(get_vector_store),
    solicitud_repo=Depends(get_solicitud_repo),
):
    if not q.strip():
        return {"resultados": [], "query": q}

    query_emb = embedding.embed(q)
    chunks = vector_store.search(query_emb, limit=10)

    seen_ids: set[str] = set()
    resultados = []
    for chunk in chunks:
        sid = chunk.get("metadata", {}).get("solicitud_id") if isinstance(chunk.get("metadata"), dict) else None
        if not sid or sid in seen_ids:
            continue
        seen_ids.add(sid)
        solicitud = solicitud_repo.find_by_id(str(sid))
        if solicitud:
            resultados.append({
                "id": solicitud.id,
                "equipo_id": solicitud.equipo_id,
                "descripcion_falla": solicitud.descripcion_falla,
                "estado": solicitud.estado,
                "fecha_reporte": str(solicitud.fecha_reporte),
                "similitud": round(chunk.get("similarity", 0), 3),
            })

    return {"resultados": resultados, "query": q}


@router.get("/inbox-preview")
def inbox_preview(
    email_reader=Depends(get_email_reader),
    solicitud_repo=Depends(get_solicitud_repo),
):
    from src.agente.infrastructure.email.outlook_adapter import IMAPAuthError
    from src.agente.infrastructure.email.fake_email_adapter import FakeEmailReaderAdapter, build_dynamic_inbox
    from src.solicitudes.domain.entities import EstadoSolicitud
    try:
        correos = email_reader.fetch_unread()
        es_mock = False
    except IMAPAuthError:
        solicitudes = solicitud_repo.find_all()
        correos = build_dynamic_inbox(solicitudes)
        es_mock = True
    return {
        "total": len(correos),
        "es_mock": es_mock,
        "correos": [
            {
                "uid": c.uid,
                "asunto": c.asunto,
                "remitente": c.remitente,
                "tiene_adjuntos": len(c.adjuntos) > 0,
            }
            for c in correos
        ],
    }


@router.post("/procesar-correos")
def procesar_correos(
    llm=Depends(get_llm_adapter),
    email_reader=Depends(get_email_reader),
    ocr=Depends(get_ocr_adapter),
    embedding=Depends(get_embedding_adapter),
    vector_store=Depends(get_vector_store),
    solicitud_repo=Depends(get_solicitud_repo),
    garantia_repo=Depends(get_garantia_repo),
    trazabilidad_repo=Depends(get_trazabilidad_repo),
    orquestar=Depends(get_orquestar_acciones),
):
    from src.agente.application.procesar_correo import ProcesarCorreo
    from src.solicitudes.application.crear_solicitud import CrearSolicitud

    from src.agente.infrastructure.email.outlook_adapter import IMAPAuthError
    from src.agente.infrastructure.email.fake_email_adapter import FakeEmailReaderAdapter, build_dynamic_inbox

    try:
        _ = email_reader.fetch_unread()
        reader = email_reader
    except IMAPAuthError:
        solicitudes = solicitud_repo.find_all()
        reader = FakeEmailReaderAdapter(correos=build_dynamic_inbox(solicitudes))

    caso_uso = ProcesarCorreo(
        llm=llm,
        email_reader=reader,
        ocr=ocr,
        embedding=embedding,
        vector_store=vector_store,
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=trazabilidad_repo,
        crear_solicitud=CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo),
        orquestar=orquestar,
    )
    return caso_uso.execute()


class ContextoChat(BaseModel):
    solicitudes_activas: int = 0
    borradores_pendientes: int = 0
    equipos_activos: list[str] = []


class ChatAgenteRequest(BaseModel):
    mensaje: str
    contexto: ContextoChat = ContextoChat()


@router.post("/chat")
def chat_agente(data: ChatAgenteRequest, llm=Depends(get_llm_adapter)):
    resultado = llm.chat(mensaje=data.mensaje, contexto=data.contexto.model_dump())
    return {
        "respuesta": resultado.respuesta,
        "accion": resultado.accion,
        "query_busqueda": resultado.query_busqueda,
    }
