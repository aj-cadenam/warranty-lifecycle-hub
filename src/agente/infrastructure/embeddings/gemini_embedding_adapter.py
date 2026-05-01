import google.generativeai as genai
from src.agente.domain.ports import EmbeddingPort


class GeminiEmbeddingAdapter(EmbeddingPort):
    def __init__(self, api_key: str, dim: int = 768):
        genai.configure(api_key=api_key)
        self._dim = dim

    def embed(self, text: str) -> list[float]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
            output_dimensionality=self._dim,
        )
        return result["embedding"]
