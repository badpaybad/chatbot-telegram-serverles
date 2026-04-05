code python để dùng gemma4 trên cpu với RAM 16GB, cung cấp các chức năng sau
code dùng huggingface không dùng ollama hay các wrapper khác , cần tạo trong folder gemma4 để chạy, có thể dùng venv hiện tại và cần import tất cả các const từ file config.py
- speech to text, đưa 1 file audio lấy ra text 
- các hàm dùng cho tạo text từ text đầu vào
- hàm dùng như tool call, định nghĩa các tên hàm đầu vào của hàm và trả về kết quả là các hàm có thể được dùng với score để đánh giá mức độ phù hợp của kết quả với yêu cầu

**bắt buộc** toàn bộ đầu trả ra của LLM cần là tiếng việt, tất cả đều dùng model google/gemma-4-e4b-it, kiểm tra nếu hỗ trợ gpu thì dùng gpu không thì dùng cpu

**cập nhật 1**
bổ xung embedding text dùng gemma4

tổng hợp code ở folder gemma4 thành 1 file tailieu.md

**cập nhật 2**

bổ xung embedding image dùng gemma4

**cập nhật 3**
dùng gemma4 để 
    - bổ xung hàm lấy mô tả tử ảnh đưa vào
    - bổ xung thêm việc đọc các file (pdf, xlsx, txt, csv, docx, pptx, ...) có kèm đưa prompt vào để thao tác file 
    - bổ xung thêm hàm thao tác với file ảnh (jpeg, png , bitmap ...) có kèm đưa prompt vào để thao thác file 

**cập nhật 4**

bổ xung dùng kokoro_onnx để text to speech cho tiếng Việt

**cập nhật 5**

sửa code gemma4/download_model.py để kiểm tra nếu chưa có thì 

    download model kokoro_onnx vào folder gemma4/model/kokoro
    download model google/gemma-4-e4b-it vào folder gemma4/model/gemma-4-e4b-it
