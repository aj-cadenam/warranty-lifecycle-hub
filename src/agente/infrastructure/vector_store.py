import json
from django.db import connection
from src.agente.infrastructure.chunking import Chunk


def store_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS document_chunks ("
            "id SERIAL PRIMARY KEY, text TEXT, embedding vector(768), metadata JSONB)"
        )
        for chunk, embedding in zip(chunks, embeddings):
            cursor.execute(
                "INSERT INTO document_chunks (text, embedding, metadata) VALUES (%s, %s::vector, %s)",
                [chunk.text, str(embedding), json.dumps(chunk.metadata)],
            )


def search_similar(query_embedding: list[float], limit: int = 5) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT text, metadata, 1 - (embedding <=> %s::vector) AS similarity "
            "FROM document_chunks ORDER BY embedding <=> %s::vector LIMIT %s",
            [str(query_embedding), str(query_embedding), limit],
        )
        rows = cursor.fetchall()
    return [{"text": r[0], "metadata": r[1], "similarity": r[2]} for r in rows]
