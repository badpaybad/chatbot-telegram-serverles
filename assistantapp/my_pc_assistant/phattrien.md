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

## Công nghệ & Thư viện sử dụng - [CẬP NHẬT]
- **State Management**: `provider`.
- **Firebase Ecosystem**: 
    - `firebase_core`: Khởi tạo Firebase.
    - `firebase_messaging` (FCM): Nhận thông báo đẩy trên Android/iOS.
    - `cloud_firestore`: Cơ sở dữ liệu NoSQL.
    - `firebase_database`: Realtime Database.
    - `firebase_analytics`: Phân tích dữ liệu.
- **Biometrics**: `local_auth` (Vân tay, Khuôn mặt - FaceID).
- **Connectivity**: `flutter_blue_plus` cho tương tác Bluetooth.
- **HTTP Client**: `dio`.

## Lộ trình thực hiện (Tiếp theo)

### Bước 6: Tích hợp Firebase & Notification
- Cấu hình khởi tạo Firebase trong `main.dart`.
- Xây dựng `NotificationService` để xử lý FCM (foreground, background, terminated).
- Thiết lập `FirestoreService` và `RealtimeDatabaseService`.

### Bước 7: Tương tác Phần cứng (Bluetooth & Biometrics)
- Xây dựng `BluetoothService` để quét và kết nối thiết bị.
- Hoàn thiện logic `LocalAuthService` cho cả FaceID (iOS) và vân tay (Android).

--- 
Lưu ý quan trọng:
Để các tính năng Firebase hoạt động, bạn cần thực hiện bước cuối cùng là thêm các tệp cấu hình từ Firebase Console:

Thêm google-services.json vào thư mục android/app/.
Thêm GoogleService-Info.plist vào thư mục ios/Runner/.