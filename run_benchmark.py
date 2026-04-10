import uuid
from pathlib import Path
from src.chunking import RecursiveChunker, compute_similarity
from src.store import EmbeddingStore
from src.embeddings import _mock_embed, LocalEmbedder
from src.models import Document

try:
    embedder = LocalEmbedder()
    print(f"[INFO] Embedding backend: {embedder._backend_name}")
except Exception as e:
    print(f"[WARN] LocalEmbedder không khởi động được ({e}), fallback về MockEmbedder")
    embedder = _mock_embed

DATA_DIR = Path(__file__).parent / "data"

METADATA_MAP = {
    "Viettel Cloud WAF.md":           {"product": "Cloud WAF",            "category": "web_security",         "service_type": "WAF",              "provider": "Viettel IDC"},
    "Viettel Cloudrity.md":           {"product": "Cloudrity",             "category": "web_security",         "service_type": "Anti-DDoS & WAF",  "provider": "Viettel IDC"},
    "Viettel Threat Intelligence.md": {"product": "Threat Intelligence",   "category": "threat_intelligence",  "service_type": "Threat Feed",       "provider": "Viettel IDC"},
    "Viettel Virtual SOC.md":         {"product": "Virtual SOC",           "category": "soc_monitoring",       "service_type": "Managed SOC",       "provider": "Viettel IDC"},
    "Viettel CSMP.md":                {"product": "CSMP",                  "category": "consulting",           "service_type": "Maturity Program",  "provider": "Viettel IDC"},
    "Viettel Endpoint Security.md":   {"product": "Endpoint Security",     "category": "endpoint_protection",  "service_type": "EDR/EPP",           "provider": "Viettel IDC"},
}

QUERIES = [
    "Viettel Cloud WAF có những gói dịch vụ nào?",
    "Giải pháp nào của Viettel giúp chống tấn công DDoS?",
    "Viettel Threat Intelligence thu thập dữ liệu từ những nguồn nào?",
    "SOC của Viettel tổ chức vận hành như thế nào?",
    "Viettel Endpoint Security hỗ trợ những hệ điều hành nào?",
]

def build_store() -> EmbeddingStore:
    chunker = RecursiveChunker(chunk_size=300)
    store = EmbeddingStore(embedding_fn=embedder)
    docs = []

    for md_file in DATA_DIR.glob("*.md"):
        meta = METADATA_MAP.get(md_file.name, {"product": md_file.stem})
        text = md_file.read_text(encoding="utf-8")
        chunks = chunker.chunk(text)
        for chunk in chunks:
            docs.append(Document(id=str(uuid.uuid4()), content=chunk, metadata=meta))

    store.add_documents(docs)
    print(f"[INFO] Loaded {len(docs)} chunks from {DATA_DIR}\n")
    return store

def run_benchmark():
    store = build_store()

    print("=" * 60)
    print("PHẦN 6: BENCHMARK QUERIES — KẾT QUẢ CÁ NHÂN")
    print("=" * 60)
    print(f"{'#':<3} {'Query':<45} {'Top-1 Chunk (tóm tắt)':<40} {'Score':>6} {'Rel?':<6}")
    print("-" * 60)

    results_table = []
    for i, q in enumerate(QUERIES, 1):
        hits = store.search(q, top_k=3)
        if not hits:
            results_table.append((i, q, "N/A", 0.0, "No"))
            continue

        best = hits[0]
        chunk_text = best["content"]
        score = best.get("score")
        if score is None:
            score = compute_similarity(_mock_embed(q), _mock_embed(chunk_text))

        short = (chunk_text[:55] + "...") if len(chunk_text) > 55 else chunk_text
        results_table.append((i, q, short, score, "?"))
        print(f"| {i} | {q[:43]:<43} | {short:<55} | {score:.4f} |")
        print(f"  → Full chunk: {chunk_text[:120]}")
        print()

    return results_table

if __name__ == "__main__":
    run_benchmark()