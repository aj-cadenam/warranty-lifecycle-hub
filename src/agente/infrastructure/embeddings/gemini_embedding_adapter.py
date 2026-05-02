from google import genai
from langfuse import observe
from src.agente.domain.ports import EmbeddingPort


class GeminiEmbeddingAdapter(EmbeddingPort):
    def __init__(self, api_key: str, dim: int = 768):
        self._client = genai.Client(api_key=api_key)
        self._dim = dim

    @observe(as_type="embedding", name="embedding.embed")
    def embed(self, text: str) -> list[float]:
        result = self._client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=text,
        )
        vector = result.embeddings[0].values
        return list(vector[: self._dim])
