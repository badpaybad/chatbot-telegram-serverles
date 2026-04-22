# dựa vào các ảnh ở folder: design
tìm hiểu kỹ và đưa ra cách làm vào phattrien.md với các yêu cầu sau:
- Sử dụng ngôn ngữ tiếng việt để viết, giải thích, trình bày, tài liệu tất cả
- App phải chạy được như thiết kế với đầy đủ các chức năng được thể hiện trong ảnh
- Ưu tiên sử dụng các thư viện của flutter và android native
- ưu tiên sử dụng các tính năng của flutter và android native có sẵng nếu không có thể tự tạo
- Cập nhật phattrien.md môĩ lần có yêu cầu mới từ yeucau.md 
- xem thêm README.md để biết build, debug, chạy và một số suggest về package
- cập nhật code xong cần chạy command [flutter run -d emulator-5556 ] để test và sửa lỗi nếu có
Cần phân tích và làm việc sau cho code flutter
FE UI của app:
- cần bố cục layout
- pages là các màn hình
- các widgets là các thành phần ui nhỏ
- việc navigation cần thống nhất với global scope
- các wdigets, pages có thể tái sử dụng được, cần có định nghĩa rõ ràng trong file riêng biệt. tạo folder dedicated cho các components, pages, services, utils
- việc gửi state qua lại giữa widgets, pages cần thống nhất theo global scope
- Những thao tác cần tương tác BE qua api cần viết mock api và data cho FE sử dụng, sau này tích hợp với BE thật thông qua hàm fetch api 
- Bổ xung việc nhận notification từ google FCM cho cả android và ios, dùng thư viện của firebase realtime, firestore, thư việc về tương tác bluetooh, vân tay, khuôn mặt ...
- 
