from typing import Optional, Tuple
from langfuse import observe
from src.agente.domain.ports import OCRPort, LLMPort, EmbeddingPort, VectorStorePort
from src.agente.domain.entities import DecisionAgente, Accion
from src.agente.infrastructure.chunking import ChunkingService
from src.solicitudes.application.crear_solicitud import CrearSolicitud
from src.solicitudes.domain.entities import SolicitudGarantia


class ProcesarDocumento:
    def __init__(
        self,
        ocr: OCRPort,
        llm: LLMPort,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
        crear_solicitud: CrearSolicitud,
        chunk_size: int = 800,
        overlap: int = 100,
    ):
        self._ocr = ocr
        self._llm = llm
        self._embedding = embedding
        self._vector_store = vector_store
        self._crear_solicitud = crear_solicitud
        self._chunker = ChunkingService(chunk_size=chunk_size, overlap=overlap)

    @observe(name="procesar_documento")
    def execute(self, pdf_path: str, extra_metadata: dict | None = None) -> Tuple[DecisionAgente, Optional[SolicitudGarantia]]:
        texto = self._ocr.extract_text(pdf_path)
        base_meta = {"pdf_path": pdf_path, **(extra_metadata or {})}
        chunks = self._chunker.chunk(texto, metadata=base_meta)
        embeddings = [self._embedding.embed(chunk.text) for chunk in chunks]

        decision = self._llm.decide(context=texto)
        solicitud_creada: Optional[SolicitudGarantia] = None

        if decision.accion == Accion.CREAR_SOLICITUD:
            params = decision.parametros
            try:
                solicitud_creada = self._crear_solicitud.execute(
                    equipo_id=params.get("equipo_serial", ""),
                    reportado_por=params.get("reportado_por", "Agente OCR"),
                    descripcion_falla=params.get("descripcion_falla", texto[:500]),
                )
                # Enrich chunk metadata with solicitud_id and equipo_serial for RAG retrieval
                for chunk in chunks:
                    chunk.metadata["solicitud_id"] = solicitud_creada.id
                    chunk.metadata["equipo_serial"] = solicitud_creada.equipo_id
            except ValueError:
                pass

        self._vector_store.store(chunks, embeddings)
        return decision, solicitud_creada, texto
