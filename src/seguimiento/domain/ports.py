from abc import ABC, abstractmethod
from typing import Optional
from src.seguimiento.domain.entities import BorradorCorreo, EventoSeguimiento, EstadoBorrador


class BorradorCorreoRepository(ABC):
    @abstractmethod
    def save(self, borrador: BorradorCorreo) -> None: ...
    @abstractmethod
    def find_by_id(self, borrador_id: str) -> Optional[BorradorCorreo]: ...
    @abstractmethod
    def find_pendientes(self) -> list[BorradorCorreo]: ...
    @abstractmethod
    def find_by_solicitud_y_estado(self, solicitud_id: str, estado: EstadoBorrador) -> Optional[BorradorCorreo]: ...


class EventoSeguimientoRepository(ABC):
    @abstractmethod
    def save(self, evento: EventoSeguimiento) -> None: ...
    @abstractmethod
    def find_by_solicitud(self, solicitud_id: str) -> list[EventoSeguimiento]: ...
