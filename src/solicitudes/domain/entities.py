from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from src.shared.domain.base import BaseEntity


class EstadoSolicitud(str, Enum):
    NUEVA = "nueva"
    VALIDADA = "validada"
    DESPACHADA = "despachada"
    EN_REPARACION = "en_reparacion"
    DEVUELTA = "devuelta"
    CERRADA = "cerrada"


_TRANSICIONES: dict[EstadoSolicitud, list[EstadoSolicitud]] = {
    EstadoSolicitud.NUEVA: [EstadoSolicitud.VALIDADA],
    EstadoSolicitud.VALIDADA: [EstadoSolicitud.DESPACHADA],
    EstadoSolicitud.DESPACHADA: [EstadoSolicitud.EN_REPARACION],
    EstadoSolicitud.EN_REPARACION: [EstadoSolicitud.DEVUELTA],
    EstadoSolicitud.DEVUELTA: [EstadoSolicitud.CERRADA],
    EstadoSolicitud.CERRADA: [],
}


@dataclass
class SolicitudGarantia(BaseEntity):
    equipo_id: str = ""
    garantia_id: str = ""
    reportado_por: str = ""
    descripcion_falla: str = ""
    fecha_reporte: date = field(default_factory=date.today)
    estado: EstadoSolicitud = EstadoSolicitud.NUEVA

    def _transicionar(self, nuevo: EstadoSolicitud) -> None:
        if nuevo not in _TRANSICIONES[self.estado]:
            raise ValueError(f"transición inválida: {self.estado} → {nuevo}")
        self.estado = nuevo

    def validar(self) -> None: self._transicionar(EstadoSolicitud.VALIDADA)
    def despachar(self) -> None: self._transicionar(EstadoSolicitud.DESPACHADA)
    def iniciar_reparacion(self) -> None: self._transicionar(EstadoSolicitud.EN_REPARACION)
    def devolver(self) -> None: self._transicionar(EstadoSolicitud.DEVUELTA)
    def cerrar(self) -> None: self._transicionar(EstadoSolicitud.CERRADA)


@dataclass
class ActaEntrega(BaseEntity):
    solicitud_id: str = ""
    tecnico_responsable: str = ""
    fecha_entrega: date = field(default_factory=date.today)
    observaciones: str = ""
    imagen_acta_path: str = ""
