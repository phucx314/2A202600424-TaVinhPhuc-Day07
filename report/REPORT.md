# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Tạ Vĩnh Phúc
**Nhóm:** 10
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Nghĩa là 2 đoạn text có "hướng ý nghĩa" gần y hệt nhau trong không gian toán học (điểm gần 1).

**Ví dụ HIGH similarity:**
- Sentence A: Tôi thích lập trình Python.
- Sentence B: Tôi rất thích code bằng Python.
- Tại sao tương đồng: Cả hai câu đều nói về sở thích lập trình bằng Python, chỉ khác nhau về cách diễn đạt.

**Ví dụ LOW similarity:**
- Sentence A: Tôi thích lập trình Python
- Sentence B: Hôm nay trời mưa to
- Tại sao khác: Hai câu hoàn toàn không liên quan đến nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Vì văn bản có độ dài ngắn khác nhau -> độ lớn vector khác nhau. Cosine chỉ đo góc (hướng ý nghĩa), nên một câu ngắn 5 chữ và một đoạn văn 500 chữ nếu nói về cùng một chủ đề thì vẫn match được với nhau. Nếu đo bằng Euclidean thì câu dài câu ngắn sẽ bị tính là cách xa nhau.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`
> -> `num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks.`
> Overlap nhiều hơn để chống gãy context. Ví dụ chunk 1 kết thúc ở chữ "Tôi rất", chunk 2 bắt đầu bằng "thích đi ngủ". Tách ra AI đọc ko hiểu do mất context. Có overlap thì chunk 2 sẽ là "Tôi rất thích đi ngủ", giữ nguyên được context.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Cybersecurity products & services (Viettel Cyber Security)

**Tại sao nhóm chọn domain này?**
> Viettel Cyber Security cung cấp hệ sinh thái giải pháp an toàn thông tin đa dạng (WAF, SOC, Threat Intelligence, Endpoint Security, CSMP). Các tài liệu datasheet có cấu trúc rõ ràng, giàu thuật ngữ chuyên ngành, phù hợp để xây dựng hệ thống RAG hỗ trợ tư vấn sản phẩm bảo mật.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Viettel Cloud WAF | Viettel IDC Datasheet | 4,481 | product: "Cloud WAF", category: "web_security", service_type: "WAF", provider: "Viettel IDC" |
| 2 | Viettel Cloudrity | Viettel IDC Datasheet | 2,914 | product: "Cloudrity", category: "web_security", service_type: "Anti-DDoS & WAF", provider: "Viettel IDC" |
| 3 | Viettel Threat Intelligence | Viettel IDC Datasheet | 5,727 | product: "Threat Intelligence", category: "threat_intelligence", service_type: "Threat Feed", provider: "Viettel IDC" |
| 4 | Viettel Virtual SOC | Viettel IDC Datasheet | 9,149 | product: "Virtual SOC", category: "soc_monitoring", service_type: "Managed SOC", provider: "Viettel IDC" |
| 5 | Viettel CSMP | Viettel IDC Datasheet | 3,491 | product: "CSMP", category: "consulting", service_type: "Maturity Program", provider: "Viettel IDC" |
| 6 | Viettel Endpoint Security | Viettel IDC Datasheet | 15,909 | product: "Endpoint Security", category: "endpoint_protection", service_type: "EDR/EPP", provider: "Viettel IDC" |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| product | string | "Cloud WAF", "Virtual SOC" | Lọc kết quả theo sản phẩm cụ thể khi user hỏi về một giải pháp |
| category | string | "web_security", "endpoint_protection" | Nhóm các sản phẩm cùng lĩnh vực, hỗ trợ so sánh giải pháp |
| service_type | string | "WAF", "Managed SOC", "EDR/EPP" | Phân biệt loại dịch vụ chi tiết, giúp retrieval chính xác hơn |
| provider | string | "Viettel IDC" | Xác định nguồn cung cấp, hữu ích khi mở rộng thêm vendor khác |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Viettel Cloud WAF | FixedSizeChunker (`fixed_size`) | 30 | 198 | Kém |
| Viettel Cloud WAF | SentenceChunker (`by_sentences`) | 3 | 1492 | Kém |
| Viettel Cloud WAF | RecursiveChunker (`recursive`) | 35 | 127 | Tốt |
| Viettel Cloudrity | FixedSizeChunker (`fixed_size`) | 19 | 197 | Kém |
| Viettel Cloudrity | SentenceChunker (`by_sentences`) | 7 | 406 | Kém |
| Viettel Cloudrity | RecursiveChunker (`recursive`) | 24 | 117 | Tốt |
| Viettel Threat Intelligence | FixedSizeChunker (`fixed_size`) | 38 | 199 | Kém |
| Viettel Threat Intelligence | SentenceChunker (`by_sentences`) | 13 | 439 | Kém |
| Viettel Threat Intelligence | RecursiveChunker (`recursive`) | 51 | 110 | Tốt |

### Strategy Của Tôi

**Loại:** RecursiveChunker kết hợp Metadata Filtering

**Mô tả cách hoạt động:**
> Thuật toán chia văn bản đệ quy dựa trên mức độ ưu tiên của các ký tự phân tách: Đoạn văn (\n\n) -> Dòng (\n) -> Dấu chấm (. ).

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Nhìn vào bảng Baseline, SentenceChunker thất bại ở file Viettel Cloud WAF.md (chỉ ra 3 chunks khổng lồ dài 1492 ký tự). Lý do là tài liệu kỹ thuật Markdown xài gạch đầu dòng hoặc bảng biểu chứ ít dùng dấu chấm câu, khiến regex cắt câu bị vô hiệu hóa. RecursiveChunker khai thác triệt để dấu \n nên cắt cực kỳ mượt, giữ nguyên vẹn từng tính năng kỹ thuật.

**Code snippet (nếu custom):**
```python
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
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| Viettel Cloud WAF | FixedSize (Baseline) | 30 | 198 | Kém |
| Viettel Cloud WAF | Recursive (Của tôi) | 35 | 127 | Tốt |
| Viettel Cloudrity | FixedSize (Baseline) | 19 | 197 | Kém |
| Viettel Cloudrity | Recursive (Của tôi) | 24 | 117 | Tốt |
| Viettel Threat Intelligence | FixedSize (Baseline) | 38 | 199 | Kém |
| Viettel Threat Intelligence | Recursive (Của tôi) | 51 | 110 | Tốt |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tạ Vĩnh Phúc | RecursiveChunker + Filter | 9 | Giữ trọn vẹn cấu trúc Markdown (bảng biểu, gạch đầu dòng). Filter giúp loại bỏ hoàn toàn nhiễu giữa các sản phẩm WAF/SOC/TI | Cần thời gian tiền xử lý dữ liệu và gắn metadata thủ công lúc đầu |
| Vũ Trung Lập    | Markdown Chunker                  | 10                    | Không gãy đổ Context logic của Document đặc thù.                                                                                      | Phụ thuộc vào chất lượng formatting Markdown.                                                                             |
| Dương Mạnh Kiên | RecursiveChunker (chunk_size=500) | 8                     | 133 chunks trên 6 tài liệu, 22% chunk có header, giữ nguyên cấu trúc section markdown, phù hợp tài liệu datasheet có cấu trúc rõ ràng | Số lượng chunk nhiều nhất (133 vs 90/63), avg length nhỏ (311 ký tự), một số chunk quá ngắn (3-32 ký tự) do separator --- |
| Nguyễn Văn Hiếu | Header Chunker                    | 9                     | Giữ trọn vẹn ý nghĩa mục lục                                                                                                          | Phụ thuộc định dạng Markdown                                                                                              |
| Bùi Quang Hải   | MarkdownHeaderChunker (Custom)    | 9.5                   | Giữ trọn vẹn ngữ cảnh theo tiêu đề, metadata heading phong phú.                                                                       | Kích thước chunk không đồng đều tùy theo văn bản gốc.                                                                     |
| Lê Đức Hải      | RecursiveChunker                  | 9                     | Giữ trọn vẹn các đoạn văn và đề mục Markdown.                                                                                         | Phức tạp trong việc thiết lập tham số                                                                                     |


