from dataclasses import dataclass
from src.agente.domain.entities import TipoCorreo, DecisionCorreo
from src.agente.domain.ports import LLMPort
from src.seguimiento.domain.entities import BorradorCorreo, DestinatarioTipo
from src.seguimiento.domain.ports import BorradorCorreoRepository
from src.solicitudes.domain.entities import SolicitudGarantia


@dataclass
class _Destino:
    tipo: DestinatarioTipo
    email: str
    rol_label: str


class OrquestarAcciones:
    def __init__(
        self,
        llm: LLMPort,
        borrador_repo: BorradorCorreoRepository,
        responsable_email: str = "",
        bodega_email: str = "",
        despacho_email: str = "",
        recepcion_email: str = "",
    ):
        self._llm = llm
        self._repo = borrador_repo
        self._responsable = responsable_email
        self._bodega = bodega_email
        self._despacho = despacho_email
        self._recepcion = recepcion_email

    def execute(
        self,
        solicitud: SolicitudGarantia,
        decision: DecisionCorreo,
    ) -> list[BorradorCorreo]:
        destinos = self._resolver_destinos(decision.tipo)
        borradores: list[BorradorCorreo] = []
        for dest in destinos:
            contexto = (
                f"Solicitud {solicitud.id}, equipo {solicitud.equipo_id}. "
                f"Falla: {solicitud.descripcion_falla}. "
                f"Evento recibido: {decision.tipo.value}. "
                f"Información adicional: {decision.informacion_adicional}. "
                f"Destinatario: {dest.rol_label}."
            )
            email_data = self._llm.generate_email(contexto)
            borrador = BorradorCorreo(
                solicitud_id=solicitud.id,
                destinatario_tipo=dest.tipo,
                destinatario_email=dest.email,
                asunto=email_data["asunto"],
                cuerpo=email_data["cuerpo"],
            )
            self._repo.save(borrador)
            borradores.append(borrador)
        return borradores

    def _resolver_destinos(self, tipo: TipoCorreo) -> list[_Destino]:
        destinos: list[_Destino] = []

        def add(tipo_dest: DestinatarioTipo, email: str, label: str) -> None:
            if email:
                destinos.append(_Destino(tipo=tipo_dest, email=email, rol_label=label))

        if tipo == TipoCorreo.ACTA_ENTREGA:
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        elif tipo == TipoCorreo.ACTUALIZACION_PROVEEDOR:
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        elif tipo == TipoCorreo.CONFIRMACION_DESPACHO:
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        elif tipo == TipoCorreo.CONFIRMACION_DEVOLUCION:
            add(DestinatarioTipo.BODEGA, self._bodega, "Bodega")
            add(DestinatarioTipo.DESPACHO, self._despacho, "Despacho")
            add(DestinatarioTipo.RECEPCION, self._recepcion, "Recepción")
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        elif tipo == TipoCorreo.CONSULTA_CLIENTE:
            add(DestinatarioTipo.RESPONSABLE, self._responsable, "Responsable de garantías")

        return destinos
