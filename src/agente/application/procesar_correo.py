from typing import Optional, Tuple
from langfuse import observe
from src.agente.domain.entities import CorreoEntrante, DecisionCorreo, TipoCorreo
from src.agente.domain.ports import LLMPort, EmailReaderPort, OCRPort, EmbeddingPort, VectorStorePort
from src.agente.application.procesar_documento import ProcesarDocumento
from src.solicitudes.application.actualizar_estado import ActualizarEstado
from src.solicitudes.domain.entities import EstadoSolicitud, SolicitudGarantia
from src.solicitudes.domain.ports import SolicitudRepository
from src.trazabilidad.domain.entities import EventoTrazabilidad, MetodoRegistro
from src.trazabilidad.domain.ports import TrazabilidadRepository
from src.solicitudes.application.crear_solicitud import CrearSolicitud

_ESTADO_MAP: dict[str, EstadoSolicitud] = {
    "validada": EstadoSolicitud.VALIDADA,
    "despachada": EstadoSolicitud.DESPACHADA,
    "en_reparacion": EstadoSolicitud.EN_REPARACION,
    "devuelta": EstadoSolicitud.DEVUELTA,
    "cerrada": EstadoSolicitud.CERRADA,
}


class ProcesarCorreo:
    def __init__(
        self,
        llm: LLMPort,
        email_reader: EmailReaderPort,
        ocr: OCRPort,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
        solicitud_repo: SolicitudRepository,
        trazabilidad_repo: TrazabilidadRepository,
        crear_solicitud: CrearSolicitud,
        orquestar=None,  # OrquestarAcciones | None — optional to keep backwards compat
    ):
        self._llm = llm
        self._email_reader = email_reader
        self._ocr = ocr
        self._embedding = embedding
        self._vector_store = vector_store
        self._solicitud_repo = solicitud_repo
        self._trazabilidad_repo = trazabilidad_repo
        self._crear_solicitud = crear_solicitud
        self._orquestar = orquestar

    @observe(name="procesar_correos")
    def execute(self) -> dict:
        correos = self._email_reader.fetch_unread()
        resultados = []
        for correo in correos:
            resultado = self._procesar(correo)
            self._email_reader.mark_as_read(correo.uid)
            resultados.append(resultado)
        return {"procesados": len(resultados), "detalle": resultados}

    def _procesar(self, correo: CorreoEntrante) -> dict:
        decision = self._llm.classify_email(correo.asunto, correo.cuerpo)
        resultado: dict = {
            "uid": correo.uid,
            "asunto": correo.asunto,
            "remitente": correo.remitente,
            "tipo": decision.tipo.value,
            "confianza": decision.confianza,
            "equipo_serial": decision.equipo_serial,
            "accion_tomada": None,
            "borradores_generados": 0,
            "destinatarios": [],
        }

        solicitud: Optional[SolicitudGarantia] = None

        if decision.tipo == TipoCorreo.ACTA_ENTREGA:
            accion, solicitud = self._manejar_acta(correo, decision)
            resultado["accion_tomada"] = accion

        elif decision.tipo in (
            TipoCorreo.ACTUALIZACION_PROVEEDOR,
            TipoCorreo.CONFIRMACION_DESPACHO,
            TipoCorreo.CONFIRMACION_DEVOLUCION,
        ):
            accion, solicitud = self._manejar_actualizacion(correo, decision)
            resultado["accion_tomada"] = accion

        elif decision.tipo == TipoCorreo.CONSULTA_CLIENTE:
            resultado["accion_tomada"] = "consulta_registrada"
            if decision.equipo_serial:
                todas = (
                    self._solicitud_repo.find_by_estado(EstadoSolicitud.NUEVA)
                    + self._solicitud_repo.find_by_estado(EstadoSolicitud.VALIDADA)
                    + self._solicitud_repo.find_by_estado(EstadoSolicitud.DESPACHADA)
                    + self._solicitud_repo.find_by_estado(EstadoSolicitud.EN_REPARACION)
                )
                solicitud = next((s for s in todas if s.equipo_id == decision.equipo_serial), None)

        else:
            resultado["accion_tomada"] = "ignorado"

        if self._orquestar and solicitud:
            borradores = self._orquestar.execute(solicitud=solicitud, decision=decision)
            resultado["borradores_generados"] = len(borradores)
            resultado["destinatarios"] = [b.destinatario_tipo.value for b in borradores]

        return resultado

    def _manejar_acta(
        self, correo: CorreoEntrante, decision: DecisionCorreo
    ) -> Tuple[str, Optional[SolicitudGarantia]]:
        for pdf_path in correo.adjuntos:
            procesador = ProcesarDocumento(
                ocr=self._ocr,
                llm=self._llm,
                embedding=self._embedding,
                vector_store=self._vector_store,
                crear_solicitud=self._crear_solicitud,
            )
            _, solicitud = procesador.execute(pdf_path=pdf_path)
            return "solicitud_creada_desde_pdf", solicitud

        if decision.equipo_serial:
            try:
                solicitud = self._crear_solicitud.execute(
                    equipo_id=decision.equipo_serial,
                    reportado_por=correo.remitente,
                    descripcion_falla=correo.cuerpo[:500],
                )
                return "solicitud_creada_desde_correo", solicitud
            except ValueError:
                return "equipo_sin_garantia_vigente", None
        return "sin_serial_identificado", None

    def _manejar_actualizacion(
        self, correo: CorreoEntrante, decision: DecisionCorreo
    ) -> Tuple[str, Optional[SolicitudGarantia]]:
        if not decision.equipo_serial:
            return "sin_serial_identificado", None

        solicitudes = (
            self._solicitud_repo.find_by_estado(EstadoSolicitud.DESPACHADA)
            + self._solicitud_repo.find_by_estado(EstadoSolicitud.EN_REPARACION)
        )
        solicitud = next((s for s in solicitudes if s.equipo_id == decision.equipo_serial), None)

        if not solicitud:
            return "solicitud_activa_no_encontrada", None

        nuevo_estado = _ESTADO_MAP.get(decision.nuevo_estado)
        if nuevo_estado:
            ActualizarEstado(self._solicitud_repo).execute(solicitud.id, nuevo_estado)

        evento = EventoTrazabilidad(
            equipo_id=decision.equipo_serial,
            solicitud_id=solicitud.id,
            ubicacion_anterior=solicitud.estado.value,
            ubicacion_nueva=decision.nuevo_estado or "actualizado_por_proveedor",
            responsable=correo.remitente,
            metodo_registro=MetodoRegistro.AGENTE_EMAIL,
            notas=decision.informacion_adicional,
            tiempo_estimado_dias=decision.tiempo_estimado_dias,
        )
        self._trazabilidad_repo.save(evento)
        return "estado_actualizado", solicitud
