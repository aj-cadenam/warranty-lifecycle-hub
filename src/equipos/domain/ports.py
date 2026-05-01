from abc import ABC, abstractmethod
from typing import Optional
from src.equipos.domain.entities import Equipo, Garantia, Proveedor


class EquipoRepository(ABC):
    @abstractmethod
    def save(self, equipo: Equipo) -> None: ...
    @abstractmethod
    def find_by_serial(self, serial: str) -> Optional[Equipo]: ...
    @abstractmethod
    def find_all(self) -> list[Equipo]: ...


class GarantiaRepository(ABC):
    @abstractmethod
    def save(self, garantia: Garantia) -> None: ...
    @abstractmethod
    def find_vigente_by_equipo(self, equipo_id: str) -> Optional[Garantia]: ...


class ProveedorRepository(ABC):
    @abstractmethod
    def save(self, proveedor: Proveedor) -> None: ...
    @abstractmethod
    def find_by_id(self, proveedor_id: str) -> Optional[Proveedor]: ...
