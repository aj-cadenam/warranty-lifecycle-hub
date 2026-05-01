from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.equipos.domain.entities import TipoEquipo, EstadoEquipo
from src.equipos.application.registrar_equipo import RegistrarEquipo
from config.dependencies import get_equipo_repo, get_garantia_repo

router = APIRouter()


class EquipoCreate(BaseModel):
    serial: str
    nombre: str
    marca: str
    modelo: str
    tipo: TipoEquipo
    ubicacion_fisica: str


class EquipoResponse(BaseModel):
    serial: str
    nombre: str
    marca: str
    modelo: str
    tipo: TipoEquipo
    ubicacion_fisica: str
    estado: EstadoEquipo


@router.post("/", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
def registrar_equipo(data: EquipoCreate, repo=Depends(get_equipo_repo)):
    caso_uso = RegistrarEquipo(equipo_repo=repo)
    try:
        equipo = caso_uso.execute(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return EquipoResponse(**equipo.__dict__)


@router.get("/", response_model=list[EquipoResponse])
def listar_equipos(repo=Depends(get_equipo_repo)):
    return [EquipoResponse(**e.__dict__) for e in repo.find_all()]


@router.get("/{serial}", response_model=EquipoResponse)
def obtener_equipo(serial: str, repo=Depends(get_equipo_repo)):
    equipo = repo.find_by_serial(serial)
    if not equipo:
        raise HTTPException(status_code=404, detail="equipo no encontrado")
    return EquipoResponse(**equipo.__dict__)
