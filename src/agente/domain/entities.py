from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Accion(str, Enum):
    CREAR_SOLICITUD = "crear_solicitud"
    ACTUALIZAR_ESTADO = "actualizar_estado"
    NOTIFICAR = "notificar"
    ESCALAR = "escalar"
    IGNORAR = "ignorar"


@dataclass
class DecisionAgente:
    accion: Accion
    confianza: float
    parametros: dict[str, Any] = field(default_factory=dict)
    razonamiento: str = ""
