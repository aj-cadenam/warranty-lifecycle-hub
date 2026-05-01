from datetime import datetime
from src.trazabilidad.domain.entities import EventoTrazabilidad, MetodoRegistro


def test_evento_trazabilidad_registra_movimiento():
    evento = EventoTrazabilidad(
        equipo_id="KYO-001",
        solicitud_id="sol-1",
        ubicacion_anterior="Piso 3",
        ubicacion_nueva="Almacén Servicio Técnico",
        responsable="Carlos Técnico",
        metodo_registro=MetodoRegistro.MANUAL,
    )
    assert evento.ubicacion_nueva == "Almacén Servicio Técnico"
    assert evento.metodo_registro == MetodoRegistro.MANUAL


def test_evento_tiene_timestamp_automatico():
    evento = EventoTrazabilidad(
        equipo_id="e1", solicitud_id="s1",
        ubicacion_anterior="A", ubicacion_nueva="B",
        responsable="Carlos", metodo_registro=MetodoRegistro.AGENTE_OCR,
    )
    assert isinstance(evento.timestamp, datetime)


def test_metodos_de_registro_disponibles():
    assert MetodoRegistro.MANUAL.value == "manual"
    assert MetodoRegistro.AGENTE_OCR.value == "agente_ocr"
    assert MetodoRegistro.AGENTE_EMAIL.value == "agente_email"
