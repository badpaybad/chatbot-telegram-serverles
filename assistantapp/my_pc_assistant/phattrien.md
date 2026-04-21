# Kế hoạch phát triển ứng dụng My PC Assistant (Cập nhật liên tục)

Dựa trên các yêu cầu trong `yeucau.md` và các tệp thiết kế trong thư mục `design`, tôi đề xuất kế hoạch triển khai ứng dụng Flutter như sau.

## Tổng quan thiết kế
Ứng dụng sẽ có giao diện hiện đại, sử dụng bảng màu tím/xanh đậm làm chủ đạo, với các bo góc mềm mại và các thành phần UI cao cấp (glassmorphism nhẹ, gradient).

### Màu sắc chủ đạo:
- **Primary**: #3F37C9 (Tím đậm)
- **Secondary**: #4CC9F0 (Xanh cyan)
- **Background**: #F8F9FE (Trắng xám nhạt cho nội dung)
- **Accent**: Các màu sắc tươi sáng cho icon (Đỏ, Cam, Xanh lá, Xanh dương).

## Cấu trúc thư mục (Folder Structure) - [HOÀN THÀNH]
Tuân thủ yêu cầu chia tách rõ ràng:
- `lib/core/`: Chứa các cấu hình dùng chung (theme, constants, routes).
- `lib/pages/`: Các màn hình chính (SignIn, SignUp, Home).
- `lib/widgets/`: Các thành phần UI nhỏ có thể tái sử dụng.
- `lib/services/`: Xử lý logic nghiệp vụ và gọi API (Mock API).
- `lib/models/`: Định nghĩa các đối tượng dữ liệu.
- `lib/utils/`: Các hàm tiện ích.

## Công nghệ & Thư viện sử dụng - [HOÀN THÀNH]
- **State Management**: `provider` (theo gợi ý trong README).
- **Typography**: `google_fonts` (sử dụng font Inter hoặc Roboto).
- **Icons**: `Material Icons` và `Font Awesome`.
- **Authentication**: `local_auth` cho tính năng vân tay.
- **HTTP Client**: `dio` (đã có trong pubspec.yaml).

## Lộ trình thực hiện

### Bước 1: Khởi tạo & Cấu trúc - [HOÀN THÀNH]
- Cập nhật `pubspec.yaml` với các thư viện cần thiết.
- Thiết lập hệ thống thư mục.
- Cấu hình Global Theme (Colors, TextStyles) và Navigation (Routes).

### Bước 2: Phát triển UI Cơ bản & Mock Data - [HOÀN THÀNH]
- Xây dựng các Widget nhỏ: `CustomTextField`, `CustomButton`, `CreditCardWidget`, `FeatureItem`.
- Tạo Mock API Service (`AuthService`) để xử lý đăng nhập và đăng ký.

### Bước 3: Màn hình Sign In & Sign Up - [HOÀN THÀNH]
- Triển khai giao diện theo thiết kế `Sign in.png` và `Sign up #2.png`.
- Tích hợp tính năng xác thực vân tay bằng `local_auth`.
- Xử lý logic chuyển trang và validate form.

### Bước 4: Màn hình Home (Dashboard) - [HOÀN THÀNH]
- Triển khai giao diện theo thiết kế `Home.png`.
- Header với ảnh đại diện và thông báo.
- Widget thẻ tín dụng với hiệu ứng gradient cao cấp.
- Lưới các chức năng (Grid 3x3) với các icon màu sắc.
- Thanh điều hướng phía dưới (Bottom Navigation Bar).

### Bước 5: Hoàn thiện & Tối ưu - [ĐANG THỰC HIỆN]
- Đảm bảo layout responsive trên các kích thước màn hình Android.
- Kiểm tra lại toàn bộ luồng điều hướng và logic xác thực.

---
**Tiến độ hiện tại: 95%**
Dự án đã cơ bản hoàn thành tất cả các chức năng và giao diện theo thiết kế. Bạn có thể chạy ứng dụng bằng lệnh `flutter run`.
