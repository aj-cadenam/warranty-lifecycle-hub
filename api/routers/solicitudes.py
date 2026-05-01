from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import date
from src.solicitudes.domain.entities import EstadoSolicitud
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from src.solicitudes.application.actualizar_estado import ActualizarEstado
from config.dependencies import get_solicitud_repo, get_garantia_repo

router = APIRouter()


class SolicitudCreate(BaseModel):
    equipo_id: str
    reportado_por: str
    descripcion_falla: str


class SolicitudResponse(BaseModel):
    id: str
    equipo_id: str
    reportado_por: str
    descripcion_falla: str
    estado: EstadoSolicitud
    fecha_reporte: date


@router.post("/", response_model=SolicitudResponse, status_code=status.HTTP_201_CREATED)
def crear_solicitud(data: SolicitudCreate, solicitud_repo=Depends(get_solicitud_repo),
                    garantia_repo=Depends(get_garantia_repo)):
    caso_uso = CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo)
    try:
        solicitud = caso_uso.execute(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return SolicitudResponse(id=solicitud.id, equipo_id=solicitud.equipo_id,
                              reportado_por=solicitud.reportado_por,
                              descripcion_falla=solicitud.descripcion_falla,
                              estado=solicitud.estado, fecha_reporte=solicitud.fecha_reporte)


class EstadoUpdate(BaseModel):
    estado: EstadoSolicitud


@router.patch("/{solicitud_id}/estado", response_model=SolicitudResponse)
def actualizar_estado(solicitud_id: str, data: EstadoUpdate, repo=Depends(get_solicitud_repo)):
    caso_uso = ActualizarEstado(solicitud_repo=repo)
    try:
        s = caso_uso.execute(solicitud_id=solicitud_id, nuevo_estado=data.estado)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return SolicitudResponse(id=s.id, equipo_id=s.equipo_id, reportado_por=s.reportado_por,
                              descripcion_falla=s.descripcion_falla, estado=s.estado,
                              fecha_reporte=s.fecha_reporte)


@router.get("/", response_model=list[SolicitudResponse])
def listar_solicitudes(repo=Depends(get_solicitud_repo)):
    return [SolicitudResponse(id=s.id, equipo_id=s.equipo_id, reportado_por=s.reportado_por,
                               descripcion_falla=s.descripcion_falla, estado=s.estado,
                               fecha_reporte=s.fecha_reporte)
            for s in repo.find_all()]
