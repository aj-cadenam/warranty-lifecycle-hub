from src.agente.domain.ports import LLMPort
from src.agente.domain.entities import DecisionAgente, Accion


class FakeLLMAdapter(LLMPort):
    def decide(self, context: str) -> DecisionAgente:
        return DecisionAgente(accion=Accion.CREAR_SOLICITUD, confianza=0.99,
                              parametros={"equipo_serial": "KYO-001", "descripcion_falla": "Falla simulada",
                                          "reportado_por": "Agente Fake"},
                              razonamiento="[FAKE] respuesta simulada")

    def generate_email(self, context: str) -> dict[str, str]:
        return {"asunto": "[FAKE] Seguimiento garantía",
                "cuerpo": "Estimados, solicitamos amablemente una actualización. Cordialmente, Datecsa S.A."}
