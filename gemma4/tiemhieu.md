# Tìm hiểu và Thiết kế Gemma 4 Gemini-Compatible API

Mục tiêu: Xây dựng một API server sử dụng FastAPI cho mô hình Gemma 4 Omni, tuân thủ hoàn toàn đặc tả **Google Gemini API REST (v1beta)**. Điều này cho phép sử dụng các SDK chính thức của Gemini để giao tiếp với mô hình chạy tại local.

## 1. Kiến trúc API (v1beta)

Hệ thống được thiết kế để khớp với các endpoint chính của Gemini:

-   **`POST /v1beta/models/{model}:generateContent`**: Sinh nội dung (Text, Image, Audio, Document).
-   **`POST /v1beta/models/{model}:streamGenerateContent`**: Sinh nội dung dạng streaming (Server-Sent Events/NDJSON).
-   **`POST /v1beta/files`**: Upload file để sử dụng lâu dài qua `file_data`.
-   **`GET /v1beta/files/{file_id}`**: Lấy thông tin metadata của file.
-   **`DELETE /v1beta/files/{file_id}`**: Xóa file.

## 2. Các Tính năng Nâng cao

### Xử lý Đa phương thức (Multi-modal)
-   **`inline_data`**: Gửi dữ liệu base64 trực tiếp trong request (tốt cho ảnh nhỏ/âm thanh ngắn).
-   **`file_data`**: Tham chiếu đến file đã upload qua endpoint `/v1beta/files` (tối ưu cho video hoặc tài liệu lớn).
-   **Document Processing**: Tự động nhận diện các file PDF, DOCX, XLSX, CSV... và trích xuất nội dung văn bản để đưa vào ngữ cảnh của LLM thông qua module `gemma4.files`.

### Tool Calling (Function Calling)
API hỗ trợ định dạng `tools` chuẩn của Gemini. 
-   Hệ thống có sẵn tool `generate_file` để LLM có thể tự động tạo file và trả về URL download cho người dùng.
-   Hỗ trợ `function_call` và `function_response` trong lịch sử hội thoại (Content parts).

### Cấu hình Sinh (Generation Config)
Hỗ trợ các tham số:
-   `temperature`, `topP`, `topK`.
-   `maxOutputTokens`.
-   `stopSequences`.
-   `thinkingConfig` (Dành cho các tác vụ cần suy luận sâu).

## 3. Luồng Xử lý Dữ liệu

1.  **Nhận Request**: Validate theo schema `GenerateContentRequest`.
2.  **Tiền xử lý Parts**:
    -   Nếu là `inline_data`: Decode base64.
    -   Nếu là `file_data`: Tìm kiếm trong `FILES_STORE` local.
    -   Nếu là Documents không phải Media: Gọi `read_file_content` từ `gemma4.files` và append text vào prompt.
3.  **Gemma 4 Manager**: Chuyển đổi sang format `messages` của mô hình Gemma 4 và thực hiện `generate`.
4.  **Hậu xử lý Tool Call**: Nếu kết quả sinh ra khớp với một khai báo tool, API sẽ trả về part `function_call` thay vì text.

## 4. Hướng dẫn Sử dụng (Ví dụ)

### Upload File
```bash
curl -X POST "http://localhost:8000/v1beta/files" \
  -F "file=@tailieu.pdf"
```
Response sẽ trả về một `uri` (ví dụ: `http://.../v1beta/files/file-123`).

### Chat với File đã upload
```bash
curl -X POST "http://localhost:8000/v1beta/models/gemma-4:generateContent" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"text": "Tóm tắt file này cho tôi"},
        {"file_data": {"file_uri": "http://.../v1beta/files/file-123"}}
      ]
    }]
  }'
```

### Download File do AI tạo
AI có thể gọi tool `generate_file` và trả về link download tại `/download/{filename}`.
