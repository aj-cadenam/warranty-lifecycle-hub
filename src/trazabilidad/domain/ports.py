from abc import ABC, abstractmethod
from typing import Optional
from src.trazabilidad.domain.entities import EventoTrazabilidad


class TrazabilidadRepository(ABC):
    @abstractmethod
    def save(self, evento: EventoTrazabilidad) -> None: ...
    @abstractmethod
    def find_by_equipo(self, equipo_id: str) -> list[EventoTrazabilidad]: ...
    @abstractmethod
    def find_by_solicitud(self, solicitud_id: str) -> list[EventoTrazabilidad]: ...
    @abstractmethod
    def find_ultimo_evento(self, solicitud_id: str) -> Optional[EventoTrazabilidad]: ...
