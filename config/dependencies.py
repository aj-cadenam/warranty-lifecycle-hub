# config/dependencies.py
from config.settings import settings
from src.agente.infrastructure.email.fake_email_adapter import FakeEmailAdapter
from src.agente.infrastructure.llm.fake_llm_adapter import FakeLLMAdapter
from src.agente.infrastructure.embeddings.fake_embedding_adapter import FakeEmbeddingAdapter
from src.agente.infrastructure.ocr.fake_ocr_adapter import FakeOCRAdapter


def get_equipo_repo():
    from src.equipos.infrastructure.repositories import DjangoEquipoRepository
    return DjangoEquipoRepository()


def get_garantia_repo():
    from src.equipos.infrastructure.repositories import DjangoGarantiaRepository
    return DjangoGarantiaRepository()


def get_solicitud_repo():
    from src.solicitudes.infrastructure.repositories import DjangoSolicitudRepository
    return DjangoSolicitudRepository()


def get_trazabilidad_repo():
    from src.trazabilidad.infrastructure.repositories import DjangoTrazabilidadRepository
    return DjangoTrazabilidadRepository()


def get_borrador_repo():
    from src.seguimiento.infrastructure.repositories import DjangoBorradorCorreoRepository
    return DjangoBorradorCorreoRepository()


def get_evento_seguimiento_repo():
    from src.seguimiento.infrastructure.repositories import DjangoEventoSeguimientoRepository
    return DjangoEventoSeguimientoRepository()


def get_email_adapter() -> FakeEmailAdapter:
    return FakeEmailAdapter()


def get_llm_adapter():
    if settings.LLM_PROVIDER == "gemini":
        from src.agente.infrastructure.llm.gemini_llm_adapter import GeminiLLMAdapter
        return GeminiLLMAdapter(api_key=settings.GEMINI_API_KEY)
    return FakeLLMAdapter()


def get_embedding_adapter():
    if settings.EMBEDDING_PROVIDER == "gemini":
        from src.agente.infrastructure.embeddings.gemini_embedding_adapter import GeminiEmbeddingAdapter
        return GeminiEmbeddingAdapter(api_key=settings.GEMINI_API_KEY, dim=settings.EMBEDDING_DIM)
    return FakeEmbeddingAdapter(dim=settings.EMBEDDING_DIM)


def get_ocr_adapter():
    if settings.OCR_BACKEND == "gemini":
        from src.agente.infrastructure.ocr.gemini_ocr_adapter import GeminiOCRAdapter
        return GeminiOCRAdapter(api_key=settings.GEMINI_API_KEY)
    return FakeOCRAdapter()


def get_vector_store():
    from src.agente.infrastructure.vector_store import PgVectorStoreAdapter
    return PgVectorStoreAdapter()
