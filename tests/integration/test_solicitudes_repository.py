import uuid
from datetime import date
from src.solicitudes.domain.entities import SolicitudGarantia, EstadoSolicitud
from src.solicitudes.infrastructure.repositories import DjangoSolicitudRepository


def _uid() -> str:
    return uuid.uuid4().hex[:8].upper()


def _solicitud(serial: str) -> SolicitudGarantia:
    return SolicitudGarantia(
        equipo_id=serial,
        reportado_por="Técnico Test",
        descripcion_falla="Falla de prueba integración",
    )


def test_solicitud_save_assigns_id():
    repo = DjangoSolicitudRepository()
    sol = _solicitud(f"INT-{_uid()}")

    repo.save(sol)

    assert sol.id != "0"
    assert sol.id.isdigit()


def test_solicitud_find_by_id_round_trip():
    repo = DjangoSolicitudRepository()
    serial = f"INT-{_uid()}"
    sol = _solicitud(serial)
    repo.save(sol)

    result = repo.find_by_id(sol.id)

    assert result is not None
    assert result.equipo_id == serial
    assert result.reportado_por == "Técnico Test"
    assert result.descripcion_falla == "Falla de prueba integración"
    assert result.estado == EstadoSolicitud.NUEVA


def test_solicitud_find_by_id_not_found():
    repo = DjangoSolicitudRepository()
    assert repo.find_by_id("999999999") is None


def test_solicitud_find_by_estado():
    repo = DjangoSolicitudRepository()
    sol = _solicitud(f"INT-{_uid()}")
    repo.save(sol)

    sol.estado = EstadoSolicitud.VALIDADA
    repo.save(sol)

    results = repo.find_by_estado(EstadoSolicitud.VALIDADA)
    ids = [s.id for s in results]
    assert sol.id in ids


def test_solicitud_find_by_estado_excludes_others():
    repo = DjangoSolicitudRepository()
    sol = _solicitud(f"INT-{_uid()}")
    repo.save(sol)

    results = repo.find_by_estado(EstadoSolicitud.CERRADA)
    ids = [s.id for s in results]
    assert sol.id not in ids


def test_solicitud_find_all_includes_saved():
    repo = DjangoSolicitudRepository()
    sol = _solicitud(f"INT-{_uid()}")
    repo.save(sol)

    all_sols = repo.find_all()
    ids = [s.id for s in all_sols]
    assert sol.id in ids


def test_solicitud_save_preserves_fecha_reporte():
    repo = DjangoSolicitudRepository()
    sol = _solicitud(f"INT-{_uid()}")
    repo.save(sol)

    result = repo.find_by_id(sol.id)
    assert result.fecha_reporte == date.today()
