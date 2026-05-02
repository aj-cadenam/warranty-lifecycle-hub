import uuid
from datetime import date, timedelta
from src.equipos.domain.entities import Equipo, Garantia, TipoEquipo, EstadoEquipo
from src.equipos.infrastructure.repositories import DjangoEquipoRepository, DjangoGarantiaRepository


def _uid() -> str:
    return uuid.uuid4().hex[:8].upper()


def _equipo(serial: str) -> Equipo:
    return Equipo(
        serial=serial,
        nombre="Test Equipo",
        marca="Kyocera",
        modelo="TASKalfa",
        tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION,
        ubicacion_fisica="Piso 1",
    )


def _proveedor():
    from src.equipos.infrastructure.django_models import ProveedorModel
    proveedor, _ = ProveedorModel.objects.get_or_create(
        contacto_email="integration@test.com",
        defaults={"nombre": "Test Proveedor", "tiempo_respuesta_dias": 5},
    )
    return proveedor


# ── DjangoEquipoRepository ────────────────────────────────────────────────────

def test_equipo_save_and_find_by_serial():
    repo = DjangoEquipoRepository()
    serial = f"INT-{_uid()}"
    repo.save(_equipo(serial))

    result = repo.find_by_serial(serial)

    assert result is not None
    assert result.serial == serial
    assert result.marca == "Kyocera"
    assert result.tipo == TipoEquipo.MULTIFUNCIONAL_IMPRESION
    assert result.estado == EstadoEquipo.ACTIVO


def test_equipo_find_by_serial_not_found():
    repo = DjangoEquipoRepository()
    assert repo.find_by_serial("NO-EXISTE-NUNCA") is None


def test_equipo_save_updates_existing():
    repo = DjangoEquipoRepository()
    serial = f"INT-{_uid()}"
    repo.save(_equipo(serial))

    updated = Equipo(serial=serial, nombre="Actualizado", marca="Barco",
                     modelo="ClickShare", tipo=TipoEquipo.COLABORACION_AUDIOVISUAL,
                     ubicacion_fisica="Sala B")
    repo.save(updated)

    result = repo.find_by_serial(serial)
    assert result.marca == "Barco"
    assert result.nombre == "Actualizado"


def test_equipo_find_all_includes_saved():
    repo = DjangoEquipoRepository()
    serial = f"INT-{_uid()}"
    repo.save(_equipo(serial))

    all_equipos = repo.find_all()
    serials = [e.serial for e in all_equipos]
    assert serial in serials


# ── DjangoGarantiaRepository ──────────────────────────────────────────────────

def test_garantia_find_vigente_returns_active():
    equipo_repo = DjangoEquipoRepository()
    garantia_repo = DjangoGarantiaRepository()
    serial = f"INT-{_uid()}"
    equipo_repo.save(_equipo(serial))
    proveedor = _proveedor()

    garantia = Garantia(
        equipo_id=serial,
        proveedor_id=str(proveedor.id),
        fecha_inicio=date.today() - timedelta(days=10),
        fecha_fin=date.today() + timedelta(days=355),
        tipo_cobertura="Total",
    )
    garantia_repo.save(garantia)

    result = garantia_repo.find_vigente_by_equipo(serial)

    assert result is not None
    assert result.equipo_id == serial
    assert result.tipo_cobertura == "Total"
    assert result.fecha_fin >= date.today()


def test_garantia_find_vigente_returns_none_when_expired():
    equipo_repo = DjangoEquipoRepository()
    garantia_repo = DjangoGarantiaRepository()
    serial = f"INT-{_uid()}"
    equipo_repo.save(_equipo(serial))
    proveedor = _proveedor()

    from src.equipos.infrastructure.django_models import GarantiaModel
    GarantiaModel.objects.create(
        equipo_serial=serial,
        proveedor=proveedor,
        fecha_inicio=date.today() - timedelta(days=400),
        fecha_fin=date.today() - timedelta(days=30),
        tipo_cobertura="Total",
        estado="vencida",
    )

    result = garantia_repo.find_vigente_by_equipo(serial)
    assert result is None


def test_garantia_find_vigente_returns_none_for_unknown_equipo():
    repo = DjangoGarantiaRepository()
    assert repo.find_vigente_by_equipo("NO-EXISTE-NUNCA") is None
