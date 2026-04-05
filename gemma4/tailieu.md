# Tài liệu và Tổng hợp Code Gemma 4 (Cập nhật 3)

File này tổng hợp toàn bộ mã nguồn của module `gemma4` phục vụ cho hệ thống Telegram Chatbot Serverless, bao gồm STT, LLM, Tool Call, Embedding, **Vision Analysis** và **Multimodal Document Processing**.

## 1. Cấu trúc thư mục
```
gemma4/
├── __init__.py      # Khởi tạo package và export API
├── manager.py       # Quản lý Singleton Model & Processor (Text, Audio, Vision)
├── llm.py           # Text Generation
├── stt.py           # Speech to Text
├── tools.py         # Tool Call Scoring
├── embeddings.py    # Text/Image Embedding
├── vision.py        # Phân tích hình ảnh (Mô tả, VQA) [NEW]
├── files.py         # Xử lý file đa định dạng (PDF, DOCX, XLSX, ...) [NEW]
└── requirements.md  # Yêu cầu hệ thống
```

---

## 2. Các chức năng mới (Cập nhật 3)

### 2.1. Phân tích hình ảnh (`gemma4/vision.py`)
Hỗ trợ mô tả ảnh chi tiết và trả lời câu hỏi dựa trên nội dung ảnh (Visual Question Answering).

```python
from gemma4.vision import describe_image, query_image

# 1. Lấy mô tả ảnh
description = describe_image("path/to/image.png")

# 2. Hỏi đáp về ảnh
answer = query_image("path/to/image.png", "Trong ảnh có bao nhiêu người?")
```

### 2.2. Xử lý file văn bản và dữ liệu (`gemma4/files.py`)
Hỗ trợ đọc nội dung từ nhiều định dạng file và đưa vào LLM kèm prompt xử lý. Các định dạng hỗ trợ: **PDF, DOCX, XLSX, CSV, PPTX, TXT**.

```python
from gemma4.files import process_file_with_prompt

# Phân tích file PDF hoặc Excel bằng prompt
result = process_file_with_prompt("data/report.pdf", "Hãy tóm tắt các ý chính trong tài liệu này.")
result_excel = process_file_with_prompt("data/sales.xlsx", "Tính tổng doanh thu và liệt kê top 3 mặt hàng bán chạy.")
```

---

## 3. Mã nguồn chi tiết các module mới

### 3.1. `gemma4/manager.py` (Hỗ trợ Multimodal Image)
Cập nhật hàm `generate` để nhận thêm tham số `image_path` và tự động tích hợp vào prompt.

### 3.2. `gemma4/files.py` (Trích đoạn logic đọc file)
Sử dụng các thư viện `pypdf`, `python-docx`, `openpyxl`, `python-pptx` để trích xuất text thô từ các định dạng tương ứng, sau đó gộp vào prompt của Gemma 4.

### 3.3. `gemma4/vision.py`
Wrapper quanh `Gemma4Manager` để thực hiện các tác vụ vision chuyên biệt.

---

## 4. Cách sử dụng tổng quát
Module `gemma4` giờ đây là một bộ công cụ AI toàn diện:
- **STT**: Chuyển giọng nói sang văn bản kèm phân tích cảm xúc.
- **LLM**: Chatbot thông minh, hỗ trợ đa ngôn ngữ (ưu tiên tiếng Việt).
- **Tools**: Tự động nhận diện và trích xuất tham số cho các hàm hệ thống.
- **Embeddings**: Chuyển văn bản và hình ảnh sang vector cho RAG.
- **Vision**: "Nhìn" và hiểu nội dung hình ảnh.
- **Files**: "Đọc" và xử lý nội dung từ tài liệu văn phòng/dữ liệu.

---
*Ghi chú: Luôn đảm bảo cài đặt đầy đủ các thư viện phụ thuộc (`pypdf`, `python-docx`, etc.) trước khi sử dụng các tính năng file.*
