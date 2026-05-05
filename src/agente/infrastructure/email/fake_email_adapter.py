from datetime import datetime
from src.agente.domain.ports import EmailPort, EmailReaderPort
from src.agente.domain.entities import CorreoEntrante

# ── Brand → provider email ────────────────────────────────────────────────────
_PROVEEDOR_EMAIL = {
    "KYO": "garantias@kyocera.com.co",
    "BAR": "soporte@barco.com",
    "BSP": "garantias@bosepro.com",
    "CRE": "soporte@crestron-lac.com",
    "LG":  "garantias@lg-business.com.co",
}
_CLIENTES = [
    "jperez@constructoraandina.com",
    "mgarcia@grupobancolombia.com",
    "ltorres@ecopetrol.com.co",
    "rcardona@gruposura.com",
    "avalencia@telmex.com.co",
]

def _proveedor(serial: str) -> str:
    prefix = serial.split("-")[0]
    return _PROVEEDOR_EMAIL.get(prefix, f"soporte@proveedor.com")


def build_dynamic_inbox(solicitudes: list) -> list[CorreoEntrante]:
    """Genera correos fake relevantes para el estado actual de cada solicitud."""
    correos: list[CorreoEntrante] = []
    cliente_idx = 0

    for i, sol in enumerate(solicitudes):
        estado = sol.estado.value if hasattr(sol.estado, "value") else str(sol.estado)
        serial = sol.equipo_id
        uid = f"dyn-{i+1:03d}"
        prov = _proveedor(serial)

        if estado == "despachada":
            correos.append(CorreoEntrante(
                uid=uid,
                asunto=f"Confirmación recepción equipo {serial}",
                cuerpo=(
                    f"Estimados señores Datecsa, confirmamos la recepción del equipo serial {serial}. "
                    f"Nuestro equipo técnico iniciará el diagnóstico en las próximas 48 horas "
                    f"y les informaremos los hallazgos. Quedo atento a cualquier consulta."
                ),
                remitente=prov,
                adjuntos=[],
                fecha=datetime.now(),
            ))

        elif estado == "en_reparacion":
            correos.append(CorreoEntrante(
                uid=uid,
                asunto=f"Diagnóstico completado — equipo listo para retiro {serial}",
                cuerpo=(
                    f"Estimados, el equipo serial {serial} fue reparado exitosamente. "
                    f"Se reemplazó la pieza defectuosa y se realizaron pruebas de funcionamiento "
                    f"con resultados satisfactorios. El equipo está disponible para retiro o devolución. "
                    f"Por favor confirmen el método de envío preferido."
                ),
                remitente=prov,
                adjuntos=[],
                fecha=datetime.now(),
            ))

        elif estado == "validada":
            cliente = _CLIENTES[cliente_idx % len(_CLIENTES)]
            cliente_idx += 1
            correos.append(CorreoEntrante(
                uid=uid,
                asunto=f"Consulta estado garantía equipo {serial}",
                cuerpo=(
                    f"Buenos días, le escribo para saber en qué estado se encuentra la garantía "
                    f"del equipo serial {serial}. Ya llevamos varios días sin el equipo y está "
                    f"afectando la operación. ¿Podría indicarnos una fecha estimada de entrega? "
                    f"Quedo pendiente."
                ),
                remitente=cliente,
                adjuntos=[],
                fecha=datetime.now(),
            ))

        elif estado == "devuelta":
            cliente = _CLIENTES[cliente_idx % len(_CLIENTES)]
            cliente_idx += 1
            correos.append(CorreoEntrante(
                uid=uid,
                asunto=f"RE: Devolución equipo — Confirmamos recepción {serial}",
                cuerpo=(
                    f"Buenas tardes, confirmamos que recibimos el equipo serial {serial} "
                    f"en perfectas condiciones. Ya fue instalado y está funcionando correctamente. "
                    f"Muchas gracias por el seguimiento y la gestión."
                ),
                remitente=_CLIENTES[cliente_idx % len(_CLIENTES)],
                adjuntos=[],
                fecha=datetime.now(),
            ))

        elif estado == "nueva":
            correos.append(CorreoEntrante(
                uid=uid,
                asunto=f"RE: Solicitud garantía {serial} — Acuse de recibo",
                cuerpo=(
                    f"Estimados Datecsa, acusamos recibo de la solicitud de garantía para el equipo "
                    f"serial {serial}. Por favor confirmen la dirección de despacho para coordinar "
                    f"la recolección del equipo."
                ),
                remitente=prov,
                adjuntos=[],
                fecha=datetime.now(),
            ))

    # ── Correos extra siempre presentes ──────────────────────────────────────
    n = len(correos)

    # Acta de entrega de equipo sin solicitud activa → crea nueva solicitud
    correos.append(CorreoEntrante(
        uid=f"dyn-extra-001",
        asunto="Acta de entrega — Crestron TSW-1070 CRE-TSW-2024-009",
        cuerpo=(
            "Buen día, adjunto el acta de entrega del equipo Crestron TSW-1070 "
            "serial CRE-TSW-2024-009 de la sala de conferencias piso 8. "
            "Falla: pantalla táctil no responde al tacto en la zona superior izquierda."
        ),
        remitente="tecnico.interno@datecsafake.com",
        adjuntos=[],
        fecha=datetime.now(),
    ))

    # Correo que debe ser ignorado
    correos.append(CorreoEntrante(
        uid=f"dyn-extra-002",
        asunto="Kyocera Partner Summit 2026 — Confirmación asistencia",
        cuerpo=(
            "Estimados partners, les recordamos que el Partner Summit de Kyocera se realizará "
            "el 20 de mayo en Bogotá. Por favor confirmen su asistencia antes del 10 de mayo."
        ),
        remitente="eventos@kyocera.com.co",
        adjuntos=[],
        fecha=datetime.now(),
    ))

    return correos

