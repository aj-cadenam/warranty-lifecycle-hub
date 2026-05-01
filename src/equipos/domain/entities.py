from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from src.shared.domain.base import BaseEntity


class TipoEquipo(str, Enum):
    MULTIFUNCIONAL_IMPRESION = "multifuncional_impresion"
    IMPRESORA_PRODUCCION = "impresora_produccion"
    COLABORACION_AUDIOVISUAL = "colaboracion_audiovisual"
    AUTOMATIZACION_SALA = "automatizacion_sala"
    AUDIO_CORPORATIVO = "audio_corporativo"
    SENALIZACION_DIGITAL = "senalizacion_digital"
    VIDEOCONFERENCIA = "videoconferencia"


class EstadoEquipo(str, Enum):
    ACTIVO = "activo"
    EN_GARANTIA = "en_garantia"
    EN_REPARACION = "en_reparacion"
    DADO_DE_BAJA = "dado_de_baja"


class EstadoGarantia(str, Enum):
    VIGENTE = "vigente"
    VENCIDA = "vencida"
    EN_PROCESO = "en_proceso"
    CERRADA = "cerrada"


@dataclass
class Equipo(BaseEntity):
    serial: str = ""
    nombre: str = ""
    marca: str = ""
    modelo: str = ""
    tipo: TipoEquipo = TipoEquipo.MULTIFUNCIONAL_IMPRESION
    ubicacion_fisica: str = ""
    estado: EstadoEquipo = EstadoEquipo.ACTIVO


@dataclass
class Proveedor(BaseEntity):
    nombre: str = ""
    contacto_email: str = ""
    telefono: str = ""
    tiempo_respuesta_dias: int = 5


@dataclass
class Garantia(BaseEntity):
    equipo_id: str = ""
    proveedor_id: str = ""
    fecha_inicio: date = field(default_factory=date.today)
    fecha_fin: date = field(default_factory=date.today)
    tipo_cobertura: str = ""
    numero_contrato: str = ""
    estado: EstadoGarantia = field(init=False)

    def __post_init__(self):
        self.estado = EstadoGarantia.VIGENTE if self.esta_vigente() else EstadoGarantia.VENCIDA

    def esta_vigente(self) -> bool:
        return self.fecha_fin >= date.today()
