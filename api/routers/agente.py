from fastapi import APIRouter, Depends
from pydantic import BaseModel
from config.dependencies import (
    get_llm_adapter,
    get_embedding_adapter,
    get_solicitud_repo,
    get_garantia_repo,
    get_ocr_adapter,
)
from src.agente.application.procesar_documento import ProcesarDocumento
from src.solicitudes.application.crear_solicitud import CrearSolicitud

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
