import pytest
from src.seguimiento.domain.entities import BorradorCorreo, EstadoBorrador, DestinatarioTipo


def test_borrador_inicia_pendiente_aprobacion():
    b = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.PROVEEDOR,
        destinatario_email="soporte@kyocera.co",
        asunto="Seguimiento garantía",
        cuerpo="Estimados, solicitamos amablemente...",
    )
    assert b.estado == EstadoBorrador.PENDIENTE_APROBACION


def test_aprobar_registra_aprobador():
    b = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.PROVEEDOR,
        destinatario_email="soporte@kyocera.co",
        asunto="Seguimiento",
        cuerpo="...",
    )
    b.aprobar(aprobado_por="juan@datecsafake.com")
    assert b.estado == EstadoBorrador.APROBADO
    assert b.aprobado_por == "juan@datecsafake.com"


def test_marcar_enviado_requiere_aprobacion():
    b = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.PROVEEDOR,
        destinatario_email="soporte@kyocera.co",
        asunto="Seguimiento",
        cuerpo="...",
    )
    with pytest.raises(ValueError, match="no está aprobado"):
        b.marcar_enviado()


def test_borrador_ya_enviado_no_se_puede_volver_a_aprobar():
    b = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.CLIENTE,
        destinatario_email="cliente@empresa.co",
        asunto="Seguimiento",
        cuerpo="...",
    )
    b.aprobar(aprobado_por="ana@datecsafake.com")
    b.marcar_enviado()
    with pytest.raises(ValueError, match="ya fue enviado"):
        b.aprobar(aprobado_por="otro@datecsafake.com")


def test_rechazar_borrador():
    b = BorradorCorreo(
        solicitud_id="sol-1",
        destinatario_tipo=DestinatarioTipo.PROVEEDOR,
        destinatario_email="soporte@kyocera.co",
        asunto="Seguimiento",
        cuerpo="...",
    )
    b.rechazar(motivo="Tono incorrecto")
    assert b.estado == EstadoBorrador.RECHAZADO
    assert b.motivo_rechazo == "Tono incorrecto"
