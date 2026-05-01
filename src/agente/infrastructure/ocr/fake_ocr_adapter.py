from src.agente.domain.ports import OCRPort

FAKE_OCR_TEXT = """ACTA DE ENTREGA — DATECSA S.A.
Fecha: 2026-04-30
Equipo: Kyocera TASKalfa 2553ci
Serial: KYO-TASKalfa-2021-001
Falla reportada: Error de fusor C3100. El equipo presenta falla en el módulo de fusión.
Técnico responsable: Carlos Ramírez
Ubicación: Piso 3 - Área Administrativa"""


class FakeOCRAdapter(OCRPort):
    def __init__(self, texto_fijo: str = FAKE_OCR_TEXT):
        self._texto = texto_fijo

    def extract_text(self, pdf_path: str) -> str:
        return self._texto
