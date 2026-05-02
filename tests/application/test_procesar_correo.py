from datetime import date, timedelta

from src.agente.application.procesar_correo import ProcesarCorreo
from src.agente.domain.entities import CorreoEntrante, DecisionCorreo, TipoCorreo, DecisionAgente, Accion
from src.agente.domain.ports import LLMPort, EmailReaderPort
from src.agente.infrastructure.email.fake_email_adapter import FakeEmailReaderAdapter
from src.agente.infrastructure.embeddings.fake_embedding_adapter import FakeEmbeddingAdapter
from src.agente.infrastructure.ocr.fake_ocr_adapter import FakeOCRAdapter
from src.agente.infrastructure.vector_store import FakeVectorStoreAdapter
from src.equipos.domain.entities import Equipo, Garantia, TipoEquipo
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from src.solicitudes.domain.entities import EstadoSolicitud
from tests.application.fakes import (
    FakeEquipoRepository, FakeGarantiaRepository,
    FakeSolicitudRepository, FakeTrazabilidadRepository,
)


class StubLLMAdapter(LLMPort):
    """Returns a fixed DecisionCorreo; delegates decide/generate_email to FakeLLM."""

    def __init__(self, decision: DecisionCorreo):
        self._decision = decision

    def decide(self, context: str) -> DecisionAgente:
        return DecisionAgente(accion=Accion.CREAR_SOLICITUD, confianza=0.99,
                              parametros={"equipo_serial": "KYO-TASKalfa-2021-001",
                                          "reportado_por": "Stub"})

    def generate_email(self, context: str) -> dict[str, str]:
        return {"asunto": "Stub", "cuerpo": "Stub"}

    def classify_email(self, asunto: str, cuerpo: str) -> DecisionCorreo:
        return self._decision


def _correo(uid: str = "uid-1", asunto: str = "Asunto", cuerpo: str = "Cuerpo",
            remitente: str = "proveedor@test.com", adjuntos: list | None = None) -> CorreoEntrante:
    return CorreoEntrante(uid=uid, asunto=asunto, cuerpo=cuerpo,
                          remitente=remitente, adjuntos=adjuntos or [])


def _setup(correos: list[CorreoEntrante], decision: DecisionCorreo,
           serial: str = "KYO-001", con_garantia: bool = True):
    equipo_repo = FakeEquipoRepository()
    garantia_repo = FakeGarantiaRepository()
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()

    equipo_repo.save(Equipo(serial=serial, nombre="Test", marca="Test",
                            modelo="Test", tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION,
                            ubicacion_fisica="Piso 1"))
    if con_garantia:
        garantia_repo.save(Garantia(equipo_id=serial, proveedor_id="prov-1",
                                    fecha_inicio=date.today() - timedelta(days=1),
                                    fecha_fin=date.today() + timedelta(days=364),
                                    tipo_cobertura="Total"))

    caso_uso = ProcesarCorreo(
        llm=StubLLMAdapter(decision),
        email_reader=FakeEmailReaderAdapter(correos),
        ocr=FakeOCRAdapter(),
        embedding=FakeEmbeddingAdapter(),
        vector_store=FakeVectorStoreAdapter(),
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=trazabilidad_repo,
        crear_solicitud=CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo),
    )
    return caso_uso, solicitud_repo, trazabilidad_repo


# ── Bandeja vacía ─────────────────────────────────────────────────────────────

def test_bandeja_vacia_retorna_procesados_cero():
    caso_uso, _, _ = _setup([], DecisionCorreo(tipo=TipoCorreo.OTRO, confianza=0.5))
    resultado = caso_uso.execute()
    assert resultado["procesados"] == 0
    assert resultado["detalle"] == []


# ── Acta de entrega ───────────────────────────────────────────────────────────

def test_acta_sin_adjunto_crea_solicitud():
    serial = "KYO-001"
    decision = DecisionCorreo(tipo=TipoCorreo.ACTA_ENTREGA, confianza=0.95, equipo_serial=serial)
    caso_uso, solicitud_repo, _ = _setup([_correo()], decision, serial=serial)

    resultado = caso_uso.execute()

    assert resultado["procesados"] == 1
    assert resultado["detalle"][0]["accion_tomada"] == "solicitud_creada_desde_correo"
    assert len(solicitud_repo.find_all()) == 1


