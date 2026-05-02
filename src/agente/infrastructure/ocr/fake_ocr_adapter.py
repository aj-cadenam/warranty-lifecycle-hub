from src.agente.domain.ports import OCRPort

FAKE_OCR_TEXT = """ACTA DE ENTREGA — DATECSA S.A.
Fecha: 2026-04-30
Equipo: Kyocera TASKalfa 2553ci
Serial: KYO-TASKalfa-2021-001
Falla reportada: Error de fusor C3100. El equipo presenta falla en el módulo de fusión.
Técnico responsable: Carlos Ramírez
Ubicación: Piso 3 - Área Administrativa"""

_TEXTS: dict[str, str] = {
    "kyocera": FAKE_OCR_TEXT,
    "kyo": FAKE_OCR_TEXT,
    "bar": """ACTA DE ENTREGA — DATECSA S.A.
Fecha: 2026-04-30
Equipo: Barco ClickShare CX-50
Serial: BAR-CS-2022-014
Falla reportada: Botón ClickShare no establece conexión con pantalla principal. WiFi conectado pero sin transmisión de video.
Técnico responsable: Ana Gómez
Ubicación: Sala de Juntas Principal""",
    "bsp": """ACTA DE ENTREGA — DATECSA S.A.
Fecha: 2026-04-30
Equipo: Bose Professional PowerMatch PM8500N
Serial: BSP-PMX-2020-007
Falla reportada: Canales 3 y 4 del amplificador sin señal de salida. Detectado durante evento corporativo.
Técnico responsable: Luis Torres
Ubicación: Auditorio""",
    "cre": """ACTA DE ENTREGA — DATECSA S.A.
Fecha: 2026-04-30
Equipo: Crestron TSW-770
Serial: CRE-TSW-2023-003
Falla reportada: Panel táctil no responde al tacto. Pantalla encendida pero sin interacción posible.
Técnico responsable: María López
Ubicación: Sala Ejecutiva B""",
    "lg": """ACTA DE ENTREGA — DATECSA S.A.
Fecha: 2026-04-30
Equipo: LG Business 55SM5KE
Serial: LG-MRI-2022-021
Falla reportada: Pantalla de señalización digital muestra artefactos visuales y parpadeo. Afecta recepción.
Técnico responsable: Jorge Herrera
Ubicación: Recepción Principal""",
}


class FakeOCRAdapter(OCRPort):
    def __init__(self, texto_fijo: str | None = None):
        self._texto_fijo = texto_fijo

    def extract_text(self, pdf_path: str) -> str:
        if self._texto_fijo is not None:
            return self._texto_fijo
        path_lower = pdf_path.lower()
        for key, text in _TEXTS.items():
            if key in path_lower:
                return text
        return FAKE_OCR_TEXT
