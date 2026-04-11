## 1. Phân tích các Module hiện có (Cập nhật 6)

*   **`manager.py`:** Hiện đã hỗ trợ nhận danh sách `images_list` và `audio_list` trực tiếp (objects), tối ưu cho API.
*   **`files.py` (RAG Core):** Đây là module quan trọng nhất để đáp ứng yêu cầu mới. Nó hỗ trợ đọc: PDF, DOCX, XLSX, PPTX, CSV, TXT. Chúng ta sẽ tích hợp module này vào API để tự động trích xuất nội dung văn bản từ các file không phải media và đưa vào ngữ cảnh của LLM.
*   **`tools.py`:** Sẽ được mở rộng để hỗ trợ các "file generation tools". Ví dụ: một tool để tạo file CSV hoặc PDF từ dữ liệu mà LLM trích xuất được.

## 2. Thiết kế `program.py` (Cập nhật 6)

`program.py` sẽ được đặt trong folder `gemma4/` để đảm bảo tính đóng gói.

### Các tính năng mới:
1.  **Xử lý File Đa định dạng (Omni-File Handling):**
    *   **Media (Image/Audio/Video):** Tiếp tục sử dụng `Gemma4Manager` để phân tích trực tiếp. Với Video, chúng ta sẽ thực hiện lấy mẫu khung hình (frame sampling) và trích xuất âm thanh để model xử lý.
    *   **Documents (PDF, Office, Text):** Sử dụng `files.py` để "đọc" nội dung, sau đó chèn vào prompt dưới dạng: `Nội dung file [tên file]: ...`.
2.  **Tự động Upload/Lưu tạm:** Các file gửi qua `inline_data` (Base64) sẽ được lưu tạm vào thư mục `gemma4/temp/` nếu cần xử lý phức tạp hoặc để phục vụ RAG.
3.  **Hỗ trợ Tạo file và Trả về Download URL:**
    *   Thêm folder `gemma4/output/` để lưu các file do AI tạo ra.
    *   Sử dụng `fastapi.responses.FileResponse` để triển khai endpoint `GET /download/{filename}`.
    *   AI sẽ trả về một chuỗi có định dạng: `File của bạn đã được tạo tại: http://<server_url>/download/<filename>`.

### Luồng xử lý file đính kèm:
1.  Nhận request chứa danh sách `parts`.
2.  Phân loại `Part`:
    *   Nếu là Image/Audio: Gom vào list để gửi `manager.generate`.
    *   Nếu là Document: Gọi hàm từ `files.py` để lấy text, cộng dồn vào prompt.
    *   Nếu là Video: (Dự kiến) Dùng `librosa` trích xuất audio và lấy mẫu ảnh.
3.  Gửi prompt tổng hợp (Text + Doc content) kèm Media list vào LLM.

## 3. Các bước thực hiện (Updated Plan)

1.  **Cấu trúc lại `gemma4/program.py`**: Di chuyển từ root vào folder `gemma4/`, cập nhật các đường dẫn import.
2.  **Tích hợp `files.py`**: Viết logic tự động nhận diện MIME type và gọi hàm parse tương ứng trong `program.py`.
3.  **Xây dựng cơ chế File Generation**:
    *   Tạo tool mẫu (ví dụ: `create_report_file`) để LLM có thể gọi khi cần tạo file.
    *   Viết endpoint download.
4.  **Hoàn thiện Video Interaction**: Nghiên cứu cách lấy mẫu frame đơn giản nhất mà không cần quá nhiều thư viện nặng.
5.  **Xác minh**: Chạy test với nhiều loại file khác nhau (PDF đính kèm, ảnh đính kèm đồng thời).
