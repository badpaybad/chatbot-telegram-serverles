# my_pc_assistant

Dự án Flutter hỗ trợ điều khiển và quản lý PC thông qua Telegram Assistant. Dự án này được phát triển và tối ưu hóa bằng **Google Antigravity IDE**.

## 🚀 Bắt đầu

### 🛠 Yêu cầu hệ thống
- Flutter SDK (phiên bản mới nhất)
- Android SDK (cho Android) / Xcode (cho iOS)
- Android NDK: `27.0.12077973` (Cấu hình trong `android/app/build.gradle.kts`)
- Google Antigravity IDE

### 🏃 Cách chạy ứng dụng
Để chạy ứng dụng trên thiết bị giả lập hoặc thiết bị thật, sử dụng lệnh sau trong terminal:

```bash
flutter run
```

### 📱 Máy ảo & Thiết bị (Emulator/Simulator)
Để kiểm tra danh sách máy ảo và thiết bị đang kết nối:
```bash
flutter devices
```

Để liệt kê các máy ảo có sẵn:
```bash
flutter emulators
```

Để khởi chạy một máy ảo cụ thể:
```bash
flutter emulators --launch <emulator_id>
flutter run -d emulator-5556

```

> [!TIP]
> Nếu máy ảo không khởi động được hoặc gặp lỗi `Broken pipe (32)` khi cài đặt APK:
> 1. Xóa file lock: `find ~/.android/avd -name "*.lock" -delete`
> 2. Chạy máy ảo ở trạng thái sạch (không snapshot): `flutter emulators --launch <id> --no-snapshot`
> 3. Hoặc xóa trắng dữ liệu máy ảo: `flutter emulators --launch <id> --wipe-data`

### 🐞 Debug & Sửa lỗi
- **Hot Reload**: Nhấn `r` trong terminal khi đang chạy `flutter run` để cập nhật code ngay lập tức.
- **Hot Restart**: Nhấn `R` để khởi động lại app.
- **Antigravity Debug**: Bạn có thể dán log lỗi vào khung chat và hỏi: "Lỗi này là gì và sửa thế nào?". Tôi sẽ phân tích stack trace và đề xuất code sửa lỗi chính xác.

### 🧪 Kiểm thử (Testing)
Để chạy toàn bộ các bài test trong thư mục `test/`:
```bash
flutter test
```
*Gợi ý: Bạn có thể bảo tôi: "Viết unit test cho hàm xử lý tin nhắn Telegram trong file telegram_service.dart".*

### 📦 Quản lý Package
Khi cần thêm thư viện mới (ví dụ: `http`, `provider`, v.v.), bạn có thể sử dụng lệnh:

```bash
flutter pub add <tên_package>
```
Sau đó chạy `flutter pub get` để cập nhật dependencies.
*Mẹo: Bạn có thể bảo Antigravity: "Thêm package http vào dự án giúp tôi".*

### 🏗 Build ứng dụng

#### Cho Android (APK/Bundle):
```bash
flutter build apk --release
# Hoặc
flutter build appbundle --release
```

#### Cho iOS:
```bash
flutter build ios --release
```

## 🤖 Phát triển với Antigravity
Dự án này được tối ưu để làm việc cùng **Antigravity**. Bạn có thể tận dụng AI để:
- **Tạo UI nhanh chóng**: "Tạo cho tôi một màn hình Dashboard đẹp mắt với các thông số CPU, RAM".
- **Fix lỗi**: "Kiểm tra và sửa lỗi logic trong file main.dart".
- **Cập nhật tính năng**: "Thêm tính năng gửi thông báo khi PC bị quá nhiệt".

---
*Dự án là một phần của hệ sinh thái a.i-assistant-chatbot-telegram-serverless.*

