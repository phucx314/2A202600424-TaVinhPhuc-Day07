from typing import Callable
from .store import EmbeddingStore

class KnowledgeBaseAgent:
    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        
        if not results:
            return "Xin lỗi, không có thông tin liên quan trong cơ sở dữ liệu."

        context_parts = [f"- {res['content']}" for res in results]
        context = "\n".join(context_parts)
        
        prompt = (
            f"Dựa vào thông tin cung cấp dưới đây, hãy trả lời câu hỏi.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        
        return self.llm_fn(prompt)