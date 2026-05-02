# Django setup is handled by tests/conftest.py (root)
import pytest


@pytest.fixture(scope="session", autouse=True)
def seed_kyocera_fixture(setup_db):
    """Ensure KYO-TASKalfa-2021-001 exists with an active warranty (used by FakeLLMAdapter)."""
    from datetime import date, timedelta
    from src.equipos.infrastructure.django_models import EquipoModel, GarantiaModel, ProveedorModel

    EquipoModel.objects.get_or_create(
        serial="KYO-TASKalfa-2021-001",
        defaults={
            "nombre": "Kyocera TASKalfa 2553ci",
            "marca": "Kyocera",
            "modelo": "TASKalfa 2553ci",
            "tipo": "multifuncional_impresion",
            "ubicacion_fisica": "Piso 3 - Área Administrativa",
            "estado": "activo",
        },
    )
    proveedor, _ = ProveedorModel.objects.get_or_create(
        contacto_email="proveedor@kyocera.com.co",
        defaults={"nombre": "Kyocera Document Solutions", "tiempo_respuesta_dias": 5},
    )
    if not GarantiaModel.objects.filter(
        equipo_serial="KYO-TASKalfa-2021-001",
        fecha_fin__gte=date.today(),
    ).exists():
        GarantiaModel.objects.create(
            equipo_serial="KYO-TASKalfa-2021-001",
            proveedor=proveedor,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=1095),
            tipo_cobertura="total",
            estado="vigente",
        )
