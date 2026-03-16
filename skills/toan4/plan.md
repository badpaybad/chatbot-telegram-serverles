# Kế hoạch phát triển Skill toan4 (Toán Lớp 4)

## Mục tiêu
Tạo ra một quy trình (skill) tự động nhận diện bài toán lớp 4 từ ảnh chụp, sau đó sinh ra một minigame HTML5 tương tác cho học sinh thực hành và giải bài toán đó, đặt trong một thư mục mang tên của bức ảnh.

## Ý tưởng cốt lõi
1. **Phân tích hình ảnh (Image Analysis / Vision):**
   - Đọc và trích xuất nội dung văn bản, các số liệu, phép tính, và ý nghĩa của bài toán từ bức ảnh mà người dùng cung cấp. Có thể lấy ra một phần hình ảnh để minh họa
   - Phân loại dạng toán lớp 4 (ví dụ: phân số, chu vi diện tích, toán đố chữ, v.v.).

2. **Thiết kế Game (Game Design):**
   - **Giao diện:** Xây dựng bằng HTML5, CSS với màu sắc tươi sáng, hình ảnh sinh động, phù hợp độ tuổi học sinh lớp 4, gây hứng thú học tập. Bổ sung **Khu vực minh họa trực quan** (như sơ đồ đoạn thẳng, hình khối, bảng biểu) để cụ thể hóa dữ kiện bài toán.
   - **Tương tác:** Kéo thả, điền số, chọn đáp án đúng, hoặc click chọn đối tượng. Tích hợp phương pháp **Dẫn dắt từng bước (Scaffolding)** đối với bài toán nhiều lời giải (gợi ý học sinh giải quyết bước 1 trước, ví dụ: tìm tổng số phần, sau đó làm bước 2).
   - **Gợi ý và Hướng dẫn (Hints & Instructions):** Áp dụng cơ chế **Gợi ý tăng dần (Progressive Hints)**:
     + *Gợi ý 1:* Trợ giúp về mặt khái niệm (Nhắc lại công thức, định nghĩa).
     + *Gợi ý 2:* Hướng tư duy (Nên làm phép tính gì trước, liên hệ thực tế).
     + *Gợi ý 3:* Hướng dẫn chi tiết bước giải như giáo án, mang tính giảng giải cách làm cho học sinh
   
   - **Cơ chế phản hồi học tập (Feedback Mechanism):**
     - *Khi làm sai:* Không báo lỗi một cách tiêu cực. Hệ thống sẽ có nhân vật hoặc hộp thoại đưa ra các "Gợi ý suy nghĩ" theo từng cấp độ đã nêu ở trên.
     - *Khi làm đúng:* Có báo động hiệu ứng chúc mừng sinh động (pháo hoa, âm thanh), khen ngợi ("Giỏi quá!", "Tuyệt vời!") và cung cấp **Lời giải chi tiết chuẩn mô phạm lớp 4** (Tóm tắt, Lời giải, Phép tính, Đáp số) để học sinh đối chiếu cách trình bày tốt nhất.

3. **Cấu trúc lưu trữ Game:**
   - Mỗi lần thực thi AI nhận được bức ảnh và yêu cầu dùng `skill toan4`, hệ thống sẽ tạo ra một folder mới có tên trùng với tên file bức ảnh (không bao gồm phần mở rộng).
   - Folder này chứa các file `index.html`, `style.css`, và `script.js` cấu thành ứng dụng web hoàn chỉnh, có thể chạy trực tiếp trên trình duyệt.

## Quy trình làm việc của Hệ thống với Skill này
- **Bước 1:** Lấy URL/Path của ảnh truyền vào từ người dùng.
- **Bước 2:** AI phân tích đề toán, lập kịch bản sư phạm cho đề đó (Đâu là đáp án? Đâu là các lỗi dễ mắc? Lời khuyên là gì? Có gợi ý hướng dẫn hoàn thành và giải thích ý nghĩa bài tập không?).
- **Bước 3:** AI sinh mã nguồn HTML/CSS/JS cho game tương ứng với kịch bản sư phạm.
- **Bước 4:** Lưu toàn bộ mã nguồn vào một folder độc lập dành riêng cho minh họa của bức ảnh đó. Nếu không thể minh họa bằng html thì có thể cất ảnh trực tiếp để minh họa câu hỏi và câu trả lời 
- **Bước 5:** Code Python thực hiện deploy qua SFTP **bắt buộc** phải import các cấu hình từ `config_dunp.py` (bao gồm `sftp_host, sftp_port, sftp_username, sftp_password`) để thực hiện kết nối SSH/SFTP. **Tuyệt đối không copy các giá trị này vào file code sinh ra** để tránh nguy cơ bảo mật lộ mật khẩu. Cần dùng script dùng chung `skills/toan4/utils/deploy_game.py {tên tương đương với ảnh}` để đẩy thư mục game vừa tạo lên server vào folder `/work/nginxstaticfile/games/maths/{tên tương đương với ảnh}`. Có thể dùng luôn folder venv mà không cần chạy sandbox. *Nếu quá trình deploy bị treo hoặc kéo dài, AI cần chạy command dưới dạng background và kiểm tra log bằng command_status hoặc set timeout hợp lý để tránh block quá trình làm việc.*
- **Bước 6:** Thông báo cho người dùng đường dẫn để mở web lên chơi thử tại: `https://static.airobotics.vn/games/maths/{tên tương đương với ảnh}/`