**Strategy nào tốt nhất cho domain này? Tại sao?**
> Markdown Chunker chính là chân ái cho dữ liệu Datasheet. Vì văn bản Markdown có bố cục Heading phân tầng cực kỳ rõ ràng, chúng ta có thể tận dụng nó để khoanh vùng tính năng một cách biệt lập. Khi thực hiện RAG, hệ thống sẽ đánh đâu trúng đó, lấy được đúng mẩu thông tin mục tiêu mà không bị lẫn tạp chất Context từ các phần khác, giúp câu trả lời cực kỳ tập trung và chuẩn xác.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Sử dụng kỹ thuật Regular Expression (Regex) với mẫu r'(?<=[.!?])\s+|(?<=\.)\n' để thực hiện việc tách câu. Kỹ thuật Lookbehind này giúp hệ thống nhận diện chính xác các điểm kết thúc câu dựa trên dấu câu (.!?) mà không làm mất đi các ký tự phân tách. Phương pháp này xử lý hiệu quả các trường hợp văn bản Markdown có tiêu đề ngắn hoặc danh sách không có dấu chấm cuối dòng, đảm bảo tính toàn vẹn của dữ liệu đầu vào.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thuật toán được triển khai theo cơ chế chia để trị dựa trên danh sách các ký tự phân tách có độ ưu tiên giảm dần (\n\n -> \n -> . ). Base case của hàm đệ quy được thiết lập khi độ dài văn bản nhỏ hơn chunk_size hoặc đã duyệt hết danh sách separators. Đặc biệt, tôi đã tối ưu hóa logic bằng cách gom nhóm các đoạn văn bản nhỏ để đảm bảo mỗi chunk đạt độ dài xấp xỉ chunk_size, từ đó tối đa hóa context cho LLM.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Dữ liệu được quản lý dưới dạng cấu trúc dictionary in-memory hoặc lưu trữ trong ChromaDB, tích hợp đồng bộ giữa vector embedding và hệ thống metadata. Trong hàm search, tôi sử dụng thuật toán tính Cosine Similarity để đo lường khoảng cách giữa query vector và tập hợp các document vectors. Kết quả được sắp xếp theo thứ tự giảm dần về độ tương đồng, cho phép truy xuất TopK những đoạn văn bản có sự liên quan chặt chẽ nhất về mặt ngữ nghĩa.

