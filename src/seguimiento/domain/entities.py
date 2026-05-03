from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
from src.shared.domain.base import BaseEntity


class EstadoBorrador(str, Enum):
    PENDIENTE_APROBACION = "pendiente_aprobacion"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    ENVIADO = "enviado"


class DestinatarioTipo(str, Enum):
    PROVEEDOR = "proveedor"
    CLIENTE = "cliente"
    RESPONSABLE = "responsable"
    BODEGA = "bodega"
    DESPACHO = "despacho"
    RECEPCION = "recepcion"


@dataclass
class BorradorCorreo(BaseEntity):
    solicitud_id: str = ""
    destinatario_tipo: DestinatarioTipo = DestinatarioTipo.PROVEEDOR
    destinatario_email: str = ""
    asunto: str = ""
    cuerpo: str = ""
    estado: EstadoBorrador = EstadoBorrador.PENDIENTE_APROBACION
    aprobado_por: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    fecha_aprobacion: Optional[datetime] = None
    dias_sin_respuesta: int = 0

    def aprobar(self, aprobado_por: str) -> None:
        if self.estado == EstadoBorrador.ENVIADO:
            raise ValueError("ya fue enviado")
        if self.estado == EstadoBorrador.RECHAZADO:
            raise ValueError("fue rechazado")
        self.estado = EstadoBorrador.APROBADO
        self.aprobado_por = aprobado_por
        self.fecha_aprobacion = datetime.now()

    def rechazar(self, motivo: str) -> None:
        self.estado = EstadoBorrador.RECHAZADO
        self.motivo_rechazo = motivo

    def marcar_enviado(self) -> None:
        if self.estado != EstadoBorrador.APROBADO:
            raise ValueError("no está aprobado para envío")
        self.estado = EstadoBorrador.ENVIADO


@dataclass
class EventoSeguimiento(BaseEntity):
    solicitud_id: str = ""
    tipo_evento: str = ""
    descripcion: str = ""
    fecha: date = field(default_factory=date.today)
    dias_sin_respuesta: int = 0