def test_acta_sin_serial_no_crea_solicitud():
    decision = DecisionCorreo(tipo=TipoCorreo.ACTA_ENTREGA, confianza=0.95, equipo_serial="")
    caso_uso, solicitud_repo, _ = _setup([_correo()], decision)

    resultado = caso_uso.execute()

    assert resultado["detalle"][0]["accion_tomada"] == "sin_serial_identificado"
    assert len(solicitud_repo.find_all()) == 0


def test_acta_equipo_sin_garantia_vigente():
    serial = "KYO-SIN-GARANTIA"
    decision = DecisionCorreo(tipo=TipoCorreo.ACTA_ENTREGA, confianza=0.95, equipo_serial=serial)
    caso_uso, solicitud_repo, _ = _setup([_correo()], decision, serial=serial, con_garantia=False)

    resultado = caso_uso.execute()

    assert resultado["detalle"][0]["accion_tomada"] == "equipo_sin_garantia_vigente"
    assert len(solicitud_repo.find_all()) == 0


# ── Actualización de proveedor ────────────────────────────────────────────────

def test_actualizacion_proveedor_actualiza_estado_y_trazabilidad():
    serial = "KYO-001"
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    equipo_repo = FakeEquipoRepository()
    garantia_repo = FakeGarantiaRepository()

    equipo_repo.save(Equipo(serial=serial, nombre="Test", marca="K", modelo="M",
                            tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION, ubicacion_fisica="P1"))
    garantia_repo.save(Garantia(equipo_id=serial, proveedor_id="p1",
                                fecha_inicio=date.today() - timedelta(days=1),
                                fecha_fin=date.today() + timedelta(days=364), tipo_cobertura="Total"))

    from src.solicitudes.domain.entities import SolicitudGarantia
    sol = SolicitudGarantia(equipo_id=serial, reportado_por="Tech",
                            descripcion_falla="Falla fusor", estado=EstadoSolicitud.DESPACHADA)
    solicitud_repo.save(sol)

    decision = DecisionCorreo(tipo=TipoCorreo.ACTUALIZACION_PROVEEDOR, confianza=0.95,
                              equipo_serial=serial, nuevo_estado="en_reparacion")
    caso_uso = ProcesarCorreo(
        llm=StubLLMAdapter(decision),
        email_reader=FakeEmailReaderAdapter([_correo()]),
        ocr=FakeOCRAdapter(), embedding=FakeEmbeddingAdapter(),
        vector_store=FakeVectorStoreAdapter(),
        solicitud_repo=solicitud_repo, trazabilidad_repo=trazabilidad_repo,
        crear_solicitud=CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo),
    )

    resultado = caso_uso.execute()

    assert resultado["detalle"][0]["accion_tomada"] == "estado_actualizado"
    solicitud_actualizada = solicitud_repo.find_by_id(sol.id)
    assert solicitud_actualizada.estado == EstadoSolicitud.EN_REPARACION
    eventos = trazabilidad_repo.find_by_equipo(serial)
    assert len(eventos) == 1
    assert eventos[0].ubicacion_nueva == "en_reparacion"


def test_actualizacion_sin_serial_retorna_sin_serial():
    decision = DecisionCorreo(tipo=TipoCorreo.ACTUALIZACION_PROVEEDOR, confianza=0.95, equipo_serial="")
    caso_uso, _, _ = _setup([_correo()], decision)

    resultado = caso_uso.execute()

    assert resultado["detalle"][0]["accion_tomada"] == "sin_serial_identificado"


def test_actualizacion_sin_solicitud_activa():
    serial = "KYO-SIN-SOLICITUD"
    decision = DecisionCorreo(tipo=TipoCorreo.ACTUALIZACION_PROVEEDOR, confianza=0.95,
                              equipo_serial=serial)
    caso_uso, _, _ = _setup([_correo()], decision, serial=serial)

    resultado = caso_uso.execute()

    assert resultado["detalle"][0]["accion_tomada"] == "solicitud_activa_no_encontrada"


