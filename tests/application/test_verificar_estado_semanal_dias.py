from datetime import datetime, timedelta
from src.seguimiento.application.verificar_estado_semanal import VerificarEstadoSemanal
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.trazabilidad.domain.entities import EventoTrazabilidad
from src.solicitudes.domain.ports import SolicitudRepository
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.seguimiento.domain.ports import BorradorCorreoRepository, EventoSeguimientoRepository
from src.seguimiento.domain.entities import EstadoBorrador
from typing import Optional


class FakeSolicitudRepoVS:
    def find_by_estado(self, estado):
        if estado == EstadoSolicitud.DESPACHADA:
            return [SolicitudGarantia(
                id="sol-1", equipo_id="KYO-001",
                reportado_por="Test", descripcion_falla="Falla",
                estado=EstadoSolicitud.DESPACHADA,
            )]
        return []
    def find_all(self): return []
    def save(self, s): pass
    def find_by_id(self, id_): return None


class FakeTrazabilidadRepoVS:
    def __init__(self, dias_atras: int):
        self._dias = dias_atras
    def find_ultimo_evento(self, sid):
        return EventoTrazabilidad(
            solicitud_id=sid,
            equipo_id="KYO-001",
            timestamp=datetime.now() - timedelta(days=self._dias),
        )
    def find_by_equipo(self, eid): return []
    def find_by_solicitud(self, sid): return []
    def save(self, e): pass


class InMemBorradorRepoVS:
    def __init__(self):
        self._store = []
    def save(self, b): self._store.append(b)
    def find_by_id(self, id_): return None
    def find_pendientes(self): return list(self._store)
    def find_by_solicitud_y_estado(self, sid, estado): return None


class InMemSeguimientoRepo:
    def save(self, e): pass
    def find_by_solicitud(self, sid): return []


def test_borrador_tiene_dias_sin_respuesta():
    borrador_repo = InMemBorradorRepoVS()
    uc = VerificarEstadoSemanal(
        solicitud_repo=FakeSolicitudRepoVS(),
        trazabilidad_repo=FakeTrazabilidadRepoVS(dias_atras=10),
        borrador_repo=borrador_repo,
        seguimiento_repo=InMemSeguimientoRepo(),
        llm=FakeLLMAdapter(),
        timeout_proveedor_dias=7,
        proveedor_email="prov@test.com",
    )
    result = uc.execute()
    assert result["borradores_generados"] == 1
    assert borrador_repo._store[0].dias_sin_respuesta == 10
