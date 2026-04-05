# Tài liệu và Tổng hợp Code Gemma 4 (Cập nhật 4)

File này tổng hợp toàn bộ mã nguồn của module `gemma4`, bao gồm STT, LLM, Tool Call, Embedding, Vision, File Processing và **TTS (Text-to-Speech)**.

## 1. Cấu trúc thư mục
```
gemma4/
├── __init__.py      # Khởi tạo package và export API
├── manager.py       # Quản lý Singleton Model & Processor
├── llm.py           # Text Generation
├── stt.py           # Speech to Text
├── tools.py         # Tool Call Scoring
├── embeddings.py    # Text/Image Embedding
├── vision.py        # Phân tích hình ảnh
├── files.py         # Xử lý file đa định dạng
├── tts.py           # CHUYỂN VĂN BẢN THÀNH GIỌNG NÓI (KOKORO-ONNX) [NEW]
├── download_kokoro.py # Tải model và voice cho TTS [NEW]
└── requirements.md  # Yêu cầu hệ thống
```

---

## 2. Các chức năng mới (Cập nhật 4)

### 2.1. Text-to-Speech tiếng Việt (`gemma4/tts.py`)
Sử dụng Kokoro-ONNX để chuyển đổi văn bản tiếng Việt thành file âm thanh chất lượng cao.

```python
from gemma4.tts import save_tts

# Chuyển văn bản thành giọng nói và lưu vào file output.wav
output_file = save_tts("Chào bạn, tôi có thể giúp gì cho bạn?", "hello.wav")
print(f"File âm thanh đã được lưu tại: {output_file}")
```

---

## 3. Cài đặt và chuẩn bị Assets

Trước khi sử dụng TTS, cần chạy script tải model:
```bash
python gemma4/download_kokoro.py
```
Model mặc định sẽ được lưu tại `gemma4/model/kokoro/`.

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
