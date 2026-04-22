# dựa vào các ảnh ở folder: design
tìm hiểu kỹ và đưa ra cách làm vào phattrien.md với các yêu cầu sau:
- Sử dụng ngôn ngữ tiếng việt để viết, giải thích, trình bày, tài liệu tất cả
- App phải chạy được như thiết kế với đầy đủ các chức năng được thể hiện trong ảnh
- Ưu tiên sử dụng các tính năng của flutter và android native có sẵng nếu không có thể tự tạo
- **bắt buộc** Cập nhật phattrien.md môĩ lần có yêu cầu mới từ yeucau.md 
- xem thêm README.md để biết build, debug, chạy và một số suggest về package
- **chú ý** cập nhật code xong cần **tự động** mở emulator nếu chưa và **tự động** chạy command vd [flutter emulators --launch Medium_Phone_API_27] or [flutter run -d emulator-5554] để test và sửa lỗi nếu có
Cần phân tích và làm việc sau cho code flutter
FE UI của app:
- cần bố cục layout
- pages là các màn hình
- các widgets là các thành phần ui nhỏ
- việc navigation cần thống nhất với global scope
- các wdigets, pages có thể tái sử dụng được, cần có định nghĩa rõ ràng trong file riêng biệt. tạo folder dedicated cho các components, pages, services, utils
- việc gửi state qua lại giữa widgets, pages cần thống nhất theo global scope
- Những thao tác cần tương tác BE qua api cần viết mock api và data cho FE sử dụng, sau này tích hợp với BE thật thông qua hàm fetch api 
- Bổ xung việc nhận notification từ google FCM cho cả android và ios, dùng thư viện của firebase realtime, firestore, thư việc về tương tác bluetooh, vân tay, khuôn mặt, nfc, wifi, 5g, 4g ...
- UI cần định nghĩa thêm việc theme change: màu sáng và màu tối cho app.

**cập nhật 2026-04-22 09:09:09**
cần lưu dữ liệu không quan trọng xuống ổ cứng, như cấu hình về hiển thị cá nhân, các dữ liệu tạm thời, cache, hoặc nhận diện khuôn mặt, chụp ảnh, files ... để khi khởi động lại app không bị mất dữ liệu và có thể sử dụng lại được. chọn package có hỗ trợ về vector database để dùng gemma4 hoặc fasttext, faiss ...