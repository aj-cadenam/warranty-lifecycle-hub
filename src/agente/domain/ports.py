from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agente.domain.entities import DecisionAgente


class OCRPort(ABC):
    @abstractmethod
    def extract_text(self, pdf_path: str) -> str: ...


class LLMPort(ABC):
    @abstractmethod
    def decide(self, context: str) -> "DecisionAgente": ...
    @abstractmethod
    def generate_email(self, context: str) -> dict[str, str]: ...


class EmbeddingPort(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]: ...


class VectorStorePort(ABC):
    @abstractmethod
    def store(self, chunks: list, embeddings: list[list[float]]) -> None: ...
    @abstractmethod
    def search(self, query_embedding: list[float], limit: int = 5) -> list[dict]: ...


class EmailPort(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None: ...
