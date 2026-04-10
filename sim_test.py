from src.embeddings import MockEmbedder
from src.chunking import compute_similarity

embedder = MockEmbedder()

pairs = [
    ("Tính năng Web Application Firewall bảo vệ khỏi các cuộc tấn công DDoS.", "WAF của giải pháp giúp ngăn chặn DDoS attacks hiệu quả."),
    ("Sản phẩm Endpoint Security cung cấp khả năng phát hiện vi rút.", "Giải pháp bảo mật điểm cuối có chống mã độc."),
    ("Viettel Cloud WAF có giá bao nhiêu?", "Mức phí dịch vụ của Viettel Cloud WAF là bao nhiêu?"),
    ("Giải pháp này sử dụng AI để phân tích.", "Hôm nay trời đẹp quá đi chơi thôi."),
    ("Viettel CSMP đánh giá tổng thể an toàn thông tin.", "Dịch vụ đánh giá an toàn thông tin toàn diện CSMP của Viettel.")
]

for a, b in pairs:
    emb_a = embedder(a)
    emb_b = embedder(b)
    sim = compute_similarity(emb_a, emb_b)
    print(f"A: {a}\nB: {b}\nSim: {sim:.4f}\n")
