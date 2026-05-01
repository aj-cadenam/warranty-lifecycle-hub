from typing import Optional
from src.equipos.domain.entities import Equipo, Garantia, Proveedor
from src.equipos.domain.ports import EquipoRepository, GarantiaRepository, ProveedorRepository
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.solicitudes.domain.ports import SolicitudRepository
from src.trazabilidad.domain.entities import EventoTrazabilidad
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.seguimiento.domain.entities import BorradorCorreo, EventoSeguimiento, EstadoBorrador
from src.seguimiento.domain.ports import BorradorCorreoRepository, EventoSeguimientoRepository


class FakeEquipoRepository(EquipoRepository):
    def __init__(self): self._store: dict[str, Equipo] = {}
    def save(self, equipo: Equipo) -> None: self._store[equipo.serial] = equipo
    def find_by_serial(self, serial: str) -> Optional[Equipo]: return self._store.get(serial)
    def find_all(self) -> list[Equipo]: return list(self._store.values())


class FakeGarantiaRepository(GarantiaRepository):
    def __init__(self): self._store: dict[str, Garantia] = {}
    def save(self, garantia: Garantia) -> None: self._store[garantia.id] = garantia
    def find_vigente_by_equipo(self, equipo_id: str) -> Optional[Garantia]:
        return next((g for g in self._store.values() if g.equipo_id == equipo_id and g.esta_vigente()), None)


class FakeSolicitudRepository(SolicitudRepository):
    def __init__(self): self._store: dict[str, SolicitudGarantia] = {}
    def save(self, s: SolicitudGarantia) -> None: self._store[s.id] = s
    def find_by_id(self, sid: str) -> Optional[SolicitudGarantia]: return self._store.get(sid)
    def find_by_estado(self, estado: EstadoSolicitud) -> list[SolicitudGarantia]:
        return [s for s in self._store.values() if s.estado == estado]
    def find_all(self) -> list[SolicitudGarantia]: return list(self._store.values())


class FakeTrazabilidadRepository(TrazabilidadRepository):
    def __init__(self): self._store: list[EventoTrazabilidad] = []
    def save(self, e: EventoTrazabilidad) -> None: self._store.append(e)
    def find_by_equipo(self, equipo_id: str) -> list[EventoTrazabilidad]:
        return [e for e in self._store if e.equipo_id == equipo_id]
    def find_by_solicitud(self, solicitud_id: str) -> list[EventoTrazabilidad]:
        return [e for e in self._store if e.solicitud_id == solicitud_id]
    def find_ultimo_evento(self, solicitud_id: str) -> Optional[EventoTrazabilidad]:
        eventos = self.find_by_solicitud(solicitud_id)
        return max(eventos, key=lambda e: e.timestamp, default=None)


class FakeBorradorCorreoRepository(BorradorCorreoRepository):
    def __init__(self): self._store: dict[str, BorradorCorreo] = {}
    def save(self, b: BorradorCorreo) -> None: self._store[b.id] = b
    def find_by_id(self, bid: str) -> Optional[BorradorCorreo]: return self._store.get(bid)
    def find_pendientes(self) -> list[BorradorCorreo]:
        return [b for b in self._store.values() if b.estado == EstadoBorrador.PENDIENTE_APROBACION]
    def find_by_solicitud_y_estado(self, solicitud_id: str, estado: EstadoBorrador) -> Optional[BorradorCorreo]:
        return next((b for b in self._store.values() if b.solicitud_id == solicitud_id and b.estado == estado), None)


class FakeEventoSeguimientoRepository(EventoSeguimientoRepository):
    def __init__(self): self._store: list[EventoSeguimiento] = []
    def save(self, e: EventoSeguimiento) -> None: self._store.append(e)
    def find_by_solicitud(self, solicitud_id: str) -> list[EventoSeguimiento]:
        return [e for e in self._store if e.solicitud_id == solicitud_id]


class FakeEmailAdapter:
    def __init__(self): self.sent: list[dict] = []
    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})
