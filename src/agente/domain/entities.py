from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Accion(str, Enum):
    CREAR_SOLICITUD = "CREAR_SOLICITUD"
    ACTUALIZAR_ESTADO = "ACTUALIZAR_ESTADO"
    NOTIFICAR = "NOTIFICAR"
    ESCALAR = "ESCALAR"
    IGNORAR = "IGNORAR"


@dataclass
class DecisionAgente:
    accion: Accion
    confianza: float
    parametros: dict[str, Any] = field(default_factory=dict)
    razonamiento: str = ""
