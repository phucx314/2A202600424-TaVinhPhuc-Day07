from __future__ import annotations

import math
import re

class FixedSizeChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks

class SentenceChunker:
    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|(?<=\.)\n', text) if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i : i + self.max_sentences_per_chunk])
            chunks.append(chunk)
        return chunks

class RecursiveChunker:
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]
        
        if not remaining_separators:
            return [current_text[i:i+self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        sep = remaining_separators[0]
        next_seps = remaining_separators[1:]

        splits = current_text.split(sep)
        chunks = []
        current_chunk = ""

        for i, part in enumerate(splits):
            piece = part + sep if i < len(splits) - 1 else part
            if len(current_chunk) + len(piece) <= self.chunk_size:
                current_chunk += piece
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if len(piece) > self.chunk_size:
                    chunks.extend(self._split(piece, next_seps))
                    current_chunk = ""
                else:
                    current_chunk = piece

        if current_chunk:
            chunks.append(current_chunk)

        return [c.strip() for c in chunks if c.strip()]

def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))

def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot_prod = _dot(vec_a, vec_b)
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(x * x for x in vec_b))
    
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_prod / (mag_a * mag_b)

class ChunkingStrategyComparator:
    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed = FixedSizeChunker(chunk_size=chunk_size).chunk(text)
        sentence = SentenceChunker().chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)
        
        def get_avg(chunks_list):
            if not chunks_list: return 0
            return sum(len(c) for c in chunks_list) / len(chunks_list)
        
        return {
            "fixed_size": {
                "count": len(fixed),
                "avg_length": get_avg(fixed),
                "chunks": fixed
            },
            "by_sentences": {
                "count": len(sentence),
                "avg_length": get_avg(sentence),
                "chunks": sentence
            },
            "recursive": {
                "count": len(recursive),
                "avg_length": get_avg(recursive),
                "chunks": recursive
            }
        }