_FAKE_INBOX: list[CorreoEntrante] = [
    # 1 — Acta de entrega de nuevo equipo (crea solicitud)
    CorreoEntrante(
        uid="fake-001",
        asunto="Acta de entrega - Kyocera TASKalfa KYO-TASKalfa-2021-001",
        cuerpo="Adjunto acta de entrega del equipo Kyocera TASKalfa serial KYO-TASKalfa-2021-001. Falla: Error fusor C3100 — falla en calentamiento al inicio del día.",
        remitente="tecnico@datecsafake.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # 2 — Proveedor confirma recepción (actualiza estado → en_reparacion)
    CorreoEntrante(
        uid="fake-002",
        asunto="RE: Solicitud garantía BAR-CS-2022-014 - Confirmación recepción",
        cuerpo="Estimados señores Datecsa, confirmamos la recepción del equipo Barco ClickShare serial BAR-CS-2022-014. Nuestro equipo técnico realizará el diagnóstico en los próximos 3 días hábiles y les informaremos los hallazgos.",
        remitente="soporte@barco.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # 3 — Proveedor informa reparación completa y despacho de vuelta (confirmacion_devolucion)
    CorreoEntrante(
        uid="fake-003",
        asunto="Equipo reparado y despachado - BSP-PMX-2020-007",
        cuerpo="Estimados, informamos que el equipo Bose Professional PowerMatch PM8500N serial BSP-PMX-2020-007 fue reparado exitosamente. Se reemplazó el módulo de amplificación del canal derecho. El equipo fue despachado hoy vía Servientrega, guía #SRV-20240503-8821, con entrega estimada en 2 días hábiles.",
        remitente="garantias@bosepro.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # 4 — Cliente pregunta por estado de su equipo (consulta_cliente)
    CorreoEntrante(
        uid="fake-004",
        asunto="¿Cuándo estará listo el equipo de recepción?",
        cuerpo="Buenos días, soy Juan Pérez del área de infraestructura de Constructora Andina. Quisiera saber en qué estado se encuentra la garantía del equipo LG 55SM5KE serial LG-MRI-2022-021 que está en la recepción principal. Llevamos más de dos semanas sin el equipo y está afectando la operación. Quedo pendiente.",
        remitente="jperez@constructoraandina.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # 5 — Proveedor actualiza diagnóstico con novedad técnica (actualizacion_proveedor)
    CorreoEntrante(
        uid="fake-005",
        asunto="Actualización diagnóstico - CRE-TSW-2023-003",
        cuerpo="Estimados Datecsa, con relación al equipo Crestron TSW-770 serial CRE-TSW-2023-003, informamos que el problema de la pantalla táctil está relacionado con un firmware defectuoso del lote de producción 2023-Q2. Crestron emitió una actualización correctiva. Aplicaremos el parche mañana y les confirmamos el resultado.",
        remitente="soporte@crestron-lac.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # 6 — Proveedor solicita información adicional para procesar garantía
    CorreoEntrante(
        uid="fake-006",
        asunto="Solicitud información adicional - garantía Kyocera KYO-TASKalfa-2021-001",
        cuerpo="Estimados, para continuar con el proceso de garantía del equipo Kyocera TASKalfa serial KYO-TASKalfa-2021-001 necesitamos la factura de compra original y el acta de entrega firmada. Por favor envíen estos documentos a la brevedad para no detener el proceso.",
        remitente="garantias@kyocera.com.co",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # 7 — Técnico interno reporta nueva falla por correo (sin PDF adjunto)
    CorreoEntrante(
        uid="fake-007",
        asunto="Nueva falla equipo sala ejecutiva - Crestron CRE-TSW-2023-003",
        cuerpo="Buenas tardes, les informo que el equipo Crestron TSW-770 serial CRE-TSW-2023-003 de la sala ejecutiva B volvió a presentar falla. Después de la actualización de firmware quedó sin respuesta completamente, ni siquiera enciende. Se requiere revisión urgente para mañana pues hay reunión de junta directiva.",
        remitente="soporte.interno@datecsafake.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # 8 — Correo sin relación con garantías (debe ser ignorado)
    CorreoEntrante(
        uid="fake-008",
        asunto="Invitación lanzamiento Kyocera TASKalfa Pro 2026",
        cuerpo="Estimados partners, los invitamos al lanzamiento del nuevo portafolio Kyocera para 2026. El evento se realizará el 15 de mayo en el Hotel Marriott de Bogotá. Confirmar asistencia antes del 10 de mayo.",
        remitente="eventos@kyocera.com.co",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # 9 — Cliente confirma recepción del equipo devuelto (cierre de solicitud)
    CorreoEntrante(
        uid="fake-009",
        asunto="RE: Devolución equipo - Confirmamos recepción Barco BAR-CS-2022-014",
        cuerpo="Buenas tardes, confirmamos que recibimos el equipo Barco ClickShare serial BAR-CS-2022-014 en perfectas condiciones. Ya fue instalado nuevamente en la sala de juntas y está funcionando correctamente. Muchas gracias por el seguimiento.",
        remitente="ti@grupobancolombia.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # 10 — Proveedor solicita autorización para reparación fuera de garantía
    CorreoEntrante(
        uid="fake-010",
        asunto="Diagnóstico fuera de garantía - BSP-PMX-2020-007",
        cuerpo="Estimados Datecsa, luego del diagnóstico del equipo Bose Professional PM8500N serial BSP-PMX-2020-007, determinamos que la falla es causada por un daño por humedad no cubierto por garantía. El costo de reparación es de USD 340. Requerimos su autorización para proceder. Quedo en espera.",
        remitente="garantias@bosepro.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
]


class FakeEmailAdapter(EmailPort):
    def __init__(self):
        self.sent: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})


class FakeEmailReaderAdapter(EmailReaderPort):
    def __init__(self, correos: list[CorreoEntrante] | None = None):
        self._inbox = list(correos if correos is not None else _FAKE_INBOX)
        self._read: set[str] = set()

    def fetch_unread(self) -> list[CorreoEntrante]:
        return [c for c in self._inbox if c.uid not in self._read]

    def mark_as_read(self, uid: str) -> None:
        self._read.add(uid)
