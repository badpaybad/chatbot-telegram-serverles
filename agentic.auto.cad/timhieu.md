# Tìm hiểu về Agentic Auto CAD

Dưới đây là các ghi chú về việc triển khai hệ thống vẽ và sửa file AutoCAD (DXF) trên Ubuntu 24.04 sử dụng IDE Antigravity.

## Công cụ sử dụng
- **ezdxf**: Thư viện Python mạnh mẽ để đọc, ghi và chỉnh sửa các file DXF (AutoCAD Drawing Exchange Format). DXF là định dạng tiêu chuẩn để trao đổi dữ liệu CAD.
- **Python 3.12+** (trên Ubuntu 24.04).

## Cấu trúc thư mục (Framework)
Đã thiết lập cấu trúc thư mục tại `agentic.auto.cad/` như sau:
- `yeucau.md`: File yêu cầu gốc của người dùng.
- `timhieu.md`: File này, dùng để ghi lại quá trình tìm hiểu và hướng dẫn.
- `my_requirements/`: Nơi người dùng đặt các yêu cầu cụ thể (text/markdown).
- `references/`: Nơi đặt các file tham khảo (ví dụ: file DXF mẫu, hình ảnh sơ đồ).
- `requested_files/`: Nơi đặt các file đầu vào cần xử lý.
- `toolcall_samples/`: Các mẫu code Python sử dụng `ezdxf` để thực hiện các tác vụ cụ thể. AI sẽ tham khảo các mẫu này để viết code xử lý.
- `processing/`: Thư mục chứa các file đang trong quá trình xử lý/chỉnh sửa.
- `done/`: Thư mục chứa các file đã hoàn thành.

## Quy trình làm việc của AI
1. Khi có yêu cầu mới tại chat của IDE Antigravity, AI sẽ đọc nội dung trong `my_requirements/` và tham khảo các file trong `references/`.
2. AI tìm kiếm các đoạn code mẫu trong `toolcall_samples/` để biết cách thực hiện yêu cầu.
3. AI thực hiện chỉnh sửa/tạo mới file CAD (thường là định dạng DXF) và lưu vào `agentic.auto.cad/processing/`.
4. Sau khi người dùng xác nhận kết quả qua chat hoặc kiểm tra file, file sẽ được chuyển sang `agentic.auto.cad/done/`.

## Các mẫu toolcall (Code Samples)
Đã tạo các mẫu code cơ bản tại `agentic.auto.cad/toolcall_samples/`:
- `create_line.py`: Cách khởi tạo 1 file DXF mới, tạo layer và vẽ đường thẳng.
- `edit_dxf.py`: Cách đọc 1 file DXF hiện có, tìm kiếm các thực thể (entities) và chỉnh sửa thuộc tính của chúng (ví dụ: đổi màu).

## Cách chạy các script
Để đảm bảo đúng môi trường và cấu hình, các script nên được chạy bằng python trong venv và đi kèm tham số `config_dunp`:
```bash
./venv/bin/python agentic.auto.cad/toolcall_samples/create_line.py config_dunp
```

## Các lưu ý kỹ thuật
- **DXF version**: Mặc định dùng `R2010` để có độ tương thích cao nhất với các phần mềm CAD cũ và mới.
- **Layers**: Luôn sử dụng layer để quản lý các nhóm thực thể khác nhau.
- **Coordinates**: Hệ tọa độ mặc định là (x, y, z). Nếu vẽ 2D, z mặc định là 0.
- **Màu sắc (Colors)**: ezdxf sử dụng bảng màu AutoCAD Color Index (ACI). Ví dụ: 1=Red, 2=Yellow, 3=Green, 4=Cyan, 5=Blue, 6=Magenta, 7=White/Black.

