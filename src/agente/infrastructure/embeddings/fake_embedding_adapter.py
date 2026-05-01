from src.agente.domain.ports import EmbeddingPort


class FakeEmbeddingAdapter(EmbeddingPort):
    def __init__(self, dim: int = 768):
        self._dim = dim

    def embed(self, text: str) -> list[float]:
        return [0.1] * self._dim
