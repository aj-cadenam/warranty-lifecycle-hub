from src.agente.domain.ports import LLMPort
from src.agente.domain.entities import DecisionAgente, Accion


class FakeLLMAdapter(LLMPort):
    def decide(self, context: str) -> DecisionAgente:
        return DecisionAgente(
            accion=Accion.CREAR_SOLICITUD,
            confianza=0.99,
            parametros={
                "equipo_serial": "KYO-TASKalfa-2021-001",
                "reportado_por": "Agente Fake",
            },
            razonamiento="[FAKE] respuesta simulada",
        )

    def generate_email(self, context: str) -> dict[str, str]:
        return {"asunto": "[FAKE] Seguimiento garantía",
                "cuerpo": "Estimados, solicitamos amablemente una actualización. Cordialmente, Datecsa S.A."}
