# Các bước thực thi tạo Game Toán Lớp 4 từ Ảnh (Skill toan4)

Khi được yêu cầu sử dụng `skill toan4` với một hình ảnh đầu vào, hệ thống AI sẽ thực hiện các bước sau:

- [ ] **Task 1: Xử lý và phân tích ảnh đầu vào**
  - Đọc hình ảnh được cung cấp.
  - Phân tích và trích xuất nội dung đề toán lớp 4 (các con số, phép tính, câu hỏi).
  - Trích xuất tên file ảnh (ví dụ: `bai1.png` -> tên bài: `bai1`).

- [ ] **Task 2: Lên kịch bản sư phạm cho bài toán**
  - Xác định dạng toán (Tổng-Tỉ, Tổng-Hiệu, Phân số, Hình học, ...).
  - Phân tích các lỗi sai phổ biến học sinh hay gặp và mức độ hiểu của học sinh ở dạng này.
  - Thiết kế phương pháp **Chia nhỏ câu hỏi (Scaffolding)** nếu là bài toán lời văn phức tạp.
  - Lên ý tưởng để **minh họa trực quan dữ kiện bài toán** (Sơ đồ đoạn thẳng, đồ thị, hình ảnh trực quan).
  - Soạn sẵn kịch bản **Gợi ý tăng dần (Progressive hints)** theo 2-3 cấp độ.
  - Viết sẵn đoạn text **Bài giải chi tiết chuẩn mô phạm lớp 4** (Lời giải, Phép tính, Đáp số) để hiển thị lúc sau cùng.

- [ ] **Task 3: Thiết kế Giao diện và Trải nghiệm (UI/UX)**
  - Xác định các thành phần của minigame HTML5 (Khu vực đọc đề, Khu vực **Minh họa trực quan/Sơ đồ**, Khu vực tương tác, Nhân vật hỗ trợ).
  - Hình dung CSS animation, màu sắc sinh động, font chữ thân thiện.

- [ ] **Task 4: Viết mã nguồn Game (HTML/CSS/JS)**
  - Sinh file `index.html` với cấu trúc DOM phù hợp.
  - Sinh file `style.css` tập trung vào đồ họa cuốn hút, trực quan. Đặc biệt chú ý CSS cho **Sơ đồ/Hình ảnh minh họa**.
  - Sinh file `script.js` với logic:
    - Đoán nhận thao tác và kiểm tra kết quả theo từng bước bài giải.
    - Hiển thị gợi ý **tăng dần cấp độ** nếu làm sai nhiều lần.
    - Hiển thị chúc mừng (pháo hoa, khen ngợi) và **bảng Lời giải chi tiết** khi làm đúng.

- [ ] **Task 5: Tạo Thư mục và Lưu File**
  - Xác định thư mục sẽ lưu game (ví dụ tạo 1 folder con bằng tên ảnh ở một nơi xác định).
  - Lưu các file `index.html`, `style.css`, `script.js` vào thư mục này.

- [ ] **Task 6: Triển khai lên Server qua SFTP**
  - Các file Python code sinh ra để sử dụng SSH hoặc SFTP **bắt buộc** phải import các cấu hình cần thiết từ `config_dunp.py` (bao gồm các key: `sftp_host`, `sftp_port`, `sftp_username`, `sftp_password`).
  - **Tuyệt đối không copy/hardcode** các value này vào các file khác để tránh nguy cơ bảo mật bị lộ mật khẩu.
  - Chạy script dùng chung `python skills/toan4/utils/deploy_game.py {tên tương đương với ảnh}` để đẩy folder game vừa tạo lên server thay vì sinh code mới. *Lưu ý: Quá trình đẩy file qua SFTP có thể bị treo hoặc chạy lâu do nghẽn mạng. AI nên cấu hình thời gian chờ WaitMsBeforeAsync thấp, cho chạy ngầm và dùng command_status để kiểm tra kết quả.*
  - Vị trí đường dẫn đích trên server: `/work/nginxstaticfile/games/maths/{tên tương đương với ảnh}`.
  - Có thể dùng luôn folder venv mà không cần chạy sandbox
  
- [ ] **Task 7: Bàn giao**
  - Trả về thông báo thành công và cung cấp đường dẫn web trên server để người dùng bắt đầu trải nghiệm trò chơi: `https://static.airobotics.vn/games/maths/{tên tương đương với ảnh}/`
