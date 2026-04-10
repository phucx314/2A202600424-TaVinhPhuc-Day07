import os
from src.chunking import ChunkingStrategyComparator

files_to_test = [
    "data/Viettel Cloud WAF.md",
    "data/Viettel Cloudrity.md",
    "data/Viettel Threat Intelligence.md"
]

comparator = ChunkingStrategyComparator()

print("| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |")
print("|-----------|----------|-------------|------------|-------------------|")

for file_path in files_to_test:
    if not os.path.exists(file_path):
        print(f"| LỖI | Không thấy file {file_path} | - | - | - |")
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    doc_name = os.path.basename(file_path).replace('.md', '')

    results = comparator.compare(text, chunk_size=200)

    print(f"| {doc_name} | FixedSizeChunker | {results['fixed_size']['count']} | {results['fixed_size']['avg_length']:.0f} |  |")
    print(f"| {doc_name} | SentenceChunker | {results['by_sentences']['count']} | {results['by_sentences']['avg_length']:.0f} |  |")
    print(f"| {doc_name} | RecursiveChunker | {results['recursive']['count']} | {results['recursive']['avg_length']:.0f} |  |")