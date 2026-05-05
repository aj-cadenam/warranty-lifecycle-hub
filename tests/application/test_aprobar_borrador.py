import pytest
from src.seguimiento.application.aprobar_borrador import AprobarBorrador
from src.seguimiento.application.rechazar_borrador import RechazarBorrador
from src.seguimiento.domain.entities import BorradorCorreo, DestinatarioTipo, EstadoBorrador
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from tests.application.fakes import FakeBorradorCorreoRepository, FakeEmailAdapter, FakeSolicitudRepository


def _crear_borrador(repo, tipo=DestinatarioTipo.PROVEEDOR, solicitud_id="sol-1"):
    b = BorradorCorreo(solicitud_id=solicitud_id, destinatario_tipo=tipo,
                       destinatario_email="soporte@kyocera.co", asunto="Seguimiento garantía",
                       cuerpo="Estimados, solicitamos amablemente una actualización...")
    repo.save(b)
    return b


def _solicitud_devuelta(sol_id="sol-1"):
    s = SolicitudGarantia(
        equipo_id="KYO-001", garantia_id="gar-1",
        reportado_por="tecnico@datecsafake.com", descripcion_falla="Falla fusor",
    )
    s.id = sol_id
    # Avanzar hasta estado devuelta
    s.validar(); s.despachar(); s.iniciar_reparacion(); s.devolver()
    return s


def test_aprobar_borrador_envia_correo_y_marca_enviado():
    repo = FakeBorradorCorreoRepository()
    email_adapter = FakeEmailAdapter()
    borrador = _crear_borrador(repo)
    AprobarBorrador(borrador_repo=repo, email_adapter=email_adapter).execute(
        borrador_id=borrador.id, aprobado_por="juan@datecsafake.com"
    )
    b = repo.find_by_id(borrador.id)
    assert b.estado == EstadoBorrador.ENVIADO
    assert b.aprobado_por == "juan@datecsafake.com"
    assert len(email_adapter.sent) == 1
    assert email_adapter.sent[0]["to"] == "soporte@kyocera.co"


def test_rechazar_borrador_no_envia_correo():
    repo = FakeBorradorCorreoRepository()
    email_adapter = FakeEmailAdapter()
    borrador = _crear_borrador(repo)
    RechazarBorrador(borrador_repo=repo).execute(borrador_id=borrador.id, motivo="Tono incorrecto")
    b = repo.find_by_id(borrador.id)
    assert b.estado == EstadoBorrador.RECHAZADO
    assert len(email_adapter.sent) == 0


def test_aprobar_borrador_inexistente_lanza_error():
    repo = FakeBorradorCorreoRepository()
    email_adapter = FakeEmailAdapter()
    with pytest.raises(ValueError, match="no encontrado"):
        AprobarBorrador(borrador_repo=repo, email_adapter=email_adapter).execute(
            borrador_id="no-existe", aprobado_por="juan@datecsafake.com"
        )


def test_aprobar_borrador_bodega_cierra_solicitud_devuelta():
    borrador_repo = FakeBorradorCorreoRepository()
    solicitud_repo = FakeSolicitudRepository()
    email_adapter = FakeEmailAdapter()

    solicitud = _solicitud_devuelta("sol-1")
    solicitud_repo.save(solicitud)
    borrador = _crear_borrador(borrador_repo, tipo=DestinatarioTipo.BODEGA, solicitud_id="sol-1")

    resultado = AprobarBorrador(
        borrador_repo=borrador_repo,
        email_adapter=email_adapter,
        solicitud_repo=solicitud_repo,
    ).execute(borrador_id=borrador.id, aprobado_por="juan@datecsafake.com")

    assert resultado["solicitud_cerrada"] is True
    sol = solicitud_repo.find_by_id("sol-1")
    assert sol.estado == EstadoSolicitud.CERRADA


def test_aprobar_borrador_responsable_no_cierra_solicitud():
    borrador_repo = FakeBorradorCorreoRepository()
    solicitud_repo = FakeSolicitudRepository()
    email_adapter = FakeEmailAdapter()

    solicitud = _solicitud_devuelta("sol-2")
    solicitud_repo.save(solicitud)
    borrador = _crear_borrador(borrador_repo, tipo=DestinatarioTipo.RESPONSABLE, solicitud_id="sol-2")

    resultado = AprobarBorrador(
        borrador_repo=borrador_repo,
        email_adapter=email_adapter,
        solicitud_repo=solicitud_repo,
    ).execute(borrador_id=borrador.id, aprobado_por="juan@datecsafake.com")

    assert resultado["solicitud_cerrada"] is False
    sol = solicitud_repo.find_by_id("sol-2")
    assert sol.estado == EstadoSolicitud.DEVUELTA


def test_aprobar_borrador_bodega_no_cierra_si_no_esta_devuelta():
    borrador_repo = FakeBorradorCorreoRepository()
    solicitud_repo = FakeSolicitudRepository()
    email_adapter = FakeEmailAdapter()

    # Solicitud en en_reparacion, no devuelta
    s = SolicitudGarantia(
        equipo_id="KYO-001", garantia_id="gar-1",
        reportado_por="tecnico@datecsafake.com", descripcion_falla="Falla",
    )
    s.id = "sol-3"
    s.validar(); s.despachar(); s.iniciar_reparacion()
    solicitud_repo.save(s)
    borrador = _crear_borrador(borrador_repo, tipo=DestinatarioTipo.BODEGA, solicitud_id="sol-3")

    resultado = AprobarBorrador(
        borrador_repo=borrador_repo,
        email_adapter=email_adapter,
        solicitud_repo=solicitud_repo,
    ).execute(borrador_id=borrador.id, aprobado_por="juan@datecsafake.com")

    assert resultado["solicitud_cerrada"] is False
    assert solicitud_repo.find_by_id("sol-3").estado == EstadoSolicitud.EN_REPARACION
