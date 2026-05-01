from datetime import date, timedelta, datetime
from src.seguimiento.application.verificar_estado_semanal import VerificarEstadoSemanal
from src.seguimiento.domain.entities import EstadoBorrador, DestinatarioTipo
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.trazabilidad.domain.entities import EventoTrazabilidad, MetodoRegistro
from tests.application.fakes import (
    FakeSolicitudRepository, FakeTrazabilidadRepository,
    FakeBorradorCorreoRepository, FakeEventoSeguimientoRepository,
)
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter


def _solicitud_despachada_hace_n_dias(n: int) -> SolicitudGarantia:
    s = SolicitudGarantia(
        equipo_id="KYO-001", garantia_id="g-1",
        reportado_por="Carlos", descripcion_falla="Falla fusor"
    )
    s.validar()
    s.despachar()
    return s


def _evento_hace_n_dias(solicitud_id: str, n: int) -> EventoTrazabilidad:
    return EventoTrazabilidad(
        equipo_id="KYO-001", solicitud_id=solicitud_id,
        ubicacion_anterior="Almacén", ubicacion_nueva="Proveedor Kyocera",
        responsable="Carlos", metodo_registro=MetodoRegistro.MANUAL,
        timestamp=datetime.now() - timedelta(days=n),
    )


def test_genera_borrador_cuando_timeout_superado():
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    borrador_repo = FakeBorradorCorreoRepository()
    seguimiento_repo = FakeEventoSeguimientoRepository()

    solicitud = _solicitud_despachada_hace_n_dias(8)
    solicitud_repo.save(solicitud)
    evento = _evento_hace_n_dias(solicitud.id, 8)
    trazabilidad_repo.save(evento)

    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo,
        trazabilidad_repo=trazabilidad_repo,
        borrador_repo=borrador_repo,
        seguimiento_repo=seguimiento_repo,
        llm=FakeLLMAdapter(),
        timeout_proveedor_dias=7,
        proveedor_email="soporte@kyocera.co",
    )
    caso_uso.execute()

    borradores = borrador_repo.find_pendientes()
    assert len(borradores) == 1
    assert borradores[0].destinatario_tipo == DestinatarioTipo.PROVEEDOR
    assert borradores[0].estado == EstadoBorrador.PENDIENTE_APROBACION


def test_no_genera_borrador_si_ya_hay_uno_pendiente():
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    borrador_repo = FakeBorradorCorreoRepository()
    seguimiento_repo = FakeEventoSeguimientoRepository()

    solicitud = _solicitud_despachada_hace_n_dias(10)
    solicitud_repo.save(solicitud)
    trazabilidad_repo.save(_evento_hace_n_dias(solicitud.id, 10))

    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo, trazabilidad_repo=trazabilidad_repo,
        borrador_repo=borrador_repo, seguimiento_repo=seguimiento_repo,
        llm=FakeLLMAdapter(), timeout_proveedor_dias=7,
        proveedor_email="soporte@kyocera.co",
    )
    caso_uso.execute()
    caso_uso.execute()  # segunda ejecución — debe ser idempotente

    assert len(borrador_repo.find_pendientes()) == 1


def test_no_genera_borrador_si_no_supera_timeout():
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    borrador_repo = FakeBorradorCorreoRepository()
    seguimiento_repo = FakeEventoSeguimientoRepository()

    solicitud = _solicitud_despachada_hace_n_dias(3)
    solicitud_repo.save(solicitud)
    trazabilidad_repo.save(_evento_hace_n_dias(solicitud.id, 3))

    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo, trazabilidad_repo=trazabilidad_repo,
        borrador_repo=borrador_repo, seguimiento_repo=seguimiento_repo,
        llm=FakeLLMAdapter(), timeout_proveedor_dias=7,
        proveedor_email="soporte@kyocera.co",
    )
    caso_uso.execute()

    assert len(borrador_repo.find_pendientes()) == 0


def test_registra_evento_seguimiento_en_verificacion():
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    borrador_repo = FakeBorradorCorreoRepository()
    seguimiento_repo = FakeEventoSeguimientoRepository()

    solicitud = _solicitud_despachada_hace_n_dias(5)
    solicitud_repo.save(solicitud)
    trazabilidad_repo.save(_evento_hace_n_dias(solicitud.id, 5))

    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo, trazabilidad_repo=trazabilidad_repo,
        borrador_repo=borrador_repo, seguimiento_repo=seguimiento_repo,
        llm=FakeLLMAdapter(), timeout_proveedor_dias=7,
        proveedor_email="soporte@kyocera.co",
    )
    caso_uso.execute()

    eventos = seguimiento_repo.find_by_solicitud(solicitud.id)
    assert len(eventos) == 1
    assert eventos[0].tipo_evento == "verificacion_semanal"
    assert eventos[0].dias_sin_respuesta == 5


def test_no_genera_borrador_sin_eventos_trazabilidad():
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    borrador_repo = FakeBorradorCorreoRepository()
    seguimiento_repo = FakeEventoSeguimientoRepository()

    solicitud = _solicitud_despachada_hace_n_dias(10)
    solicitud_repo.save(solicitud)
    # No se agrega evento de trazabilidad

    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo, trazabilidad_repo=trazabilidad_repo,
        borrador_repo=borrador_repo, seguimiento_repo=seguimiento_repo,
        llm=FakeLLMAdapter(), timeout_proveedor_dias=7,
        proveedor_email="soporte@kyocera.co",
    )
    caso_uso.execute()

    assert len(borrador_repo.find_pendientes()) == 0


def test_verifica_solicitudes_en_reparacion():
    solicitud_repo = FakeSolicitudRepository()
    trazabilidad_repo = FakeTrazabilidadRepository()
    borrador_repo = FakeBorradorCorreoRepository()
    seguimiento_repo = FakeEventoSeguimientoRepository()

    solicitud = SolicitudGarantia(
        equipo_id="BAR-CS-001", garantia_id="g-2",
        reportado_por="Luis", descripcion_falla="No enciende"
    )
    solicitud.validar()
    solicitud.despachar()
    solicitud.iniciar_reparacion()
    solicitud_repo.save(solicitud)
    trazabilidad_repo.save(_evento_hace_n_dias(solicitud.id, 9))

    caso_uso = VerificarEstadoSemanal(
        solicitud_repo=solicitud_repo, trazabilidad_repo=trazabilidad_repo,
        borrador_repo=borrador_repo, seguimiento_repo=seguimiento_repo,
        llm=FakeLLMAdapter(), timeout_proveedor_dias=7,
        proveedor_email="soporte@barco.co",
    )
    caso_uso.execute()

    assert len(borrador_repo.find_pendientes()) == 1
