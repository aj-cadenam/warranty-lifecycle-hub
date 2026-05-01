from src.agente.domain.ports import OCRPort, LLMPort, EmbeddingPort
from src.agente.domain.entities import DecisionAgente
from src.agente.infrastructure.chunking import ChunkingService
from src.solicitudes.application.crear_solicitud import CrearSolicitud


class ProcesarDocumento:
    def __init__(
        self,
        ocr: OCRPort,
        llm: LLMPort,
        embedding: EmbeddingPort,
        crear_solicitud: CrearSolicitud,
        chunk_size: int = 800,
        overlap: int = 100,
    ):
        self._ocr = ocr
        self._llm = llm
        self._embedding = embedding
        self._crear_solicitud = crear_solicitud
        self._chunker = ChunkingService(chunk_size=chunk_size, overlap=overlap)

    def execute(self, pdf_path: str) -> DecisionAgente:
        texto = self._ocr.extract_text(pdf_path)
        chunks = self._chunker.chunk(texto, metadata={"pdf_path": pdf_path})
        for chunk in chunks:
            self._embedding.embed(chunk.text)

        decision = self._llm.decide(context=texto)

        if decision.accion.value == "crear_solicitud":
            params = decision.parametros
            self._crear_solicitud.execute(
                equipo_id=params.get("equipo_serial", ""),
                reportado_por=params.get("reportado_por", "Agente OCR"),
                descripcion_falla=params.get("descripcion_falla", texto[:500]),
            )

        return decision
