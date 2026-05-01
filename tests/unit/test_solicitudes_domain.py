import pytest
from datetime import date
from src.solicitudes.domain.entities import SolicitudGarantia, ActaEntrega, EstadoSolicitud


def test_solicitud_inicia_en_estado_nueva():
    s = SolicitudGarantia(
        equipo_id="KYO-001",
        garantia_id="g-1",
        reportado_por="Carlos",
        descripcion_falla="Error de fusor C3100",
    )
    assert s.estado == EstadoSolicitud.NUEVA


def test_flujo_completo_de_estados():
    s = SolicitudGarantia(equipo_id="e1", garantia_id="g1", reportado_por="Ana", descripcion_falla="Falla")
    s.validar()
    assert s.estado == EstadoSolicitud.VALIDADA
    s.despachar()
    assert s.estado == EstadoSolicitud.DESPACHADA
    s.iniciar_reparacion()
    assert s.estado == EstadoSolicitud.EN_REPARACION
    s.devolver()
    assert s.estado == EstadoSolicitud.DEVUELTA
    s.cerrar()
    assert s.estado == EstadoSolicitud.CERRADA


def test_transicion_invalida_lanza_error():
    s = SolicitudGarantia(equipo_id="e1", garantia_id="g1", reportado_por="Ana", descripcion_falla="Falla")
    with pytest.raises(ValueError, match="transición inválida"):
        s.cerrar()


def test_no_se_puede_despachar_sin_validar():
    s = SolicitudGarantia(equipo_id="e1", garantia_id="g1", reportado_por="Ana", descripcion_falla="Falla")
    with pytest.raises(ValueError, match="transición inválida"):
        s.despachar()


def test_acta_entrega_tiene_fecha_por_defecto():
    acta = ActaEntrega(
        solicitud_id="sol-1",
        tecnico_responsable="Carlos Ramírez",
    )
    assert acta.fecha_entrega == date.today()
    assert acta.solicitud_id == "sol-1"
