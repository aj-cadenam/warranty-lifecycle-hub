from datetime import datetime
from src.agente.domain.ports import EmailPort, EmailReaderPort
from src.agente.domain.entities import CorreoEntrante

_FAKE_INBOX: list[CorreoEntrante] = [
    # 1 — Acta de entrega de nuevo equipo (crea solicitud)
    CorreoEntrante(
        uid="fake-001",
        asunto="Acta de entrega - Kyocera TASKalfa KYO-TASKalfa-2021-001",
        cuerpo="Adjunto acta de entrega del equipo Kyocera TASKalfa serial KYO-TASKalfa-2021-001. Falla: Error fusor C3100 — falla en calentamiento al inicio del día.",
        remitente="tecnico@datecsa.com",
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
        remitente="soporte.interno@datecsa.com",
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
