from src.agente.application.orquestar_acciones import OrquestarAcciones
from src.agente.domain.entities import TipoCorreo, DecisionCorreo
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.seguimiento.domain.entities import DestinatarioTipo, EstadoBorrador
from src.seguimiento.domain.ports import BorradorCorreoRepository
from src.solicitudes.domain.entities import SolicitudGarantia
from typing import Optional


class InMemoryBorradorRepo(BorradorCorreoRepository):
    def __init__(self):
        self._store: list = []
    def save(self, b):
        self._store.append(b)
    def find_by_id(self, id_): return None
    def find_pendientes(self): return list(self._store)
    def find_by_solicitud_y_estado(self, sid, estado): return None


def _solicitud(equipo_id: str = "KYO-001") -> SolicitudGarantia:
    return SolicitudGarantia(
        id="sol-1",
        equipo_id=equipo_id,
        reportado_por="Agente Test",
        descripcion_falla="Error fusor",
    )


def _decision(tipo: TipoCorreo, serial: str = "KYO-001") -> DecisionCorreo:
    return DecisionCorreo(tipo=tipo, confianza=0.95, equipo_serial=serial)


def test_acta_entrega_notifica_responsable():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
    )
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.ACTA_ENTREGA))
    assert len(borradores) == 1
    assert borradores[0].destinatario_tipo == DestinatarioTipo.RESPONSABLE
    assert borradores[0].destinatario_email == "resp@datecsa.com"
    assert borradores[0].estado == EstadoBorrador.PENDIENTE_APROBACION


def test_actualizacion_proveedor_notifica_responsable():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
    )
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.ACTUALIZACION_PROVEEDOR))
    assert len(borradores) == 1
    assert borradores[0].destinatario_tipo == DestinatarioTipo.RESPONSABLE


def test_confirmacion_devolucion_notifica_bodega_despacho_recepcion_responsable():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
        bodega_email="bodega@datecsa.com",
        despacho_email="despacho@datecsa.com",
        recepcion_email="recepcion@datecsa.com",
    )
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.CONFIRMACION_DEVOLUCION))
    tipos = {b.destinatario_tipo for b in borradores}
    assert len(borradores) == 4
    assert DestinatarioTipo.BODEGA in tipos
    assert DestinatarioTipo.DESPACHO in tipos
    assert DestinatarioTipo.RECEPCION in tipos
    assert DestinatarioTipo.RESPONSABLE in tipos


def test_sin_emails_configurados_no_crea_borradores():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(llm=FakeLLMAdapter(), borrador_repo=repo)
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.CONFIRMACION_DEVOLUCION))
    assert len(borradores) == 0


def test_tipo_otro_no_crea_borradores():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
    )
    borradores = uc.execute(_solicitud(), _decision(TipoCorreo.OTRO))
    assert len(borradores) == 0


def test_borradores_son_persistidos():
    repo = InMemoryBorradorRepo()
    uc = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=repo,
        responsable_email="resp@datecsa.com",
    )
    uc.execute(_solicitud(), _decision(TipoCorreo.ACTA_ENTREGA))
    assert len(repo._store) == 1
    assert repo._store[0].solicitud_id == "sol-1"
