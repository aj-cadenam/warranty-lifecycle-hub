from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
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
    destinatario_email: str
    asunto: str
    cuerpo: str
    estado: EstadoBorrador
    aprobado_por: Optional[str] = None


@router.get("/", response_model=list[BorradorResponse])
def listar_pendientes(repo=Depends(get_borrador_repo)):
    return [BorradorResponse(id=b.id, solicitud_id=b.solicitud_id,
                              destinatario_email=b.destinatario_email, asunto=b.asunto,
                              cuerpo=b.cuerpo, estado=b.estado, aprobado_por=b.aprobado_por)
            for b in repo.find_pendientes()]


@router.get("/{borrador_id}", response_model=BorradorResponse)
def obtener_borrador(borrador_id: str, repo=Depends(get_borrador_repo)):
    b = repo.find_by_id(borrador_id)
    if not b:
        raise HTTPException(status_code=404, detail="borrador no encontrado")
    return BorradorResponse(id=b.id, solicitud_id=b.solicitud_id,
                             destinatario_email=b.destinatario_email, asunto=b.asunto,
                             cuerpo=b.cuerpo, estado=b.estado, aprobado_por=b.aprobado_por)


@router.patch("/{borrador_id}")
def editar_borrador(borrador_id: str, data: EditarBorradorRequest, repo=Depends(get_borrador_repo)):
    b = repo.find_by_id(borrador_id)
    if not b:
        raise HTTPException(status_code=404, detail="borrador no encontrado")
    b.cuerpo = data.cuerpo
    repo.save(b)
    return {"ok": True}


@router.post("/{borrador_id}/aprobar")
def aprobar_borrador(borrador_id: str, data: AprobarRequest,
                     repo=Depends(get_borrador_repo), email=Depends(get_email_adapter)):
    try:
        AprobarBorrador(borrador_repo=repo, email_adapter=email).execute(
            borrador_id=borrador_id, aprobado_por=data.aprobado_por)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "mensaje": "Correo enviado"}


@router.post("/{borrador_id}/rechazar")
def rechazar_borrador(borrador_id: str, data: RechazarRequest, repo=Depends(get_borrador_repo)):
    try:
        RechazarBorrador(borrador_repo=repo).execute(borrador_id=borrador_id, motivo=data.motivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "mensaje": "Borrador rechazado"}
