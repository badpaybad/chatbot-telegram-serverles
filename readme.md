
# Biến PC của bạn thành 1 AI chat bot assistant

- Chạy hoàn toàn private PC của bạn, không cần server, không cần domain, không cần database server, bảo mật, an toàn dữ liệu

- Thực hiện lệnh từ xa thông qua chát chít (UI telegram chat) ( command line exec với ngôn ngữ tự nhiên bạn không cần biết tới lệnh chạy thật, an toàn đảm bảo)
- Tổng hợp tin nhắn từ các group chat . VD như 1 con bot hóng tin và summary cho bạn
- Jira : Hỗ trợ các nhóm cskh tạo tự động các issues và báo cáo tiến độ cho issues 
- Quét các folder tại PC chủ động dùng OCR , LLM ... summary image , video, pdx, docx ... để làm knowledge base cho assistant PC của bạn  
- Google drive, ms one drive ..
- Browser automation (puppyteer,playwright), GUI automation ( pyautogui)
- Hỗ trợ gemini, nếu bạn không muốn dùng gemini có thể dùng LLM PC như ollama, llama.cpp ...
- Tự bổ xung thêm skill nhờ LLM và python script, đơn giản chỉ cần tạo subfolder trong skills với cấu trúc

                        skill_name
                        ├── main.py
                        ├── readme.md
                        └── config.py

hoặc gemini_dynamic : có các buildin tool call: cli, http request crawler, file io, database query ... sẽ tự động build json input cho các tool call khi cần vào context chat, việc quyết định gọi tool call rồi gọi qua lại các tool call khác để có kết quả theo intent của người dùng

                        skill_name
                        ├── system_instruction.md
                        ├── readme.md


| cmd explain and exec | email cli |
| :---: | :---: |
|![cli](img1.png)|![email](img2.png)|

|jira issues|poem|
|:---: |:---: |
|![jira](img4.png)|![poem](img3.png)|

# Chạy trực tiếp trên PC không cần server cần: OS Ubuntu, Telegram, Gemini api  

Use telegram as chatbot assitance. We dont need develop UI to chat, we just wait telegram callback webhook , then we call LLM , then send reply message 

- Use cloud flare tunnel to get an free ssl subdomain
- Every time start app we need to update web hook (subdomain from cloud flare) for telegram chatbot 


We dont need build server , dont need buy domain ... Just use our PC , We can use ollama to deploy local PC.

When we chat an message -> telegram call webhook to subdomain ( we use cloudflare tunnel ) -> python in our PC call LLM (eg: gemini or ollama local PC) -> get response -> chatbot reply message 

Just need : python program.py 

All above run

# 1. tạo chatbot telegram 

          Cách sử dụng @BotFather để tạo bot:
          Tìm kiếm @BotFather: Mở Telegram, tìm kiếm "@BotFather" (nhớ tìm bot có dấu tích xanh xác nhận).
          Bắt đầu: Gõ /start và nhấn gửi.
          Tạo bot mới: Gõ lệnh /newbot.
          Đặt tên: Nhập tên hiển thị cho bot (ví dụ: "MyBotAssitance").
          Đặt username: Nhập username cho bot (phải kết thúc bằng "bot", ví dụ: "MyBotAssitance_bot").
          Nhận token: BotFather sẽ gửi lại một mã API token, đây là chìa khóa để bạn lập trình bot của mình.
          Quản lý bot: Dùng các lệnh khác như /mybots để xem danh sách bot, /setdescription để đổi mô tả, hoặc /setuserpic để đổi ảnh đại diện. 
          Cần turn off group privacy để bot luôn nhận được tin nhắn từ các group nó được add vào. 

# 2. cloudflare tunnel 


          # 1. Tải về file cài đặt (Phiên bản cho Linux 64-bit thông dụng)
          curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

          # 2. Cài đặt
          sudo dpkg -i cloudflared.deb

          # 3. Kiểm tra xem cài được chưa
          cloudflared --version

          # 4. Tạo tunnel , sẽ dùng subproces python chạy cmd khi start app, bạn ko cần chạy tay 
          cloudflared tunnel --url http://localhost:8088

# 3. coding 

            rename config.sample.py into config.py 

            fill your : TELEGRAM_BOT_TOKEN , TELEGRAM_BOT_USERNAME ....

# 4. run app 


              python -m venv venv
              source venv/bin/activate


              pip install --upgrade pip
              pip install fastapi uvicorn pydantic httpx pynacl google-genai telethon Pyrogram matplotlib bs4 playwright faiss-cpu fasttext numpy transformers sentence_transformers 

              pip install einops timm

              playwright install chromium

              python program.py 

                          INFO:     Waiting for application startup.
                          🚀 Server đang khởi động, bắt đầu đăng ký Webhook...
                          🛰️ Đang khởi tạo Cloudflare Tunnel...
                          INFO:     Application startup complete.
                          INFO:     Uvicorn running on http://0.0.0.0:8088 (Press CTRL+C to quit)
                          INFO:     127.0.0.1:48778 - "GET / HTTP/1.1" 200 OK
                          Server đã sẵn sàng trên port 8088!
                          🔗 Đang gửi Webhook tới Telegram: https://may-allergy-codes-precious.trycloudflare.com/webhook
                          Tunnel đang cần đăng ký: https://may-allergy-codes-precious.trycloudflare.com/webhook
                          Telegram Response: {'ok': True, 'result': True, 'description': 'Webhook was set'}


# 5. LLM local  

                    If dont want gemini can use ollama  local 

                    https://github.com/ollama/ollama


### Nếu bạn là devleroper nên dùng: https://github.com/ggml-org/llama.cpp 

              
# 6. my_telethon.py

Để lấy tất cả msg mà account của bạn đã tham gia, rồi summary unread và gửi vào saved messages. Không bắt buộc cần có


            if  TELEGRAM_API_ID is not None and TELEGRAM_API_ID !="" and TELEGRAM_API_HASH is not None and TELEGRAM_API_HASH != "": 
                # https://my.telegram.org/apps  nếu muốn nhận tất cả tin nhắn từ các nhóm mà bạn tham gia 
                asyncio.create_task(my_telethon.run_until_disconnected())

            https://my.telegram.org/apps find it here
            TELEGRAM_API_ID=""
            TELEGRAM_API_HASH="" 


# pyautogui

Dùng để lấy thông tin trên màn hình = OCR 

            pip install pyautogui pillow opencv-python easyocr


# skills 

Là folder chứa các skill, mỗi skill là một folder chứa các file sau:

- readme.md: Mô tả chức năng của skill
- main.py: Chứa logic của skill
- config.py: Chứa cấu hình của skill


# orchestrationcontext.py

Là file chứa logic để điều phối các skill, mỗi skill là một folder chứa các file sau:

- tự động build prompt từ các file trong folder skills/ đọc file readme.md của từng skill

# dbcontext

các tên db và bảng dùng sqllite chung cho cả project, có query json , dùng dbconnect.py để kết nối sqllite


# chat context

- Luôn luôn phải có context chat, dùng để quyết định orchestration route, từng skill đều chung 
- List Summary , List Recent Chat, Current Message , Urls, Content for url (scraped from url), files ( image, video, pdf, docx, csv, excel, txt ...)
- Chat context phân biệt nhờ chat_id 

# LLM 

- Luôn luôn phải có LLM để quyết định orchestration route, từng skill đều chung 
- LLM phân biệt nhờ chat_id 
- LLM có thể là gemini hoặc ollama local
- LLM có tool call hoặc function call để gọi các skill