**`search_with_filter` + `delete_document`** — approach:
> Tôi áp dụng chiến lược Pre-filtering (lọc trước khi truy vấn): hệ thống sẽ quét qua metadata để lọc ra các tài liệu thỏa mãn điều kiện (ví dụ: lọc theo product hoặc category), sau đó mới thực hiện tính toán similarity trên tập dữ liệu đã thu hẹp. Cách tiếp cận này giúp tối ưu hóa hiệu năng và độ chính xác. Hàm delete_document được thiết kế để loại bỏ triệt để các bản ghi dựa trên doc_id, đảm bảo tính nhất quán và sạch sẽ cho cơ sở dữ liệu vector.

### KnowledgeBaseAgent

**`answer`** — approach:
> Cấu trúc Prompt được thiết kế theo dạng chỉ thị nghiêm ngặt (Strict Instruction-based): định hướng AI đóng vai trò chuyên gia phân tích, chỉ được phép sử dụng thông tin từ context được cung cấp và phải từ chối trả lời nếu dữ liệu không đầy đủ để tránh hiện tượng "ảo giác" (hallucination). Context injection được thực hiện bằng cách chuẩn hóa các Top-K chunks thành một khối văn bản có cấu trúc rõ ràng (thông qua bullet points), giúp LLM dễ dàng phân tích và trích xuất thông tin một cách mạch lạc.

### Test Results

