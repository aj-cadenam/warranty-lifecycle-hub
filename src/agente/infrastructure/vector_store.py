import json
from django.db import connection
from src.agente.domain.ports import VectorStorePort
from src.agente.infrastructure.chunking import Chunk

_DDL = (
    "CREATE TABLE IF NOT EXISTS document_chunks ("
    "id SERIAL PRIMARY KEY, text TEXT, embedding vector(768), metadata JSONB)"
)


class PgVectorStoreAdapter(VectorStorePort):
    def _ensure_table(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cursor.execute(_DDL)

    def store(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self._ensure_table()
        with connection.cursor() as cursor:
            for chunk, embedding in zip(chunks, embeddings):
                cursor.execute(
                    "INSERT INTO document_chunks (text, embedding, metadata) VALUES (%s, %s::vector, %s)",
                    [chunk.text, str(embedding), json.dumps(chunk.metadata)],
                )

    def search(self, query_embedding: list[float], limit: int = 5) -> list[dict]:
        self._ensure_table()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT text, metadata, 1 - (embedding <=> %s::vector) AS similarity "
                "FROM document_chunks ORDER BY embedding <=> %s::vector LIMIT %s",
                [str(query_embedding), str(query_embedding), limit],
            )
            rows = cursor.fetchall()
        return [{"text": r[0], "metadata": json.loads(r[1]) if isinstance(r[1], str) else r[1], "similarity": float(r[2])} for r in rows]


class FakeVectorStoreAdapter(VectorStorePort):
    def __init__(self):
        self._chunks: list[dict] = []

    def store(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        for chunk, emb in zip(chunks, embeddings):
            self._chunks.append({"text": chunk.text, "metadata": chunk.metadata, "embedding": emb})

    def search(self, query_embedding: list[float], limit: int = 5) -> list[dict]:
        return [{"text": c["text"], "metadata": c["metadata"], "similarity": 0.9}
                for c in self._chunks[:limit]]
