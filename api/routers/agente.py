from fastapi import APIRouter, Depends
from pydantic import BaseModel
from config.dependencies import (
    get_llm_adapter,
    get_embedding_adapter,
    get_solicitud_repo,
    get_garantia_repo,
    get_ocr_adapter,
    get_trazabilidad_repo,
    get_borrador_repo,
    get_evento_seguimiento_repo,
)
from config.settings import settings
from src.agente.application.procesar_documento import ProcesarDocumento
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from src.seguimiento.application.verificar_estado_semanal import VerificarEstadoSemanal

router = APIRouter()


class ProcesarDocumentoRequest(BaseModel):
    pdf_path: str


@router.post("/procesar-documento")
def procesar_documento(
    data: ProcesarDocumentoRequest,
    ocr=Depends(get_ocr_adapter),
    llm=Depends(get_llm_adapter),
    embedding=Depends(get_embedding_adapter),
    solicitud_repo=Depends(get_solicitud_repo),
    garantia_repo=Depends(get_garantia_repo),
):
    crear_solicitud = CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo)
    caso_uso = ProcesarDocumento(ocr=ocr, llm=llm, embedding=embedding, crear_solicitud=crear_solicitud)
    decision = caso_uso.execute(pdf_path=data.pdf_path)
    return {"accion": decision.accion, "confianza": decision.confianza, "razonamiento": decision.razonamiento}


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
    )
    caso_uso.execute()
    return {"ok": True, "mensaje": "Verificación completada"}
