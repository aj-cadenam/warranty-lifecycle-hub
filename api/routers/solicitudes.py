from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import date
from typing import Optional
from src.solicitudes.domain.entities import EstadoSolicitud
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from src.solicitudes.application.actualizar_estado import ActualizarEstado
from config.dependencies import get_solicitud_repo, get_garantia_repo, get_equipo_repo, get_trazabilidad_repo

router = APIRouter()


class SolicitudCreate(BaseModel):
    equipo_id: str
    reportado_por: str
    descripcion_falla: str


class EquipoEnSolicitud(BaseModel):
    serial: str
    nombre: str
    marca: str
    modelo: str
    tipo: str
    ubicacion_fisica: str
    estado: str


class EventoTrazabilidadResponse(BaseModel):
    id: str
    equipo_id: str
    solicitud_id: str
    ubicacion_anterior: str
    ubicacion_nueva: str
    metodo_registro: str
    timestamp: str
    notas: str = ""


class SolicitudResponse(BaseModel):
    id: str
    equipo_id: str
    reportado_por: str
    descripcion_falla: str
    estado: EstadoSolicitud
    fecha_reporte: date
    equipo: Optional[EquipoEnSolicitud] = None
    eventos: list[EventoTrazabilidadResponse] = []


def _equipo_data(equipo_repo, equipo_id: str) -> Optional[EquipoEnSolicitud]:
    eq = equipo_repo.find_by_serial(equipo_id)
    if not eq:
        return None
    return EquipoEnSolicitud(
        serial=eq.serial, nombre=eq.nombre, marca=eq.marca, modelo=eq.modelo,
        tipo=eq.tipo.value, ubicacion_fisica=eq.ubicacion_fisica, estado=eq.estado.value,
    )


def _eventos_data(trazabilidad_repo, solicitud_id: str, equipo_id: str) -> list[EventoTrazabilidadResponse]:
    return [
        EventoTrazabilidadResponse(
            id=ev.id, equipo_id=ev.equipo_id, solicitud_id=ev.solicitud_id,
            ubicacion_anterior=ev.ubicacion_anterior, ubicacion_nueva=ev.ubicacion_nueva,
            metodo_registro=ev.metodo_registro.value,
            timestamp=ev.timestamp.isoformat() if hasattr(ev.timestamp, "isoformat") else str(ev.timestamp),
            notas=ev.notas,
        )
        for ev in trazabilidad_repo.find_by_solicitud(solicitud_id)
        if ev.equipo_id == equipo_id
    ]


def _to_response(s, equipo_repo=None, trazabilidad_repo=None) -> SolicitudResponse:
    return SolicitudResponse(
        id=s.id, equipo_id=s.equipo_id, reportado_por=s.reportado_por,
        descripcion_falla=s.descripcion_falla, estado=s.estado, fecha_reporte=s.fecha_reporte,
        equipo=_equipo_data(equipo_repo, s.equipo_id) if equipo_repo else None,
        eventos=_eventos_data(trazabilidad_repo, s.id, s.equipo_id) if trazabilidad_repo else [],
    )


class EstadoUpdate(BaseModel):
    estado: EstadoSolicitud


@router.post("/", response_model=SolicitudResponse, status_code=status.HTTP_201_CREATED)
def crear_solicitud(
    data: SolicitudCreate,
    solicitud_repo=Depends(get_solicitud_repo),
    garantia_repo=Depends(get_garantia_repo),
    equipo_repo=Depends(get_equipo_repo),
):
    caso_uso = CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo)
    try:
        solicitud = caso_uso.execute(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _to_response(solicitud, equipo_repo)


@router.patch("/{solicitud_id}/estado", response_model=SolicitudResponse)
def actualizar_estado(
    solicitud_id: str,
    data: EstadoUpdate,
    repo=Depends(get_solicitud_repo),
    equipo_repo=Depends(get_equipo_repo),
):
    caso_uso = ActualizarEstado(solicitud_repo=repo)
    try:
        s = caso_uso.execute(solicitud_id=solicitud_id, nuevo_estado=data.estado)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _to_response(s, equipo_repo)


@router.get("/", response_model=list[SolicitudResponse])
def listar_solicitudes(
    repo=Depends(get_solicitud_repo),
    equipo_repo=Depends(get_equipo_repo),
):
    return [_to_response(s, equipo_repo) for s in repo.find_all()]


@router.get("/{solicitud_id}", response_model=SolicitudResponse)
def obtener_solicitud(
    solicitud_id: str,
    repo=Depends(get_solicitud_repo),
    equipo_repo=Depends(get_equipo_repo),
    trazabilidad_repo=Depends(get_trazabilidad_repo),
):
    s = repo.find_by_id(solicitud_id)
    if not s:
        raise HTTPException(status_code=404, detail="solicitud no encontrada")
    return _to_response(s, equipo_repo, trazabilidad_repo)
