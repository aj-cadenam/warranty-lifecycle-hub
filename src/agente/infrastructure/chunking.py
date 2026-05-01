from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    index: int
    metadata: dict


class ChunkingService:
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        metadata = metadata or {}
        words = text.split()
        chunks = []
        start = 0
        index = 0
        while start < len(words):
            end = min(start + self._chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            chunks.append(Chunk(text=chunk_text, index=index, metadata={**metadata, "chunk_index": index}))
            start += self._chunk_size - self._overlap
            index += 1
        return chunks
