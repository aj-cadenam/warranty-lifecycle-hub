from src.agente.domain.entities import TipoCorreo
from src.seguimiento.domain.entities import DestinatarioTipo, BorradorCorreo


def test_tipo_correo_tiene_confirmacion_devolucion():
    assert TipoCorreo.CONFIRMACION_DEVOLUCION == "confirmacion_devolucion"


def test_destinatario_tipo_tiene_internos():
    assert DestinatarioTipo.RESPONSABLE == "responsable"
    assert DestinatarioTipo.BODEGA == "bodega"
    assert DestinatarioTipo.DESPACHO == "despacho"
    assert DestinatarioTipo.RECEPCION == "recepcion"


def test_borrador_correo_tiene_dias_sin_respuesta():
    b = BorradorCorreo()
    assert b.dias_sin_respuesta == 0


def test_borrador_correo_acepta_dias_sin_respuesta():
    b = BorradorCorreo(dias_sin_respuesta=12)
    assert b.dias_sin_respuesta == 12