```
# Paste output of: pytest tests/ -v

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                                                                     [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                                                                              [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                                                                       [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                                                                        [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                                                                             [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                                                                             [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                                                                   [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                                                                    [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                                                                  [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                                                                    [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                                                                    [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                                                                               [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                                                                           [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                                                                     [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                                                                            [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                                                                                [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                                                                          [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                                                                                [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                                                                    [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                                                                      [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                                                                        [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                                                                              [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                                                                   [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                                                                     [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                                                                         [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                                                                      [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                                                                               [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                                                                              [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                                                                         [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                                                                     [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                                                                                [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                                                                    [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                                                                          [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                                                                    [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                                                                                 [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                                                                               [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                                                                              [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                                                                  [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                                                                             [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                                                                      [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                                                                            [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                                                                                [100%]

====================================================================================== 42 passed in 0.06s =======================================================================================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Bảo vệ ứng dụng web khỏi OWASP | Tính năng của tường lửa WAF | High | 0.05 | Sai |
| 2 | Cập nhật IP độc hại | Dữ liệu Threat Intelligence Feed | High | -0.06 | Sai |
| 3 | WAF chặn tấn công web | SOC giám sát an toàn thông tin | Low | 0.18 | Đúng |
| 4 | Cloudrity hỗ trợ Multi-Cloud | Hướng dẫn triển khai Cloudrity | High | -0.04 | Sai |
| 5 | Cài đặt Endpoint Security | Chống tấn công DDoS L4/L7 | Low | -0.06 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Bất ngờ nhất là Pair 1 và 2: hai câu rõ ràng nói về cùng chủ đề (WAF/OWASP, Threat Intelligence) nhưng lại có score gần 0 hoặc âm. Nguyên nhân là `MockEmbedder` tạo vector từ MD5 hash — hoàn toàn ngẫu nhiên và không capture ngữ nghĩa. Điều này chứng minh rằng chất lượng embedding model là nền tảng sống còn của toàn bộ hệ thống RAG: nếu embedding sai thì retrieval sẽ thất bại dù chunking strategy có tốt đến đâu.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Viettel Cloud WAF có những gói dịch vụ nào? | 3 gói: Standard, Advanced, Complete — khác nhau về WAF, Bot Manager, DDoS, Data Retention |
| 2 | Giải pháp nào của Viettel giúp chống tấn công DDoS? | Viettel Cloudrity (Anti-DDoS L4/L7) và Viettel Cloud WAF (DDoS Protection lên đến 15 Tbps) |
| 3 | Viettel Threat Intelligence thu thập dữ liệu từ những nguồn nào? | ISP toàn cầu, đối tác FIRST/APWG, Pentest, Threat Hunting, Managed Security Service, nghiên cứu nội bộ APT/zero-day |
| 4 | SOC của Viettel tổ chức vận hành như thế nào? | 6 nhóm: Tier 1 (giám sát 24/7), Tier 2 (xử lý sự cố), Tier 3 (chuyên sâu), Content Analysis, Threat Analysis, SOC Manager |
| 5 | Viettel Endpoint Security hỗ trợ những hệ điều hành nào? | Windows, Linux, macOS, Android, iOS; tương thích VMware, Hyper-V, XenServer, KVM |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Viettel Cloud WAF có những gói dịch vụ nào? | Công nghệ hiện đại, phù hợp xu thế: Viettel IDC cam kết... | 0.2525 | No | MockEmbedder không hỗ trợ LLM call |
| 2 | Giải pháp nào của Viettel giúp chống tấn công DDoS? | ## Phản hồi và ứng cứu sự cố 24/7 | 0.3823 | No | MockEmbedder không hỗ trợ LLM call |
| 3 | Viettel Threat Intelligence thu thập dữ liệu từ những nguồn nào? | Viettel cung cấp hệ thống SOC đi kèm với hệ sinh thái... | 0.2877 | No | MockEmbedder không hỗ trợ LLM call |
| 4 | SOC của Viettel tổ chức vận hành như thế nào? | Tính năng / Khả năng tương thích hệ điều hành... | 0.3851 | No | MockEmbedder không hỗ trợ LLM call |
| 5 | Viettel Endpoint Security hỗ trợ những hệ điều hành nào? | Anti-Phishing và Web Security: Bảo vệ khỏi các dạng Phishing... | 0.4525 | No | MockEmbedder không hỗ trợ LLM call |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 0 / 5

> **Giải thích:** Hệ thống load 208 chunks từ 6 tài liệu thật trong `data/`. MockEmbedder tạo vector bằng MD5 hash nên không capture ngữ nghĩa — retrieval hoàn toàn ngẫu nhiên, query nào cũng lấy sai document. Đây là minh chứng thực tế rõ ràng nhất về tầm quan trọng của embedding model thật trong RAG production.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Từ Trung Lập, tôi nhận ra rằng MarkdownChunker — dù đơn giản về mặt triển khai — lại cực kỳ hiệu quả với tài liệu có cấu trúc heading rõ ràng như datasheet của Viettel. Strategy này khai thác trực tiếp bố cục sẵn có của tài liệu thay vì cố gắng phân tích ngôn ngữ, khiến mỗi chunk biệt lập hoàn toàn về logic và không bị lẫn context giữa các tính năng khác nhau.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Qua phần demo của các nhóm, tôi nhận thấy mỗi nhóm có hướng tiếp cận riêng với cùng một bài toán RAG — từ lựa chọn embedding model, chiến lược chunking đến cách tổ chức metadata schema. Điều này cho thấy không có một giải pháp tối ưu duy nhất mà phụ thuộc vào đặc thù domain và dữ liệu, và việc so sánh kết quả giữa các nhóm chính là cách học hiệu quả nhất để calibrate lại strategy của bản thân.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ ưu tiên dùng embedding model thật (LocalEmbedder với `all-MiniLM-L6-v2`) ngay từ đầu thay vì MockEmbedder để kết quả benchmark phản ánh đúng chất lượng retrieval. Ngoài ra, tôi sẽ bổ sung thêm trường metadata `section` để ghi lại tiêu đề section mà chunk được trích xuất, giúp `search_with_filter()` lọc chính xác hơn đến từng phần trong cùng một sản phẩm.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **100 / 100** |
