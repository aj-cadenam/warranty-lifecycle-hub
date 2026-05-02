from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import date, datetime
from src.equipos.domain.entities import TipoEquipo, EstadoEquipo, EstadoGarantia
from src.equipos.application.registrar_equipo import RegistrarEquipo
from config.dependencies import get_equipo_repo, get_garantia_repo, get_trazabilidad_repo

router = APIRouter()


class EquipoCreate(BaseModel):
    serial: str
    nombre: str
    marca: str
    modelo: str
    tipo: TipoEquipo
    ubicacion_fisica: str


class EquipoResponse(BaseModel):
    id: str
    serial: str
    nombre: str
    marca: str
    modelo: str
    tipo: TipoEquipo
    ubicacion_fisica: str
    estado: EstadoEquipo


class GarantiaResponse(BaseModel):
    id: str
    equipo_id: str
    fecha_inicio: date
    fecha_fin: date
    tipo_cobertura: str
    estado: EstadoGarantia


def _equipo_response(e) -> EquipoResponse:
    return EquipoResponse(id=e.serial, serial=e.serial, nombre=e.nombre, marca=e.marca,
                          modelo=e.modelo, tipo=e.tipo, ubicacion_fisica=e.ubicacion_fisica,
                          estado=e.estado)


@router.post("/", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
def registrar_equipo(data: EquipoCreate, repo=Depends(get_equipo_repo)):
    caso_uso = RegistrarEquipo(equipo_repo=repo)
    try:
        equipo = caso_uso.execute(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _equipo_response(equipo)


@router.get("/", response_model=list[EquipoResponse])
def listar_equipos(repo=Depends(get_equipo_repo)):
    return [_equipo_response(e) for e in repo.find_all()]


@router.get("/{serial}/garantia", response_model=GarantiaResponse)
def obtener_garantia_vigente(serial: str, garantia_repo=Depends(get_garantia_repo)):
    garantia = garantia_repo.find_vigente_by_equipo(serial)
    if not garantia:
        raise HTTPException(status_code=404, detail="sin garantía vigente")
    return GarantiaResponse(id=garantia.id, equipo_id=garantia.equipo_id,
                             fecha_inicio=garantia.fecha_inicio, fecha_fin=garantia.fecha_fin,
                             tipo_cobertura=garantia.tipo_cobertura, estado=garantia.estado)


class TrazabilidadResponse(BaseModel):
    id: str
    equipo_id: str
    solicitud_id: str
    ubicacion_anterior: str
    ubicacion_nueva: str
    metodo_registro: str
    timestamp: datetime


@router.get("/{serial}/trazabilidad", response_model=list[TrazabilidadResponse])
def obtener_trazabilidad(serial: str, trazabilidad_repo=Depends(get_trazabilidad_repo)):
    eventos = trazabilidad_repo.find_by_equipo(serial)
    return [
        TrazabilidadResponse(
            id=e.id, equipo_id=e.equipo_id, solicitud_id=e.solicitud_id,
            ubicacion_anterior=e.ubicacion_anterior, ubicacion_nueva=e.ubicacion_nueva,
            metodo_registro=e.metodo_registro.value, timestamp=e.timestamp,
        )
        for e in eventos
    ]


@router.get("/{serial}", response_model=EquipoResponse)
def obtener_equipo(serial: str, repo=Depends(get_equipo_repo)):
    equipo = repo.find_by_serial(serial)
    if not equipo:
        raise HTTPException(status_code=404, detail="equipo no encontrado")
    return _equipo_response(equipo)
