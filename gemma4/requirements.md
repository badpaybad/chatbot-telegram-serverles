code python để dùng gemma4 trên cpu với RAM 16GB, cung cấp các chức năng sau
code dùng huggingface không dùng ollama hay các wrapper khác , cần tạo trong folder gemma4 để chạy, có thể dùng venv hiện tại và cần import tất cả các const từ file config.py
- speech to text, đưa 1 file audio lấy ra text 
- các hàm dùng cho tạo text từ text đầu vào
- hàm dùng như tool call, định nghĩa các tên hàm đầu vào của hàm và trả về kết quả là các hàm có thể được dùng với score để đánh giá mức độ phù hợp của kết quả với yêu cầu

**bắt buộc** toàn bộ đầu trả ra của LLM cần là tiếng việt, tất cả đều dùng model google/gemma-4-e4b-it, kiểm tra nếu hỗ trợ gpu thì dùng gpu không thì dùng cpu

**cập nhật 1**
bổ xung embedding text dùng gemma4

tổng hợp code ở folder gemma4 thành 1 file tailieu.md