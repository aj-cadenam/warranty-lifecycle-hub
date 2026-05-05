from datetime import datetime
from src.agente.application.procesar_correo import ProcesarCorreo
from src.agente.application.orquestar_acciones import OrquestarAcciones
from src.agente.domain.entities import CorreoEntrante
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.agente.infrastructure.email.fake_email_adapter import FakeEmailReaderAdapter, FakeEmailAdapter
from src.agente.infrastructure.ocr.fake_ocr_adapter import FakeOCRAdapter
from src.agente.infrastructure.embeddings.fake_embedding_adapter import FakeEmbeddingAdapter
from src.seguimiento.domain.entities import DestinatarioTipo
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.solicitudes.domain.ports import SolicitudRepository
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.seguimiento.domain.ports import BorradorCorreoRepository
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from src.equipos.domain.entities import Equipo, Garantia, TipoEquipo
from datetime import date
from typing import Optional


# ── Fakes ──

class FakeVectorStore:
    def store(self, chunks, embeddings): pass
    def search(self, emb, limit=5): return []


class FakeSolicitudRepo(SolicitudRepository):
    def __init__(self):
        self._store: dict[str, SolicitudGarantia] = {}
        self._id_counter = 1

    def save(self, s: SolicitudGarantia) -> None:
        if not s.id:
            s.id = str(self._id_counter)
            self._id_counter += 1
        self._store[s.id] = s

    def find_by_id(self, id_: str) -> Optional[SolicitudGarantia]:
        return self._store.get(id_)

    def find_all(self) -> list[SolicitudGarantia]:
        return list(self._store.values())

    def find_by_estado(self, estado: EstadoSolicitud) -> list[SolicitudGarantia]:
        return [s for s in self._store.values() if s.estado == estado]


class FakeGarantiaRepo:
    def find_vigente_by_equipo(self, equipo_id: str) -> Optional[Garantia]:
        return Garantia(
            equipo_id=equipo_id,
            proveedor_id="prov-1",
            fecha_inicio=date(2020, 1, 1),
            fecha_fin=date(2027, 1, 1),
            tipo_cobertura="total",
        )
    def save(self, g): pass


class FakeTrazabilidadRepo(TrazabilidadRepository):
    def __init__(self):
        self._store = []
    def save(self, e): self._store.append(e)
    def find_by_equipo(self, eid): return []
    def find_by_solicitud(self, sid): return []
    def find_ultimo_evento(self, sid): return None


class InMemoryBorradorRepo(BorradorCorreoRepository):
    def __init__(self):
        self._store = []
    def save(self, b): self._store.append(b)
    def find_by_id(self, id_): return None
    def find_pendientes(self): return list(self._store)
    def find_by_solicitud_y_estado(self, sid, estado): return None


# ── Tests ──

def _inbox_with(correos: list[CorreoEntrante]) -> FakeEmailReaderAdapter:
    return FakeEmailReaderAdapter(correos=correos)


def test_acta_entrega_genera_borrador_responsable():
    inbox = _inbox_with([CorreoEntrante(
        uid="t-001",
        asunto="Acta de entrega - KYO-TASKalfa-2021-001",
        cuerpo="Falla error fusor C3100. Serial: KYO-TASKalfa-2021-001.",
        remitente="tecnico@datecsafake.com",
        fecha=datetime.now(),
    )])
    solicitud_repo = FakeSolicitudRepo()
    borrador_repo = InMemoryBorradorRepo()
    orquestar = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=borrador_repo,
        responsable_email="resp@datecsafake.com",
    )
    caso_uso = ProcesarCorreo(
        llm=FakeLLMAdapter(),
        email_reader=inbox,
        ocr=FakeOCRAdapter(),
        embedding=FakeEmbeddingAdapter(dim=768),
        vector_store=FakeVectorStore(),
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=FakeTrazabilidadRepo(),
        crear_solicitud=CrearSolicitud(
            solicitud_repo=solicitud_repo,
            garantia_repo=FakeGarantiaRepo(),
        ),
        orquestar=orquestar,
    )
    result = caso_uso.execute()
    assert result["procesados"] == 1
    assert result["detalle"][0]["borradores_generados"] == 1
    assert result["detalle"][0]["destinatarios"] == ["responsable"]


def test_confirmacion_devolucion_genera_4_borradores():
    inbox = _inbox_with([CorreoEntrante(
        uid="t-002",
        asunto="Equipo reparado listo para retiro - KYO-TASKalfa-2021-001",
        cuerpo="El equipo serial KYO-TASKalfa-2021-001 está listo para retiro.",
        remitente="soporte@kyocera.com",
        fecha=datetime.now(),
    )])
    solicitud_repo = FakeSolicitudRepo()
    # Pre-load a solicitud in despachada state
    sol = SolicitudGarantia(
        id="sol-existing",
        equipo_id="KYO-TASKalfa-2021-001",
        reportado_por="Test",
        descripcion_falla="Error fusor",
        estado=EstadoSolicitud.DESPACHADA,
    )
    solicitud_repo.save(sol)

    borrador_repo = InMemoryBorradorRepo()
    orquestar = OrquestarAcciones(
        llm=FakeLLMAdapter(),
        borrador_repo=borrador_repo,
        responsable_email="resp@datecsafake.com",
        bodega_email="bodega@datecsafake.com",
        despacho_email="despacho@datecsafake.com",
        recepcion_email="recepcion@datecsafake.com",
    )
    caso_uso = ProcesarCorreo(
        llm=FakeLLMAdapter(),
        email_reader=inbox,
        ocr=FakeOCRAdapter(),
        embedding=FakeEmbeddingAdapter(dim=768),
        vector_store=FakeVectorStore(),
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=FakeTrazabilidadRepo(),
        crear_solicitud=CrearSolicitud(
            solicitud_repo=solicitud_repo,
            garantia_repo=FakeGarantiaRepo(),
        ),
        orquestar=orquestar,
    )
    result = caso_uso.execute()
    assert result["detalle"][0]["borradores_generados"] == 4
