from datetime import datetime
from src.solicitudes.domain.ports import SolicitudRepository
from src.solicitudes.domain.entities import EstadoSolicitud
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.seguimiento.domain.ports import BorradorCorreoRepository, EventoSeguimientoRepository
from src.seguimiento.domain.entities import (
    BorradorCorreo, EventoSeguimiento, DestinatarioTipo, EstadoBorrador
)
from src.agente.domain.ports import LLMPort


class VerificarEstadoSemanal:
    def __init__(
        self,
        solicitud_repo: SolicitudRepository,
        trazabilidad_repo: TrazabilidadRepository,
        borrador_repo: BorradorCorreoRepository,
        seguimiento_repo: EventoSeguimientoRepository,
        llm: LLMPort,
        timeout_proveedor_dias: int = 7,
        proveedor_email: str = "",
    ):
        self._solicitudes = solicitud_repo
        self._trazabilidad = trazabilidad_repo
        self._borradores = borrador_repo
        self._seguimiento = seguimiento_repo
        self._llm = llm
        self._timeout = timeout_proveedor_dias
        self._proveedor_email = proveedor_email

    def execute(self) -> dict:
        estados_activos = [EstadoSolicitud.DESPACHADA, EstadoSolicitud.EN_REPARACION]
        solicitudes_verificadas = 0
        borradores_generados = 0
        for estado in estados_activos:
            for solicitud in self._solicitudes.find_by_estado(estado):
                if self._verificar_solicitud(solicitud):
                    borradores_generados += 1
                solicitudes_verificadas += 1
        return {"solicitudes_verificadas": solicitudes_verificadas, "borradores_generados": borradores_generados}

    def _verificar_solicitud(self, solicitud) -> bool:
        ultimo_evento = self._trazabilidad.find_ultimo_evento(solicitud.id)
        if not ultimo_evento:
            return False

        dias_sin_respuesta = (datetime.now() - ultimo_evento.timestamp).days

        evento = EventoSeguimiento(
            solicitud_id=solicitud.id,
            tipo_evento="verificacion_semanal",
            descripcion=f"Verificación semanal: {dias_sin_respuesta} días sin respuesta",
            dias_sin_respuesta=dias_sin_respuesta,
        )
        self._seguimiento.save(evento)

        if dias_sin_respuesta < self._timeout:
            return False

        borrador_existente = self._borradores.find_by_solicitud_y_estado(
            solicitud.id, EstadoBorrador.PENDIENTE_APROBACION
        )
        if borrador_existente:
            return False

        contexto = (
            f"Solicitud {solicitud.id} para equipo {solicitud.equipo_id}. "
            f"Falla: {solicitud.descripcion_falla}. "
            f"Días sin respuesta del proveedor: {dias_sin_respuesta}."
        )
        email_data = self._llm.generate_email(context=contexto)

        borrador = BorradorCorreo(
            solicitud_id=solicitud.id,
            destinatario_tipo=DestinatarioTipo.PROVEEDOR,
            destinatario_email=self._proveedor_email,
            asunto=email_data["asunto"],
            cuerpo=email_data["cuerpo"],
            dias_sin_respuesta=dias_sin_respuesta,
        )
        self._borradores.save(borrador)
        return True
