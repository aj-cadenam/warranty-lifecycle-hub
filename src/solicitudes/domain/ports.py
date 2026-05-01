from abc import ABC, abstractmethod
from typing import Optional
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud


class SolicitudRepository(ABC):
    @abstractmethod
    def save(self, solicitud: SolicitudGarantia) -> None: ...
    @abstractmethod
    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudGarantia]: ...
    @abstractmethod
    def find_by_estado(self, estado: EstadoSolicitud) -> list[SolicitudGarantia]: ...
    @abstractmethod
    def find_all(self) -> list[SolicitudGarantia]: ...
