Dùng DDD (Domain-Driven Design) để chia folder

Tham khảo assistantapp/techstack.md để biết các framework, thư viện, công cụ sẽ được sử dụng trong assistant app

Từng folder sẽ có các file .md tương ứng mô tả cách tạo code trong folder đó, vd: auth/ thì có auth.md mô tả cách tạo code logic trong folder auth

Dữ liệu được lưu trữ trong local với objectbox

Các folder sẽ có các file gọi api riêng và các types hoặc dto riêng

Các services cho từng folder sẽ chia sẻ các event, command thông qua 1 buss chung ở folder buss

Các action người dùng sẽ tạo các command và enqueue lên buss với topic : command_{tên folder}_{tên dto or tpyes hoặc 1 chuỗi string có ý nghĩa vd theo tên hàm}


Các action trước khi return hoặc kết thúc thường sẽ gửi 1 event (topic pub sub ) lên buss dạng : event_{tên folder}_{tên dto or tpyes hoặc 1 chuỗi string có ý nghĩa vd theo tên hàm}


Các queries sẽ được viết riêng ở class query trong folder, chỉ dùng để query dữ liệu từ local hoặc từ api , cache ...



