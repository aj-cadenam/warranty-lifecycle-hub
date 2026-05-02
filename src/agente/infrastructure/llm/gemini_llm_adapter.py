import json
from google import genai
from langfuse import observe
from src.agente.domain.ports import LLMPort
from src.agente.domain.entities import DecisionAgente, Accion, DecisionCorreo, TipoCorreo, RespuestaChat

_CHAT_SYSTEM_PROMPT = """
Eres un asistente de gestión de garantías para Datecsa S.A.
Responde en español, de forma concisa y útil. Usa el contexto del sistema para dar respuestas precisas.

Si el usuario quiere buscar casos similares o fallas parecidas, detecta la query de búsqueda.
Si quiere ejecutar la verificación semanal de garantías, indícalo.

Responde SOLO con JSON válido (sin bloques markdown):
{
  "respuesta": "texto natural para el usuario",
  "accion": "" | "buscar_similares" | "verificar_semanal",
  "query_busqueda": "términos de búsqueda si accion=buscar_similares, sino vacío"
}
"""

_SYSTEM_PROMPT = """
Eres un agente de gestión de garantías de equipos para Datecsa S.A.
Analiza el texto del documento y responde SOLO con JSON válido (sin bloques markdown):
{
  "accion": "CREAR_SOLICITUD" | "ACTUALIZAR_ESTADO" | "NOTIFICAR" | "ESCALAR" | "IGNORAR",
  "confianza": float 0-1,
  "parametros": {
    "equipo_serial": "...",
    "descripcion_falla": "...",
    "reportado_por": "..."
  },
  "razonamiento": "..."
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
            f"Genera un correo formal y amable en español para solicitar una actualización "
            f"de garantía. Contexto: {context}\n"
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
  "tipo": "acta_entrega" | "actualizacion_proveedor" | "consulta_cliente" | "confirmacion_despacho" | "otro",
  "confianza": float 0-1,
  "equipo_serial": "serial del equipo si se menciona, sino vacío",
  "nuevo_estado": "estado sugerido para la solicitud si aplica, sino vacío",
  "tiempo_estimado_dias": 0,
  "informacion_adicional": "datos relevantes extraídos del correo",
  "razonamiento": "por qué clasificaste así"
}}

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
