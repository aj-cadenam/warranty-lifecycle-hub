from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.trazabilidad.domain.entities import EventoTrazabilidad, MetodoRegistro

router = APIRouter()


class TrazabilidadCreate(BaseModel):
    equipo_id: str
    solicitud_id: str
    ubicacion_anterior: str
    ubicacion_nueva: str
    metodo_registro: str = "manual"
    timestamp: Optional[str] = None


class TrazabilidadResponse(BaseModel):
    id: str
    equipo_id: str
    solicitud_id: str
    ubicacion_anterior: str
    ubicacion_nueva: str
    metodo_registro: str
    timestamp: datetime


@router.post("/", response_model=TrazabilidadResponse, status_code=status.HTTP_201_CREATED)
def registrar_evento(data: TrazabilidadCreate):
    from src.trazabilidad.infrastructure.repositories import DjangoTrazabilidadRepository

    ts = datetime.fromisoformat(data.timestamp) if data.timestamp else datetime.now()
    try:
        metodo = MetodoRegistro(data.metodo_registro)
    except ValueError:
        metodo = MetodoRegistro.MANUAL

    evento = EventoTrazabilidad(
        equipo_id=data.equipo_id,
        solicitud_id=data.solicitud_id,
        ubicacion_anterior=data.ubicacion_anterior,
        ubicacion_nueva=data.ubicacion_nueva,
        metodo_registro=metodo,
        timestamp=ts,
    )
    repo = DjangoTrazabilidadRepository()
    repo.save(evento)
    return TrazabilidadResponse(
        id=evento.id,
        equipo_id=evento.equipo_id,
        solicitud_id=evento.solicitud_id,
        ubicacion_anterior=evento.ubicacion_anterior,
        ubicacion_nueva=evento.ubicacion_nueva,
        metodo_registro=evento.metodo_registro.value,
        timestamp=evento.timestamp,
    )
