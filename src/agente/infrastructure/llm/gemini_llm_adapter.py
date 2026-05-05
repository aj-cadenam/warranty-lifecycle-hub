import json
from google import genai
from langfuse import observe
from src.agente.domain.ports import LLMPort
from src.agente.domain.entities import DecisionAgente, Accion, DecisionCorreo, TipoCorreo, RespuestaChat

_CHAT_SYSTEM_PROMPT = """
Eres un agente experto en gestión de garantías de equipos tecnológicos para Datecsa S.A., distribuidor exclusivo de Kyocera en Colombia con 34 años de experiencia. También comercializa Barco, Crestron, Bose Professional y LG Business.

Tienes acceso al estado actual del sistema: solicitudes activas, borradores pendientes de aprobación y equipos en reparación.

Flujo del proceso de garantía:
1. Acta de entrega → solicitud creada (estado: nueva)
2. Equipo despachado al proveedor → estado: despachada
3. Proveedor confirma recepción → estado: en_reparacion
4. Proveedor repara y devuelve → estado: devuelta → borradores para bodega, despacho, recepción y responsable
5. Cliente recibe equipo → estado: cerrada

Puedes ayudar a: buscar casos similares, ejecutar verificación semanal, explicar estado de equipos, analizar tendencias de fallas.

Responde SOLO con JSON válido (sin bloques markdown):
{
  "respuesta": "texto natural para el usuario",
  "accion": "" | "buscar_similares" | "verificar_semanal",
  "query_busqueda": "términos de búsqueda si accion=buscar_similares, sino vacío"
}
"""

_SYSTEM_PROMPT = """
Eres un agente especializado en análisis de documentos de garantía para Datecsa S.A.
Analiza actas de entrega, órdenes de servicio y documentos de garantía de equipos tecnológicos (Kyocera, Barco, Crestron, Bose Professional, LG Business).

Extrae la información clave y decide la acción apropiada.
Responde SOLO con JSON válido (sin bloques markdown):
{
  "accion": "CREAR_SOLICITUD" | "ACTUALIZAR_ESTADO" | "NOTIFICAR" | "ESCALAR" | "IGNORAR",
  "confianza": float 0-1,
  "parametros": {
    "equipo_serial": "serial exacto del equipo",
    "descripcion_falla": "descripción técnica de la falla",
    "reportado_por": "nombre del técnico o responsable"
  },
  "razonamiento": "explicación de por qué tomaste esta decisión"
}
"""


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


