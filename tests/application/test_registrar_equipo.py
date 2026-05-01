import pytest
from src.equipos.domain.entities import TipoEquipo
from src.equipos.application.registrar_equipo import RegistrarEquipo
from tests.application.fakes import FakeEquipoRepository


def test_registrar_equipo_lo_persiste():
    repo = FakeEquipoRepository()
    caso_uso = RegistrarEquipo(equipo_repo=repo)
    caso_uso.execute(serial="KYO-001", nombre="Kyocera TASKalfa", marca="Kyocera",
                     modelo="TASKalfa 2553ci", tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION,
                     ubicacion_fisica="Piso 3")
    equipo = repo.find_by_serial("KYO-001")
    assert equipo is not None
    assert equipo.marca == "Kyocera"


def test_registrar_equipo_duplicado_lanza_error():
    repo = FakeEquipoRepository()
    caso_uso = RegistrarEquipo(equipo_repo=repo)
    caso_uso.execute(serial="KYO-001", nombre="Kyocera", marca="Kyocera",
                     modelo="TASKalfa", tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION, ubicacion_fisica="Piso 1")
    with pytest.raises(ValueError, match="serial ya existe"):
        caso_uso.execute(serial="KYO-001", nombre="Otro", marca="Kyocera",
                         modelo="TASKalfa", tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION, ubicacion_fisica="Piso 2")
