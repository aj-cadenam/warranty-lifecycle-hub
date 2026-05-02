import json
import google.generativeai as genai
from src.agente.domain.ports import LLMPort
from src.agente.domain.entities import DecisionAgente, Accion

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
    # Strip markdown fenced blocks if Gemini wraps the response
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


class GeminiLLMAdapter(LLMPort):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-1.5-flash")

    def decide(self, context: str) -> DecisionAgente:
        response = self._model.generate_content(f"{_SYSTEM_PROMPT}\n\nDocumento:\n{context}")
        data = _parse_json(response.text)
        return DecisionAgente(
            accion=Accion(data["accion"].upper()),
            confianza=data["confianza"],
            parametros=data.get("parametros", {}),
            razonamiento=data.get("razonamiento", ""),
        )

    def generate_email(self, context: str) -> dict[str, str]:
        prompt = (
            f"Genera un correo formal y amable en español para solicitar una actualización "
            f"de garantía. Contexto: {context}\n"
            f"Responde SOLO con JSON (sin bloques markdown): {{\"asunto\": \"...\", \"cuerpo\": \"...\"}}"
        )
        response = self._model.generate_content(prompt)
        return _parse_json(response.text)
