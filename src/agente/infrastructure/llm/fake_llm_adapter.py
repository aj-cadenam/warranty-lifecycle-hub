import re
from src.agente.domain.ports import LLMPort
from src.agente.domain.entities import DecisionAgente, Accion, DecisionCorreo, TipoCorreo, RespuestaChat

_DEFAULT_SERIAL = "KYO-TASKalfa-2021-001"


class FakeLLMAdapter(LLMPort):
    def decide(self, context: str) -> DecisionAgente:
        match = re.search(r"Serial:\s*([A-Za-z0-9\-]+)", context)
        serial = match.group(1) if match else _DEFAULT_SERIAL
        return DecisionAgente(
            accion=Accion.CREAR_SOLICITUD,
            confianza=0.99,
            parametros={
                "equipo_serial": serial,
                "reportado_por": "Agente Fake",
            },
            razonamiento="[FAKE] respuesta simulada",
        )

    def generate_email(self, context: str) -> dict[str, str]:
        import re
        serial_match = re.search(r"Serial del equipo:\s*([^\.\,]+)", context)
        serial = serial_match.group(1).strip() if serial_match else "equipo en garantía"
        dias_match = re.search(r"Días sin respuesta:\s*(\d+)", context)
        dias = dias_match.group(1) if dias_match else None
        fecha_match = re.search(r"Fecha de (?:reporte|envío al proveedor):\s*([^\.\,]+)", context)
        fecha = fecha_match.group(1).strip() if fecha_match else None

        if dias:
            asunto = f"[FAKE] Seguimiento garantía — {serial}"
            cuerpo = (
                f"Buenos días,\n\n"
                f"Espero se encuentre muy bien.\n\n"
                f"Me podría actualizar acerca del equipo {serial}"
                f"{f', enviado el {fecha}' if fecha else ''}. "
                f"Llevamos {dias} días sin respuesta de su parte y queremos asegurarnos "
                f"de que todo esté en orden con el proceso de reparación.\n\n"
                f"Agradezco mucho su atención y quedo atento a su respuesta.\n\n"
                f"Atentamente,\n\n"
                f"Equipo de Servicio Técnico\nDatacsa S.A."
            )
        else:
            asunto = f"[FAKE] Notificación garantía — {serial}"
            cuerpo = (
                f"Buenos días,\n\n"
                f"Espero se encuentre muy bien.\n\n"
                f"Quiero informarle sobre una novedad relacionada con el equipo {serial}. "
                f"Por favor revisar el caso y coordinar las acciones correspondientes.\n\n"
                f"Cualquier duda, con gusto le colaboro.\n\n"
                f"Atentamente,\n\n"
                f"Equipo de Servicio Técnico\nDatacsa S.A."
            )
        return {"asunto": asunto, "cuerpo": cuerpo}

    def classify_email(self, asunto: str, cuerpo: str) -> DecisionCorreo:
        texto = (asunto + " " + cuerpo).lower()
        match = re.search(r"([A-Z]{2,4}-[A-Za-z]+-\d{4}-\d{3})", asunto + " " + cuerpo)
        serial = match.group(1) if match else ""

        if any(w in texto for w in ["acta", "entrega", "falla", "adjunto"]):
            return DecisionCorreo(tipo=TipoCorreo.ACTA_ENTREGA, confianza=0.95,
                                  equipo_serial=serial, razonamiento="[FAKE] contiene palabras clave de acta")
        if any(w in texto for w in ["recibimos", "diagnóstico", "estimamos", "días hábiles", "reparación"]):
            return DecisionCorreo(tipo=TipoCorreo.ACTUALIZACION_PROVEEDOR, confianza=0.95,
                                  equipo_serial=serial, razonamiento="[FAKE] actualización de proveedor")
        if any(w in texto for w in ["despachamos", "enviamos", "guía", "tracking"]):
            return DecisionCorreo(tipo=TipoCorreo.CONFIRMACION_DESPACHO, confianza=0.95,
                                  equipo_serial=serial, razonamiento="[FAKE] confirmación de despacho")
        if any(w in texto for w in ["listo para retiro", "reparado listo", "listo para recoger"]):
            return DecisionCorreo(tipo=TipoCorreo.CONFIRMACION_DEVOLUCION, confianza=0.95,
                                  equipo_serial=serial, razonamiento="[FAKE] confirmación de devolución")
        if any(w in texto for w in ["estado", "cuándo", "cuando", "consulta"]):
            return DecisionCorreo(tipo=TipoCorreo.CONSULTA_CLIENTE, confianza=0.90,
                                  equipo_serial=serial, razonamiento="[FAKE] consulta de cliente")
        return DecisionCorreo(tipo=TipoCorreo.OTRO, confianza=0.80,
                              razonamiento="[FAKE] no clasificado")

    def chat(self, mensaje: str, contexto: dict) -> RespuestaChat:
        n = contexto.get("solicitudes_activas", 0)
        return RespuestaChat(
            respuesta=f"[FAKE] Entendido. Actualmente gestionas {n} solicitudes activas.",
        )
