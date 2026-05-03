from datetime import datetime
from src.agente.domain.ports import EmailPort, EmailReaderPort
from src.agente.domain.entities import CorreoEntrante

_FAKE_INBOX: list[CorreoEntrante] = [
    CorreoEntrante(
        uid="fake-001",
        asunto="Acta de entrega - Kyocera TASKalfa KYO-TASKalfa-2021-001",
        cuerpo="Adjunto acta de entrega del equipo Kyocera TASKalfa serial KYO-TASKalfa-2021-001. Falla: Error fusor C3100.",
        remitente="tecnico@datecsa.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-002",
        asunto="RE: Solicitud garantía BAR-CS-2022-014 - Actualización",
        cuerpo="Estimados, confirmamos recepción del equipo Barco ClickShare serial BAR-CS-2022-014. Estimamos diagnóstico en 3 días hábiles.",
        remitente="soporte@barco.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-003",
        asunto="Consulta estado garantía",
        cuerpo="Buenos días, quisiera saber cuándo estará listo el equipo de la sala de juntas. Gracias.",
        remitente="cliente@empresa.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-004",
        asunto="Confirmación recepción equipo - Kyocera KYO-TASKalfa-2021-001",
        cuerpo="Estimados, confirmamos recepción del equipo Kyocera TASKalfa serial KYO-TASKalfa-2021-001. Estimamos diagnóstico en 3 días hábiles.",
        remitente="soporte@kyocera.com",
        adjuntos=[],
        fecha=datetime.now(),
    ),
    CorreoEntrante(
        uid="fake-005",
        asunto="Equipo reparado listo para retiro - Barco BAR-CS-2022-014",
        cuerpo="Estimados, el equipo Barco ClickShare serial BAR-CS-2022-014 ha sido reparado y está listo para retiro o devolución.",
        remitente="soporte@barco.com",
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