def test_confirmacion_despacho_registra_trazabilidad():
    serial = "KYO-001"
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    equipo_repo = FakeEquipoRepository()
    garantia_repo = FakeGarantiaRepository()

    equipo_repo.save(Equipo(serial=serial, nombre="T", marca="K", modelo="M",
                            tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION, ubicacion_fisica="P1"))
    garantia_repo.save(Garantia(equipo_id=serial, proveedor_id="p1",
                                fecha_inicio=date.today() - timedelta(days=1),
                                fecha_fin=date.today() + timedelta(days=364), tipo_cobertura="Total"))
    from src.solicitudes.domain.entities import SolicitudGarantia
    sol = SolicitudGarantia(equipo_id=serial, reportado_por="Tech",
                            descripcion_falla="Falla", estado=EstadoSolicitud.EN_REPARACION)
    solicitud_repo.save(sol)

    decision = DecisionCorreo(tipo=TipoCorreo.CONFIRMACION_DESPACHO, confianza=0.95,
                              equipo_serial=serial, nuevo_estado="devuelta")
    caso_uso = ProcesarCorreo(
        llm=StubLLMAdapter(decision),
        email_reader=FakeEmailReaderAdapter([_correo()]),
        ocr=FakeOCRAdapter(), embedding=FakeEmbeddingAdapter(),
        vector_store=FakeVectorStoreAdapter(),
        solicitud_repo=solicitud_repo, trazabilidad_repo=trazabilidad_repo,
        crear_solicitud=CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo),
    )

    resultado = caso_uso.execute()

    assert resultado["detalle"][0]["accion_tomada"] == "estado_actualizado"
    assert len(trazabilidad_repo.find_by_equipo(serial)) == 1


# ── Consulta cliente / Otro ───────────────────────────────────────────────────

def test_consulta_cliente_retorna_consulta_registrada():
    decision = DecisionCorreo(tipo=TipoCorreo.CONSULTA_CLIENTE, confianza=0.90)
    caso_uso, _, _ = _setup([_correo()], decision)

    resultado = caso_uso.execute()

    assert resultado["detalle"][0]["accion_tomada"] == "consulta_registrada"


def test_correo_otro_es_ignorado():
    decision = DecisionCorreo(tipo=TipoCorreo.OTRO, confianza=0.60)
    caso_uso, _, _ = _setup([_correo()], decision)

    resultado = caso_uso.execute()

    assert resultado["detalle"][0]["accion_tomada"] == "ignorado"


# ── Marcado como leído ────────────────────────────────────────────────────────

def test_todos_los_correos_se_marcan_como_leidos():
    correos = [_correo("uid-1"), _correo("uid-2"), _correo("uid-3")]
    decision = DecisionCorreo(tipo=TipoCorreo.OTRO, confianza=0.5)
    reader = FakeEmailReaderAdapter(correos)

    caso_uso = ProcesarCorreo(
        llm=StubLLMAdapter(decision),
        email_reader=reader,
        ocr=FakeOCRAdapter(), embedding=FakeEmbeddingAdapter(),
        vector_store=FakeVectorStoreAdapter(),
        solicitud_repo=FakeSolicitudRepository(),
        trazabilidad_repo=FakeTrazabilidadRepository(),
        crear_solicitud=CrearSolicitud(
            solicitud_repo=FakeSolicitudRepository(),
            garantia_repo=FakeGarantiaRepository(),
        ),
    )
    caso_uso.execute()

    assert reader.fetch_unread() == []


def test_multiples_correos_todos_procesados():
    serial = "KYO-001"
    decision = DecisionCorreo(tipo=TipoCorreo.ACTA_ENTREGA, confianza=0.95, equipo_serial=serial)
    correos = [_correo("uid-1"), _correo("uid-2")]
    caso_uso, solicitud_repo, _ = _setup(correos, decision, serial=serial)

    resultado = caso_uso.execute()

    assert resultado["procesados"] == 2
    assert len(solicitud_repo.find_all()) == 2
