# Hướng dẫn Chạy Gemma 4 trên AMD iGPU 780M (ROCm)

Tài liệu này hướng dẫn cách cấu hình môi trường Linux để tận dụng GPU tích hợp AMD Radeon 780M (kiến trúc RDNA 3) giúp tăng tốc xử lý cho mô hình Gemma 4.

## 1. Yêu cầu hệ thống
- **Hệ điều hành**: Linux (Ubuntu 22.04+ khuyên dùng).
- **Driver**: Đã cài đặt ROCm (phiên bản 6.0 hoặc mới hơn).
- **Phần cứng**: AMD Ryzen có iGPU 780M (Phoenix/Hawk Point).
- **BIOS**: Đã cấu hình "UMA Frame Buffer Size" tối thiểu 4GB (khuyên dùng 8GB).

## 2. Các bước cài đặt môi trường

### Bước 0: Cấp quyền truy cập GPU (Quan trọng)
ROCm cần quyền truy cập vào các file thiết bị. Hãy chạy lệnh sau và **khởi động lại máy (hoặc Logout/Login)**:
```bash
sudo usermod -aG render $USER
sudo usermod -aG video $USER
```

### Bước 1: Gỡ bộ PyTorch cũ (nếu có)
```bash
./venv/bin/pip uninstall -y torch torchvision torchaudio bitsandbytes
```

### Bước 2: Cài đặt PyTorch hỗ trợ ROCm
Cài đặt bản build chính thức từ PyTorch dành cho ROCm (ví dụ bản 6.2):
```bash
./venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
```

### Bước 3: Cài đặt bitsandbytes hỗ trợ ROCm
Từ phiên bản 0.49.2, bitsandbytes đã hỗ trợ chính thức ROCm:
```bash
./venv/bin/pip install bitsandbytes
```

## 3. Cấu hình mã nguồn (Quan trọng)

Vì iGPU 780M (gfx1102/1103) không phải là card đồ họa rời chuyên dụng và một số hệ thống có thể thiếu các công cụ như `rocminfo`, bạn cần thực hiện các bước sau:

### 3.1. Tạo shim cho rocminfo (nếu thiếu)
Nếu gặp lỗi `Could not detect ROCm GPU architecture: 'rocminfo'`, hãy tạo một file shim giả lập `rocminfo` trong thư mục `gemma4/`:

**File: `gemma4/rocminfo`**
```bash
#!/bin/bash
# Shim giả lập đầu ra cho bitsandbytes
echo "ROCm System Management Interface shim"
echo "Name:                    gfx1102"
echo "Wavefront Size:          32(0x20)"
```
Đảm bảo file có quyền thực thi: `chmod +x gemma4/rocminfo`.

### 3.2. Thiết lập biến môi trường (BẮT BUỘC)
Trong mã nguồn (ví dụ `gemma4/manager.py`, `program.py`), bạn **PHẢI** đặt các biến này ở ngay dòng đầu tiên, trước khi bất kỳ thư viện nào (như `torch` hoặc `bitsandbytes`) được nạp:

```python
import os
import sys

# Ép kiểu kiến trúc về gfx1100 (tương thích nhất cho RDNA3/780M trên ROCm 6.2)
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Thêm thư mục gemma4 vào PATH để nhận diện shim rocminfo
current_dir = os.path.dirname(os.path.abspath(__file__))
gemma4_dir = os.path.join(current_dir, "gemma4")
os.environ["PATH"] = gemma4_dir + os.pathsep + os.environ.get("PATH", "")

# (Tùy chọn) Chỉ định LD_LIBRARY_PATH tới thư viện ROCm đi kèm torch
# Thường nằm trong venv/lib/python3.12/site-packages/torch/lib
```

Các cấu hình này đã được cập nhật đồng bộ trong `gemma4/manager.py`, `gemma4lib.py` và `gemma4/program.py`.

## 4. Kiểm tra hoạt động
Chạy script kiểm tra sau:
```bash
./venv/bin/python test/test_rocm_check.py
```

Nếu kết quả trả về `CUDA (ROCm) Available: True` và tên thiết bị là `AMD Radeon 780M`, hệ thống đã sẵn sàng.

## 5. Lưu ý về hiệu năng
- **Quantization**: Nên dùng NF4 hoặc INT4 để mô hình khớp hoàn toàn vào VRAM (UMA).
- **Nhiệt độ**: Khi chạy Full Load, iGPU sẽ toả nhiệt chung với CPU, hãy đảm bảo tản nhiệt ổn định.
