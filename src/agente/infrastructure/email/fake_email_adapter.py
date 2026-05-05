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
    """Genera correos fake relevantes para el estado actual de cada solicitud.
    Si la DB está vacía devuelve el inbox estático para que la demo siempre tenga datos."""
    if not solicitudes:
        return list(_FAKE_INBOX)

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
    # 5 actas de entrega — una por serial registrado (funcionan con DB vacía)
    CorreoEntrante(
        uid="fake-001",
        asunto="Acta entrega — Kyocera TASKalfa KYO-TASKalfa-2021-001",
        cuerpo=(
            "Señores Datecsa, adjunto acta de entrega del equipo Kyocera TASKalfa "
            "serial KYO-TASKalfa-2021-001 ubicado en el Área Administrativa piso 3. "
            "Falla reportada: Error fusor C3100, falla en calentamiento al inicio del día. "
            "Técnico responsable: Carlos Mendoza. Fecha de entrega: hoy."
        ),
        remitente="tecnico@datecsafake.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-002",
        asunto="Acta entrega — Barco ClickShare BAR-CS-2022-014",
        cuerpo=(
            "Cordial saludo, adjunto acta de entrega del equipo Barco ClickShare CX-50 "
            "serial BAR-CS-2022-014 de la Sala de Juntas Principal. "
            "Falla reportada: pantalla táctil sin respuesta, botón de encendido intermitente. "
            "Técnico: Alejandro Torres."
        ),
        remitente="tecnico@datecsafake.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-003",
        asunto="Acta entrega — Bose PowerMatch BSP-PMX-2020-007",
        cuerpo=(
            "Buenas tardes, se adjunta acta de entrega del equipo Bose Professional PowerMatch PM8500N "
            "serial BSP-PMX-2020-007 del Auditorio. "
            "Falla: distorsión de audio en canal derecho, ruido en frecuencias bajas durante reproducción. "
            "Técnico responsable: María González."
        ),
        remitente="tecnico@datecsafake.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-004",
        asunto="Acta entrega — Crestron TSW-770 CRE-TSW-2023-003",
        cuerpo=(
            "Estimados, adjunto acta de entrega del equipo Crestron TSW-770 "
            "serial CRE-TSW-2023-003 de la Sala Ejecutiva B. "
            "Falla: pantalla táctil no responde después de actualización de firmware aplicada el martes. "
            "Técnico responsable: Luis Herrera."
        ),
        remitente="tecnico@datecsafake.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-005",
        asunto="Acta entrega — LG Business 55SM5KE LG-MRI-2022-021",
        cuerpo=(
            "Señores Datecsa, adjunto acta de entrega del equipo LG Business 55SM5KE "
            "serial LG-MRI-2022-021 de la Recepción Principal. "
            "Falla: imagen con franjas verticales en la zona inferior de la pantalla, visible desde el encendido. "
            "Técnico: Sandra Ríos."
        ),
        remitente="tecnico@datecsafake.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    # Correos adicionales variados
    CorreoEntrante(
        uid="fake-006",
        asunto="Invitación lanzamiento Kyocera TASKalfa Pro 2026",
        cuerpo=(
            "Estimados partners, los invitamos al lanzamiento del nuevo portafolio Kyocera para 2026. "
            "El evento se realizará el 15 de mayo en el Hotel Marriott de Bogotá. "
            "Confirmar asistencia antes del 10 de mayo."
        ),
        remitente="eventos@kyocera.com.co",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-007",
        asunto="Kyocera Partner Summit 2026 — Registro abierto",
        cuerpo=(
            "Estimados distribuidores, les informamos que el registro para el Partner Summit 2026 "
            "ya está disponible en el portal de partners. Cupos limitados."
        ),
        remitente="eventos@kyocera.com.co",
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
