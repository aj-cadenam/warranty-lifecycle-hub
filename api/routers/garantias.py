from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import date
from src.equipos.domain.entities import EstadoGarantia

router = APIRouter()


class GarantiaCreate(BaseModel):
    equipo_id: str
    proveedor_nombre: str
    proveedor_email: str
    fecha_inicio: date
    fecha_fin: date
    tipo_cobertura: str


class GarantiaResponse(BaseModel):
    id: str
    equipo_id: str
    fecha_inicio: date
    fecha_fin: date
    tipo_cobertura: str
    estado: EstadoGarantia


@router.post("/", response_model=GarantiaResponse, status_code=status.HTTP_201_CREATED)
def crear_garantia(data: GarantiaCreate):
    from src.equipos.infrastructure.django_models import GarantiaModel, ProveedorModel

    if GarantiaModel.objects.filter(
        equipo_serial=data.equipo_id,
        fecha_fin__gte=date.today(),
    ).exists():
        raise HTTPException(status_code=400, detail="ya existe garantía vigente para este equipo")

    proveedor, _ = ProveedorModel.objects.get_or_create(
        contacto_email=data.proveedor_email,
        defaults={"nombre": data.proveedor_nombre, "tiempo_respuesta_dias": 5},
    )

    estado = EstadoGarantia.VIGENTE if data.fecha_fin >= date.today() else EstadoGarantia.VENCIDA
    g = GarantiaModel.objects.create(
        equipo_serial=data.equipo_id,
        proveedor=proveedor,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        tipo_cobertura=data.tipo_cobertura,
        estado=estado.value,
    )
    return GarantiaResponse(
        id=str(g.id),
        equipo_id=g.equipo_serial,
        fecha_inicio=g.fecha_inicio,
        fecha_fin=g.fecha_fin,
        tipo_cobertura=g.tipo_cobertura,
        estado=estado,
    )
