# Tài liệu và Tổng hợp Code Gemma 4 (Cập nhật 5)

File này tổng hợp toàn bộ mã nguồn của module `gemma4`, bao gồm STT, LLM, Tool Call, Embedding, Vision, File Processing và TTS.

## 1. Cấu trúc thư mục
```
gemma4/
├── __init__.py      # Khởi tạo package và export API
├── manager.py       # Quản lý Singleton Model & Processor (Tự động tải model)
├── llm.py           # Text Generation
├── stt.py           # Speech to Text
├── tools.py         # Tool Call Scoring
├── embeddings.py    # Text/Image Embedding
├── vision.py        # Phân tích hình ảnh
├── files.py         # Xử lý file đa định dạng
├── tts.py           # Chuyển văn bản thành giọng nói (Kokoro-ONNX)
├── download_model.py # Script hỗ trợ tải model thủ công [NEW/UPDATED]
└── requirements.md  # Yêu cầu hệ thống
```

---

## 2. Các chức năng tự động (Cập nhật 5)

### 2.1. Tự động kiểm tra và tải Model
Module `gemma4` hiện đã hỗ trợ tự động kiểm tra sự tồn tại của các model cần thiết khi khởi tạo `Gemma4Manager`.

- **Gemma 4**: Kiểm tra tại HF Cache hoặc thư mục `gemma4/model/`. Nếu thiếu, sẽ tự động tải từ `google/gemma-4-e4b-it`.
- **Kokoro ONNX**: Kiểm tra tại `gemma4/model/kokoro/`. Nếu thiếu, sẽ tự động tải model và voices.

### 2.2. Text-to-Speech tiếng Việt (`gemma4/tts.py`)
Sử dụng Kokoro-ONNX để chuyển đổi văn bản tiếng Việt thành file âm thanh.

```python
from gemma4.tts import save_tts

# Hệ thống sẽ tự động tải model nếu bạn chưa chạy script download!
output_file = save_tts("Chào bạn, tôi là trợ lý AI.", "hello.wav")
```

---

## 3. Cài đặt thủ công (Tùy chọn)

Nếu bạn muốn chuẩn bị assets trước khi chạy ứng dụng chính:
```bash
python gemma4/download_model.py
```

---

## 4. Danh sách API toàn diện
- **`transcribe_audio(audio_path)`**: STT.
- **`generate_text(prompt)`**: LLM Chat.
- **`get_text_embedding(text)`**: Text vector.
- **`get_image_embedding(image_path)`**: Image vector.
- **`describe_image(image_path)`**: Mô tả ảnh.
- **`query_image(image_path, prompt)`**: Hỏi đáp ảnh.
- **`process_file_with_prompt(file_path, prompt)`**: Phân tích tài liệu PDF/Excel.
- **`save_tts(text, filename)`**: TTS tiếng Việt.
