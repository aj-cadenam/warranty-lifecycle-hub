import base64
import google.generativeai as genai
from src.agente.domain.ports import OCRPort


class GeminiOCRAdapter(OCRPort):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-1.5-flash")

    def extract_text(self, pdf_path: str) -> str:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        pdf_b64 = base64.b64encode(pdf_bytes).decode()
        response = self._model.generate_content([
            {"mime_type": "application/pdf", "data": pdf_b64},
            "Extrae todo el texto de este documento. Responde solo con el texto extraído, sin explicaciones.",
        ])
        return response.text
