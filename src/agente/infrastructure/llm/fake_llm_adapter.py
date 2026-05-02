import re
from src.agente.domain.ports import LLMPort
from src.agente.domain.entities import DecisionAgente, Accion

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
        return {"asunto": "[FAKE] Seguimiento garantía",
                "cuerpo": "Estimados, solicitamos amablemente una actualización. Cordialmente, Datecsa S.A."}
