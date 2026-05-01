import pytest
from datetime import date, timedelta
from src.equipos.domain.entities import (
    Equipo, Garantia, Proveedor, TipoEquipo, EstadoGarantia, EstadoEquipo
)


def test_equipo_se_crea_con_datos_validos():
    equipo = Equipo(
        serial="KYO-TASKalfa-2021-001",
        nombre="Multifuncional Kyocera TASKalfa 2553ci",
        marca="Kyocera",
        modelo="TASKalfa 2553ci",
        tipo=TipoEquipo.MULTIFUNCIONAL_IMPRESION,
        ubicacion_fisica="Piso 3 - Área Administrativa",
    )
    assert equipo.serial == "KYO-TASKalfa-2021-001"
    assert equipo.tipo == TipoEquipo.MULTIFUNCIONAL_IMPRESION
    assert equipo.estado == EstadoEquipo.ACTIVO


def test_garantia_vigente_cuando_fecha_fin_es_futura():
    garantia = Garantia(
        equipo_id="KYO-TASKalfa-2021-001",
        proveedor_id="prov-1",
        fecha_inicio=date.today() - timedelta(days=30),
        fecha_fin=date.today() + timedelta(days=335),
        tipo_cobertura="Total",
    )
    assert garantia.esta_vigente()
    assert garantia.estado == EstadoGarantia.VIGENTE


def test_garantia_vencida_cuando_fecha_fin_es_pasada():
    garantia = Garantia(
        equipo_id="KYO-TASKalfa-2021-001",
        proveedor_id="prov-1",
        fecha_inicio=date.today() - timedelta(days=400),
        fecha_fin=date.today() - timedelta(days=35),
        tipo_cobertura="Total",
    )
    assert not garantia.esta_vigente()
    assert garantia.estado == EstadoGarantia.VENCIDA


def test_proveedor_tiene_tiempo_respuesta_por_defecto():
    proveedor = Proveedor(
        nombre="Kyocera Colombia",
        contacto_email="soporte@kyocera.co"
    )
    assert proveedor.tiempo_respuesta_dias == 5


def test_todos_los_tipos_de_equipo_datecsa_existen():
    tipos = [t.value for t in TipoEquipo]
    assert "multifuncional_impresion" in tipos
    assert "colaboracion_audiovisual" in tipos
    assert "audio_corporativo" in tipos
    assert "automatizacion_sala" in tipos
    assert "senalizacion_digital" in tipos
    assert "videoconferencia" in tipos
