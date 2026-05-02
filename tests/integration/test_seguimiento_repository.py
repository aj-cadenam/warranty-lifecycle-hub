import uuid
from src.seguimiento.domain.entities import (
    BorradorCorreo, EventoSeguimiento, EstadoBorrador, DestinatarioTipo
)
from src.seguimiento.infrastructure.repositories import (
    DjangoBorradorCorreoRepository, DjangoEventoSeguimientoRepository
)


def _uid() -> str:
    return uuid.uuid4().hex[:8].upper()


def _solicitud_id() -> str:
    return str(int(uuid.uuid4().int % 900000) + 100000)


def _borrador(solicitud_id: str) -> BorradorCorreo:
    return BorradorCorreo(
        solicitud_id=solicitud_id,
        destinatario_tipo=DestinatarioTipo.PROVEEDOR,
        destinatario_email="proveedor@test.com",
        asunto="Seguimiento solicitud de garantía",
        cuerpo="Estimado proveedor, solicitamos una actualización.",
    )


# ── DjangoBorradorCorreoRepository ───────────────────────────────────────────

def test_borrador_save_assigns_id():
    repo = DjangoBorradorCorreoRepository()
    borrador = _borrador(_solicitud_id())

    repo.save(borrador)

    assert borrador.id.isdigit()
    assert int(borrador.id) > 0


def test_borrador_find_by_id_round_trip():
    repo = DjangoBorradorCorreoRepository()
    sid = _solicitud_id()
    borrador = _borrador(sid)
    repo.save(borrador)

    result = repo.find_by_id(borrador.id)

    assert result is not None
    assert result.solicitud_id == sid
    assert result.destinatario_email == "proveedor@test.com"
    assert result.asunto == "Seguimiento solicitud de garantía"
    assert result.estado == EstadoBorrador.PENDIENTE_APROBACION


def test_borrador_find_by_id_not_found():
    repo = DjangoBorradorCorreoRepository()
    assert repo.find_by_id("999999999") is None


def test_borrador_find_pendientes_includes_new():
    repo = DjangoBorradorCorreoRepository()
    borrador = _borrador(_solicitud_id())
    repo.save(borrador)

    pendientes = repo.find_pendientes()
    ids = [b.id for b in pendientes]
    assert borrador.id in ids


def test_borrador_find_pendientes_excludes_aprobado():
    repo = DjangoBorradorCorreoRepository()
    borrador = _borrador(_solicitud_id())
    repo.save(borrador)

    borrador.estado = EstadoBorrador.APROBADO
    borrador.aprobado_por = "admin"
    repo.save(borrador)

    pendientes = repo.find_pendientes()
    ids = [b.id for b in pendientes]
    assert borrador.id not in ids


def test_borrador_find_by_solicitud_y_estado():
    repo = DjangoBorradorCorreoRepository()
    sid = _solicitud_id()
    borrador = _borrador(sid)
    repo.save(borrador)

    result = repo.find_by_solicitud_y_estado(sid, EstadoBorrador.PENDIENTE_APROBACION)

    assert result is not None
    assert result.solicitud_id == sid


def test_borrador_find_by_solicitud_y_estado_returns_none_when_not_matching():
    repo = DjangoBorradorCorreoRepository()
    sid = _solicitud_id()
    borrador = _borrador(sid)
    repo.save(borrador)

    result = repo.find_by_solicitud_y_estado(sid, EstadoBorrador.APROBADO)
    assert result is None


def test_borrador_save_updates_existing():
    repo = DjangoBorradorCorreoRepository()
    borrador = _borrador(_solicitud_id())
    repo.save(borrador)
    original_id = borrador.id

    borrador.cuerpo = "Cuerpo actualizado por el usuario."
    repo.save(borrador)

    result = repo.find_by_id(original_id)
    assert result.cuerpo == "Cuerpo actualizado por el usuario."


# ── DjangoEventoSeguimientoRepository ────────────────────────────────────────

def test_evento_seguimiento_save_and_find():
    repo = DjangoEventoSeguimientoRepository()
    sid = _solicitud_id()
    evento = EventoSeguimiento(
        solicitud_id=sid,
        tipo_evento="verificacion_semanal",
        descripcion="15 días sin respuesta del proveedor",
        dias_sin_respuesta=15,
    )

    repo.save(evento)

    results = repo.find_by_solicitud(sid)
    assert len(results) >= 1
    found = next(e for e in results if e.tipo_evento == "verificacion_semanal")
    assert found.descripcion == "15 días sin respuesta del proveedor"
    assert found.dias_sin_respuesta == 15


def test_evento_seguimiento_find_by_solicitud_empty():
    repo = DjangoEventoSeguimientoRepository()
    assert repo.find_by_solicitud(_solicitud_id()) == []


def test_evento_seguimiento_multiple_eventos():
    repo = DjangoEventoSeguimientoRepository()
    sid = _solicitud_id()

    repo.save(EventoSeguimiento(solicitud_id=sid, tipo_evento="verificacion_semanal",
                                descripcion="Semana 1", dias_sin_respuesta=7))
    repo.save(EventoSeguimiento(solicitud_id=sid, tipo_evento="verificacion_semanal",
                                descripcion="Semana 2", dias_sin_respuesta=14))

    results = repo.find_by_solicitud(sid)
    assert len(results) == 2
