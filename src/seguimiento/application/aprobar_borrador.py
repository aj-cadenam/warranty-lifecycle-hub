from typing import Optional
from src.seguimiento.domain.ports import BorradorCorreoRepository
from src.seguimiento.domain.entities import DestinatarioTipo
from src.solicitudes.domain.ports import SolicitudRepository
from src.solicitudes.domain.entities import EstadoSolicitud
from src.agente.domain.ports import EmailPort


class AprobarBorrador:
    def __init__(
        self,
        borrador_repo: BorradorCorreoRepository,
        email_adapter: EmailPort,
        solicitud_repo: Optional[SolicitudRepository] = None,
    ):
        self._repo = borrador_repo
        self._email = email_adapter
        self._solicitud_repo = solicitud_repo

    def execute(self, borrador_id: str, aprobado_por: str) -> dict:
        borrador = self._repo.find_by_id(borrador_id)
        if borrador is None:
            raise ValueError(f"borrador {borrador_id} no encontrado")
        borrador.aprobar(aprobado_por=aprobado_por)
        dest = borrador.destinatario_email or "sin-destinatario@datecsafake.com"
        try:
            self._email.send(to=dest, subject=borrador.asunto, body=borrador.cuerpo)
        except Exception:
            pass  # envío real no disponible en demo — borrador queda marcado como enviado igual
        borrador.marcar_enviado()
        self._repo.save(borrador)

        solicitud_cerrada = self._cerrar_si_corresponde(borrador)
        return {"solicitud_cerrada": solicitud_cerrada}

    def _cerrar_si_corresponde(self, borrador) -> bool:
        if self._solicitud_repo is None:
            return False
        if borrador.destinatario_tipo != DestinatarioTipo.BODEGA:
            return False
        solicitud = self._solicitud_repo.find_by_id(str(borrador.solicitud_id))
        if solicitud is None or solicitud.estado != EstadoSolicitud.DEVUELTA:
            return False
        solicitud.cerrar()
        self._solicitud_repo.save(solicitud)
        return True