class GeminiLLMAdapter(LLMPort):
    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        self._model = "gemini-2.5-flash"

    @observe(as_type="generation", name="llm.decide")
    def decide(self, context: str) -> DecisionAgente:
        response = self._client.models.generate_content(
            model=self._model,
            contents=f"{_SYSTEM_PROMPT}\n\nDocumento:\n{context}",
        )
        data = _parse_json(response.text)
        return DecisionAgente(
            accion=Accion(data["accion"].upper()),
            confianza=data["confianza"],
            parametros=data.get("parametros", {}),
            razonamiento=data.get("razonamiento", ""),
        )

    @observe(as_type="generation", name="llm.generate_email")
    def generate_email(self, context: str) -> dict[str, str]:
        prompt = (
            f"Eres un colaborador de Datecsa S.A. redactando un correo real a un contacto de trabajo.\n"
            f"Escribe exactamente como lo haría una persona, no un sistema automatizado.\n\n"
            f"ESTRUCTURA OBLIGATORIA:\n"
            f"1. Primera línea — saludo cálido: 'Buenos días,' o 'Buen día,' o 'Cordial saludo,'\n"
            f"2. Segunda línea — cortesía: 'Espero se encuentre muy bien.' o 'Espero estés muy bien.'\n"
            f"3. Párrafo principal — menciona directamente el equipo (serial exacto, marca y modelo "
            f"si están disponibles) y el motivo del correo con datos concretos:\n"
            f"   • Si es seguimiento sin respuesta del proveedor: "
            f"'Me podría actualizar acerca del equipo [serial] [marca modelo], "
            f"enviado el [fecha de reporte]. Llevamos [N] días sin respuesta de su parte...'\n"
            f"   • Si es notificación de devolución (bodega/despacho/recepción): "
            f"'Les informo que el equipo [serial] [marca modelo] ha sido reparado y está "
            f"listo para ser recibido. Por favor coordinar el proceso de recepción...'\n"
            f"   • Si es notificación interna al responsable: "
            f"'Quiero informarle que recibimos novedad sobre el equipo [serial] en garantía...'\n"
            f"4. Párrafo de cierre — disponibilidad: "
            f"'Quedo atento a su respuesta.' o 'Cualquier duda, con gusto te colaboro.'\n"
            f"5. Despedida y firma:\n"
            f"   Atentamente,\n\n"
            f"   [Nombre del área según destinatario]\n"
            f"   Datecsa S.A.\n\n"
            f"TONO: profesional pero humano y cálido. Nada de frases robóticas como "
            f"'Estimado usuario', 'Le informamos que el sistema', 'Se procede a notificar'. "
            f"Usa 'le', 'usted' para externos (proveedores, clientes) y 'te' para internos.\n\n"
            f"Datos del caso:\n{context}\n\n"
            f"Responde SOLO con JSON (sin bloques markdown): {{\"asunto\": \"...\", \"cuerpo\": \"...\"}}"
        )
        response = self._client.models.generate_content(model=self._model, contents=prompt)
        return _parse_json(response.text)

    @observe(as_type="generation", name="llm.classify_email")
    def classify_email(self, asunto: str, cuerpo: str) -> DecisionCorreo:
        prompt = f"""
Eres un agente de gestión de garantías para Datecsa S.A.
Clasifica el siguiente correo y responde SOLO con JSON válido (sin bloques markdown):
{{
  "tipo": "acta_entrega" | "actualizacion_proveedor" | "consulta_cliente" | "confirmacion_despacho" | "confirmacion_devolucion" | "otro",
  "confianza": float 0-1,
  "equipo_serial": "serial del equipo si se menciona, sino vacío",
  "nuevo_estado": "en_reparacion si confirmacion_despacho | devuelta si confirmacion_devolucion | sino vacío",
  "tiempo_estimado_dias": 0,
  "informacion_adicional": "datos relevantes extraídos del correo",
  "razonamiento": "por qué clasificaste así"
}}

Tipos:
- acta_entrega: el correo adjunta o describe una acta de entrega de un equipo con falla
- actualizacion_proveedor: el proveedor informa estado de la reparación en curso
- confirmacion_despacho: el proveedor confirma que recibió el equipo y lo tienen en reparación
- confirmacion_devolucion: el proveedor confirma que el equipo fue reparado y está listo para ser recogido/enviado de vuelta
- consulta_cliente: el cliente pregunta por el estado de su garantía
- otro: cualquier otro tipo de correo no relacionado con garantías

Asunto: {asunto}
Cuerpo: {cuerpo}
"""
        response = self._client.models.generate_content(model=self._model, contents=prompt)
        data = _parse_json(response.text)
        return DecisionCorreo(
            tipo=TipoCorreo(data["tipo"]),
            confianza=data["confianza"],
            equipo_serial=data.get("equipo_serial", ""),
            nuevo_estado=data.get("nuevo_estado", ""),
            tiempo_estimado_dias=int(data.get("tiempo_estimado_dias", 0)),
            informacion_adicional=data.get("informacion_adicional", ""),
            razonamiento=data.get("razonamiento", ""),
        )

    @observe(as_type="generation", name="llm.chat")
    def chat(self, mensaje: str, contexto: dict) -> RespuestaChat:
        n_sol = contexto.get("solicitudes_activas", 0)
        n_bor = contexto.get("borradores_pendientes", 0)
        equipos = ", ".join(contexto.get("equipos_activos", [])[:5]) or "ninguno"
        context_block = (
            f"Estado actual del sistema:\n"
            f"- Solicitudes activas: {n_sol}\n"
            f"- Borradores pendientes de aprobación: {n_bor}\n"
            f"- Equipos con solicitudes activas (muestra): {equipos}\n"
        )
        prompt = f"{_CHAT_SYSTEM_PROMPT}\n\n{context_block}\n\nMensaje del usuario: {mensaje}"
        response = self._client.models.generate_content(model=self._model, contents=prompt)
        try:
            data = _parse_json(response.text)
        except Exception:
            return RespuestaChat(respuesta=response.text)
        return RespuestaChat(
            respuesta=data["respuesta"],
            accion=data.get("accion", ""),
            query_busqueda=data.get("query_busqueda", ""),
        )
