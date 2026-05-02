import uuid
from datetime import datetime, timedelta
from src.trazabilidad.domain.entities import EventoTrazabilidad, MetodoRegistro
from src.trazabilidad.infrastructure.repositories import DjangoTrazabilidadRepository


def _uid() -> str:
    return uuid.uuid4().hex[:8].upper()


def _evento(equipo_id: str, solicitud_id: str = "1", ubicacion_nueva: str = "Taller") -> EventoTrazabilidad:
    return EventoTrazabilidad(
        equipo_id=equipo_id,
        solicitud_id=solicitud_id,
        ubicacion_anterior="Bodega",
        ubicacion_nueva=ubicacion_nueva,
        responsable="Técnico Test",
        metodo_registro=MetodoRegistro.MANUAL,
    )


def test_trazabilidad_save_assigns_id():
    repo = DjangoTrazabilidadRepository()
    evento = _evento(f"INT-{_uid()}")

    repo.save(evento)

    assert evento.id != ""
    assert evento.id.isdigit()


def test_trazabilidad_find_by_equipo():
    repo = DjangoTrazabilidadRepository()
    equipo_id = f"INT-{_uid()}"
    evento = _evento(equipo_id)
    repo.save(evento)

    results = repo.find_by_equipo(equipo_id)

    assert len(results) >= 1
    assert any(e.equipo_id == equipo_id for e in results)


def test_trazabilidad_find_by_equipo_empty_for_unknown():
    repo = DjangoTrazabilidadRepository()
    assert repo.find_by_equipo("NO-EXISTE-NUNCA") == []


def test_trazabilidad_find_by_solicitud():
    repo = DjangoTrazabilidadRepository()
    equipo_id = f"INT-{_uid()}"
    solicitud_id = str(int(uuid.uuid4().int % 900000) + 100000)
    evento = _evento(equipo_id, solicitud_id=solicitud_id)
    repo.save(evento)

    results = repo.find_by_solicitud(solicitud_id)

    assert len(results) >= 1
    assert all(e.solicitud_id == solicitud_id for e in results)


def test_trazabilidad_find_ultimo_evento_returns_most_recent():
    repo = DjangoTrazabilidadRepository()
    equipo_id = f"INT-{_uid()}"
    solicitud_id = str(int(uuid.uuid4().int % 900000) + 100000)

    evento_viejo = _evento(equipo_id, solicitud_id, ubicacion_nueva="Taller Inicial")
    evento_viejo.timestamp = datetime.now() - timedelta(days=5)
    repo.save(evento_viejo)

    evento_reciente = _evento(equipo_id, solicitud_id, ubicacion_nueva="Proveedor")
    repo.save(evento_reciente)

    ultimo = repo.find_ultimo_evento(solicitud_id)

    assert ultimo is not None
    assert ultimo.ubicacion_nueva == "Proveedor"


def test_trazabilidad_find_ultimo_evento_none_when_empty():
    repo = DjangoTrazabilidadRepository()
    solicitud_id = str(int(uuid.uuid4().int % 900000) + 100000)
    assert repo.find_ultimo_evento(solicitud_id) is None


def test_trazabilidad_round_trip_fields():
    repo = DjangoTrazabilidadRepository()
    equipo_id = f"INT-{_uid()}"
    evento = _evento(equipo_id)
    repo.save(evento)

    results = repo.find_by_equipo(equipo_id)
    saved = next(e for e in results if e.equipo_id == equipo_id)

    assert saved.ubicacion_anterior == "Bodega"
    assert saved.ubicacion_nueva == "Taller"
    assert saved.responsable == "Técnico Test"
    assert saved.metodo_registro == MetodoRegistro.MANUAL
