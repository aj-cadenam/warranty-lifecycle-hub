import pytest
from datetime import date, timedelta
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from src.equipos.domain.entities import Equipo, Garantia, TipoEquipo
from tests.application.fakes import FakeEquipoRepository, FakeGarantiaRepository, FakeSolicitudRepository


def _setup_equipo_con_garantia():
    equipo_repo = FakeEquipoRepository()
    garantia_repo = FakeGarantiaRepository()
    equipo = Equipo(serial="KYO-001", nombre="Kyocera", marca="Kyocera",
                    modelo="TASKalfa", tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION, ubicacion_fisica="Piso 3")
    equipo_repo.save(equipo)
    garantia = Garantia(equipo_id="KYO-001", proveedor_id="prov-1",
                        fecha_inicio=date.today() - timedelta(days=30),
                        fecha_fin=date.today() + timedelta(days=335), tipo_cobertura="Total")
    garantia_repo.save(garantia)
    return equipo_repo, garantia_repo


def test_crear_solicitud_con_garantia_vigente():
    equipo_repo, garantia_repo = _setup_equipo_con_garantia()
    solicitud_repo = FakeSolicitudRepository()
    caso_uso = CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo)
    solicitud = caso_uso.execute(equipo_id="KYO-001", reportado_por="Carlos",
                                  descripcion_falla="Error fusor C3100")
    assert solicitud.equipo_id == "KYO-001"
    assert solicitud_repo.find_by_id(solicitud.id) is not None


def test_crear_solicitud_sin_garantia_vigente_lanza_error():
    garantia_repo = FakeGarantiaRepository()
    solicitud_repo = FakeSolicitudRepository()
    caso_uso = CrearSolicitud(solicitud_repo=solicitud_repo, garantia_repo=garantia_repo)
    with pytest.raises(ValueError, match="no tiene garantía vigente"):
        caso_uso.execute(equipo_id="NO-EXISTE", reportado_por="Carlos", descripcion_falla="Falla")
