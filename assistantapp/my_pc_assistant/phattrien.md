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
- **Bluetooth**: `flutter_blue_plus`.
- **NFC**: `nfc_manager`.
- **Connectivity**: `connectivity_plus` (Wifi, 4G, 5G).
- **HTTP Client**: `dio`.

## Lộ trình thực hiện (Tiếp theo)

### Bước 6: Tích hợp Firebase & Notification - [HOÀN THÀNH]
- Cấu hình khởi tạo Firebase trong `main.dart`.
- Xây dựng `NotificationService` để xử lý FCM (foreground, background, terminated).
- Thiết lập `DatabaseService` cho Firestore và Realtime Database.

### Bước 7: Tương tác Phần hardware (Bluetooth, Biometrics, NFC, Connectivity) - [HOÀN THÀNH]
- Xây dựng `BluetoothService` để quét và kết nối thiết bị.
- Xây dựng `BiometricService` hỗ trợ vân tay và FaceID thông qua `local_auth`.
- Xây dựng `NfcService` xử lý tương tác NFC.
- Xây dựng `ConnectivityService` theo dõi trạng thái mạng (Wifi, 4G, 5G).

### Bước 8: Đa giao diện (Light/Dark Mode) - [HOÀN THÀNH]
- Đã định nghĩa `darkTheme` trong `app_theme.dart`.
- Quản lý trạng thái thông qua `ThemeService` (Provider).
- Tích hợp nút chuyển đổi nhanh trên giao diện chính.

### Bước 9: Tích hợp Firebase (FCM, Firestore, Realtime) - [HOÀN THÀNH]
- Đã xây dựng `NotificationService` để xử lý FCM.
- Đã xây dựng `DatabaseService` để tương tác với Firestore và Realtime Database.

### Bước 10: Lưu trữ dữ liệu cục bộ & Vector Database - [HOÀN THÀNH]
- Tích hợp `shared_preferences` cho cấu hình người dùng (theme, cài đặt cá nhân).
- Tích hợp `path_provider` để quản lý tệp tin, ảnh chụp và bộ nhớ tạm (cache).
- Sử dụng `ObjectBox` làm Vector Database hỗ trợ lưu trữ embedding cho AI (Gemma4, FastText).
- Đảm bảo dữ liệu được duy trì khi khởi động lại ứng dụng.

--- 
Lưu ý quan trọng:
Để các tính năng Firebase hoạt động, bạn cần thực hiện bước cuối cùng là thêm các tệp cấu hình từ Firebase Console:

Thêm google-services.json vào thư mục android/app/.
Thêm GoogleService-Info.plist vào thư mục ios/Runner/.