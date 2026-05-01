from src.seguimiento.domain.ports import BorradorCorreoRepository
from src.agente.domain.ports import EmailPort


class AprobarBorrador:
    def __init__(self, borrador_repo: BorradorCorreoRepository, email_adapter: EmailPort):
        self._repo = borrador_repo
        self._email = email_adapter

    def execute(self, borrador_id: str, aprobado_por: str) -> None:
        borrador = self._repo.find_by_id(borrador_id)
        if borrador is None:
            raise ValueError(f"borrador {borrador_id} no encontrado")
        borrador.aprobar(aprobado_por=aprobado_por)
        self._email.send(to=borrador.destinatario_email, subject=borrador.asunto, body=borrador.cuerpo)
        borrador.marcar_enviado()
        self._repo.save(borrador)
