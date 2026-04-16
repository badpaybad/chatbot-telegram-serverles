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

# Tối ưu cho iGPU 780M (RDNA3/gfx1103) trên ROCm 6.2
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"
os.environ["HSA_ENABLE_SDMA"] = "1"      # Tăng tốc truyền dữ liệu CPU <-> iGPU
os.environ["MIOPEN_DEBUG_DISABLE_FIND_DB"] = "1" # Bỏ qua bước tìm kiếm DB MIOpen chậm chạp
os.environ["ROCM_RELAXED_ASIC_CHECK"] = "1"      # Tăng tính tương thích cho Mobile APU

# Tối ưu hóa bộ nhớ cho iGPU 16GB UMA
os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "0" # Tắt JIT Compilation để tránh tốn RAM/VRAM lúc khởi động
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:128"

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

## 5. Lưu ý về hiệu năng và Tối ưu

### 5.1. Khắc phục tình trạng chạy chậm
Nếu model load rất chậm hoặc sinh text chậm (lag), hãy kiểm tra các yếu tố sau:

- **Áp lực bộ nhớ (RAM/Swap)**: iGPU dùng chung RAM hệ thống. Nếu RAM đầy, Linux sẽ đẩy dữ liệu vào **Swap (Disk)**, khiến tốc độ giảm hàng chục lần.
    - **Cách xử lý**: Đóng các trình duyệt (Chrome/Firefox) hoặc các ứng dụng nặng để giải phóng ít nhất 16GB RAM trống trước khi chạy.
- **Compute Dtype**: Hãy sử dụng `float16` thay vì `bfloat16`. Thử nghiệm cho thấy card RDNA3 (780M) xử lý FP16 nhanh hơn đáng kể trong các phiên bản ROCm hiện tại.
- **UMA Buffer**: Phải vào BIOS cài đặt **UMA Frame Buffer Size** lên mức cao nhất (khuyên dùng **8GB** hoặc **16GB** nếu máy có 32GB RAM). Nếu để 2GB hoặc 4GB, model lớn sẽ bị lỗi hoặc chạy cực chậm.

### 5.2. Quantization
Nên dùng NF4 (4-bit) để mô hình khớp hoàn toàn vào VRAM (UMA), tránh việc offload từng phần sang CPU sẽ làm giảm tốc độ xử lý multimodal (Audio/Image).

### 5.4. Tối ưu tốc độ Load model (ROCm Specific)
Khi load model lớn (như Gemma 4), việc thực hiện quantization on-the-fly (nén sang 4-bit lúc nạp) tiêu tốn rất nhiều tài nguyên CPU. Để tối ưu:

- **Dùng Float16 làm Base**: Luôn truyền `torch_dtype=torch.float16` vào `from_pretrained`. Điều này giúp bộ nạp không phải chuyển đổi từ FP32 sang FP16 trước khi nén sang 4-bit.
- **Tắt Offload 8-bit**: Nếu dùng 4-bit (NF4), hãy đảm bảo **không** bật `llm_int8_enable_fp32_cpu_offload`. Biến này chỉ dành cho 8-bit và có thể gây xung đột hoặc làm chậm quá trình nạp 4-bit.
- **SDPA (Scaled Dot-Product Attention)**: Sử dụng `attn_implementation="sdpa"` để tận dụng các kernel tối ưu mặc định của PyTorch, giúp tăng tốc cả bước nạp và bước sinh text.
- **Dọn dẹp bộ nhớ**: Sau khi nạp xong, hãy gọi `gc.collect()` và `torch.cuda.empty_cache()` để giải phóng các buffer trung gian.

Ví dụ cấu hình nạp tối ưu trong `manager.py`:
```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)

model = AutoModelForMultimodalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto",
    quantization_config=quantization_config,
    low_cpu_mem_usage=True,
    attn_implementation="sdpa"
)
### 5.5. Chuyển đổi giữa các phiên bản model (E2B vs E4B)
Dòng Gemma 4 cung cấp nhiều kích thước khác nhau để cân bằng giữa chất lượng và tốc độ:

- **E2B (Effective 2B)**: Nhẹ nhất, dung lượng 4-bit chỉ ~3GB. Tốc độ cực nhanh, phù hợp cho phản hồi thời gian thực.
- **E4B (Effective 4B)**: Cân bằng nhất, dung lượng 4-bit ~4.5GB (nhưng file gốc 15GB). Chất lượng suy luận cao hơn E2B khoảng 10-15%.

Để chuyển đổi, bạn chỉ cần thay đổi tham số `model_id` trong class `Gemma4Manager` tại file `manager.py`:

```python
# Trong gemma4/manager.py
def __new__(cls, model_id: str = "google/gemma-4-e2b-it"): # Đổi thành e4b-it nếu muốn chất lượng cao hơn
```

Hệ thống sẽ tự động tạo thư mục riêng trong `gemma4/model/` cho từng phiên bản, tránh việc tải đè dữ liệu.

## 6. Theo dõi Bộ nhớ (VRAM & GTT)

Đối với iGPU, bộ nhớ được chia thành **VRAM (UMA)** (phần RAM hệ thống được BIOS cấp cứng cho GPU) và **GTT (Shared)** (phần RAM hệ thống GPU có thể mượn thêm).

### 6.1. Kiểm tra nhanh qua Terminal
Dùng lệnh sau để xem dung lượng đang dùng (đơn vị MB):
```bash
# Xem VRAM (UMA)
echo "VRAM Used: $(cat /sys/class/drm/card1/device/mem_info_vram_used | awk '{print $1/1024/1024}') MB"
echo "VRAM Total: $(cat /sys/class/drm/card1/device/mem_info_vram_total | awk '{print $1/1024/1024}') MB"

# Xem GTT (Bộ nhớ dùng chung)
echo "GTT Used: $(cat /sys/class/drm/card1/device/mem_info_gtt_used | awk '{print $1/1024/1024}') MB"
echo "GTT Total: $(cat /sys/class/drm/card1/device/mem_info_gtt_total | awk '{print $1/1024/1024}') MB"
```

### 6.2. Công cụ giám sát trực quan
Sử dụng **radeontop** để xem biểu đồ sử dụng thời gian thực:
```bash
sudo radeontop
```

Hoặc dùng **rocm-smi** với tuỳ chọn chi tiết:
```bash
rocm-smi --showmeminfo vram gtt
```
Nếu bạn thấy `VRAM Used` đã gần bằng `VRAM Total`, model sẽ bắt đầu tràn sang GTT hoặc Swap, gây ra hiện tượng lag nghiêm trọng hoặc lỗi Load model.
