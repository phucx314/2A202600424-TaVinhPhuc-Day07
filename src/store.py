from __future__ import annotations
from typing import Any, Callable
import uuid

from .chunking import _dot, compute_similarity
from .embeddings import _mock_embed
from .models import Document

class EmbeddingStore:
    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb
            self._chroma_client = chromadb.Client()
            unique_name = f"{collection_name}_{uuid.uuid4().hex}"
            self._collection = self._chroma_client.create_collection(name=unique_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        emb = self._embedding_fn(doc.content)
        idx = str(self._next_index)
        self._next_index += 1

        meta = doc.metadata.copy() if doc.metadata else {}
        
        if "doc_id" not in meta:
            if hasattr(doc, "id") and doc.id is not None:
                meta["doc_id"] = doc.id
            elif hasattr(doc, "doc_id") and doc.doc_id is not None:
                meta["doc_id"] = doc.doc_id
            else:
                meta["doc_id"] = idx

        return {
            "id": idx,
            "content": doc.content,
            "metadata": meta,
            "embedding": emb
        }

    def _search_records(self, query_emb: list[float], records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        scored = []
        for rec in records:
            score = compute_similarity(query_emb, rec["embedding"])
            scored.append((score, rec))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"content": item["content"], "metadata": item["metadata"], "score": score} for score, item in scored[:top_k]]

    def add_documents(self, docs: list[Document]) -> None:
        if not docs:
            return
        records = [self._make_record(doc) for doc in docs]
        
        if self._use_chroma:
            self._collection.add(
                ids=[r["id"] for r in records],
                documents=[r["content"] for r in records],
                metadatas=[r["metadata"] for r in records],
                embeddings=[r["embedding"] for r in records]
            )
        else:
            self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_emb = self._embedding_fn(query)
        
        if self._use_chroma:
            results = self._collection.query(
                query_embeddings=[query_emb],
                n_results=top_k
            )
            output = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    output.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    })
            return output
        else:
            return self._search_records(query_emb, self._store, top_k)

    def get_collection_size(self) -> int:
        if self._use_chroma:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        query_emb = self._embedding_fn(query)
        
        if self._use_chroma:
            results = self._collection.query(
                query_embeddings=[query_emb],
                n_results=top_k,
                where=metadata_filter
            )
            output = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    output.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    })
            return output
        else:
            filtered_records = self._store
            if metadata_filter:
                filtered_records = [
                    r for r in self._store 
                    if all(r["metadata"].get(k) == v for k, v in metadata_filter.items())
                ]
            return self._search_records(query_emb, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        initial_size = self.get_collection_size()
        
        if self._use_chroma:
            try:
                self._collection.delete(where={"doc_id": doc_id})
            except Exception:
                pass
        else:
            self._store = [
                r for r in self._store 
                if r.get("metadata", {}).get("doc_id") != doc_id
            ]
            
        return self.get_collection_size() < initial_size