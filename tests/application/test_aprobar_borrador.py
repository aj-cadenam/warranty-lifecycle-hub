import pytest
from src.seguimiento.application.aprobar_borrador import AprobarBorrador
from src.seguimiento.application.rechazar_borrador import RechazarBorrador
from src.seguimiento.domain.entities import BorradorCorreo, DestinatarioTipo, EstadoBorrador
from tests.application.fakes import FakeBorradorCorreoRepository, FakeEmailAdapter


def _crear_borrador(repo):
    b = BorradorCorreo(solicitud_id="sol-1", destinatario_tipo=DestinatarioTipo.PROVEEDOR,
                       destinatario_email="soporte@kyocera.co", asunto="Seguimiento garantía",
                       cuerpo="Estimados, solicitamos amablemente una actualización...")
    repo.save(b)
    return b


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
