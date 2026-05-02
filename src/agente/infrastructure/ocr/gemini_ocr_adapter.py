from google import genai
from google.genai import types
from langfuse import observe
from src.agente.domain.ports import OCRPort


class GeminiOCRAdapter(OCRPort):
    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        self._model = "gemini-2.5-flash"

    @observe(name="ocr.extract_text")
    def extract_text(self, pdf_path: str) -> str:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        response = self._client.models.generate_content(
            model=self._model,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                "Extrae todo el texto de este documento. Responde solo con el texto extraído, sin explicaciones.",
            ],
        )
        return response.text
