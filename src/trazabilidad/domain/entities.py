from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from src.shared.domain.base import BaseEntity


class MetodoRegistro(str, Enum):
    MANUAL = "manual"
    AGENTE_OCR = "agente_ocr"
    AGENTE_EMAIL = "agente_email"


@dataclass
class EventoTrazabilidad(BaseEntity):
    equipo_id: str = ""
    solicitud_id: str = ""
    ubicacion_anterior: str = ""
    ubicacion_nueva: str = ""
    responsable: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metodo_registro: MetodoRegistro = MetodoRegistro.MANUAL
