from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.seguimiento.domain.entities import EstadoBorrador
from src.seguimiento.application.aprobar_borrador import AprobarBorrador
from src.seguimiento.application.rechazar_borrador import RechazarBorrador
from config.dependencies import get_borrador_repo, get_email_adapter

router = APIRouter()


class AprobarRequest(BaseModel):
    aprobado_por: str


class RechazarRequest(BaseModel):
    motivo: str


class EditarBorradorRequest(BaseModel):
    cuerpo: str


class BorradorResponse(BaseModel):
    id: str
    solicitud_id: str
    destinatario_tipo: str
    destinatario_email: str
    asunto: str
    cuerpo: str
    estado: EstadoBorrador
    aprobado_por: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    fecha_aprobacion: Optional[datetime] = None
    dias_sin_respuesta: int = 0


def _to_response(b) -> BorradorResponse:
    return BorradorResponse(
        id=b.id,
        solicitud_id=b.solicitud_id,
        destinatario_tipo=b.destinatario_tipo.value,
        destinatario_email=b.destinatario_email,
        asunto=b.asunto,
        cuerpo=b.cuerpo,
        estado=b.estado,
        aprobado_por=b.aprobado_por,
        motivo_rechazo=b.motivo_rechazo,
        fecha_aprobacion=b.fecha_aprobacion,
        dias_sin_respuesta=b.dias_sin_respuesta,
    )


@router.get("/", response_model=list[BorradorResponse])
def listar_pendientes(repo=Depends(get_borrador_repo)):
    return [_to_response(b) for b in repo.find_pendientes()]


@router.get("/{borrador_id}", response_model=BorradorResponse)
def obtener_borrador(borrador_id: str, repo=Depends(get_borrador_repo)):
    b = repo.find_by_id(borrador_id)
    if not b:
        raise HTTPException(status_code=404, detail="borrador no encontrado")
    return _to_response(b)


@router.patch("/{borrador_id}", response_model=BorradorResponse)
def editar_borrador(borrador_id: str, data: EditarBorradorRequest, repo=Depends(get_borrador_repo)):
    b = repo.find_by_id(borrador_id)
    if not b:
        raise HTTPException(status_code=404, detail="borrador no encontrado")
    b.cuerpo = data.cuerpo
    repo.save(b)
    b = repo.find_by_id(borrador_id)
    if not b:
        raise HTTPException(status_code=404, detail="borrador no encontrado")
    return _to_response(b)


@router.post("/{borrador_id}/aprobar", response_model=BorradorResponse)
def aprobar_borrador(borrador_id: str, data: AprobarRequest,
                     repo=Depends(get_borrador_repo), email=Depends(get_email_adapter)):
    try:
        AprobarBorrador(borrador_repo=repo, email_adapter=email).execute(
            borrador_id=borrador_id, aprobado_por=data.aprobado_por)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    b = repo.find_by_id(borrador_id)
    if not b:
        raise HTTPException(status_code=404, detail="borrador no encontrado")
    return _to_response(b)


@router.post("/{borrador_id}/rechazar", response_model=BorradorResponse)
def rechazar_borrador(borrador_id: str, data: RechazarRequest, repo=Depends(get_borrador_repo)):
    try:
        RechazarBorrador(borrador_repo=repo).execute(borrador_id=borrador_id, motivo=data.motivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    b = repo.find_by_id(borrador_id)
    if not b:
        raise HTTPException(status_code=404, detail="borrador no encontrado")
    return _to_response(b)
