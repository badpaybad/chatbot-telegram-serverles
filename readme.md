
# idea

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
              pip install fastapi uvicorn pydantic httpx pynacl google-genai

              python program.py 

# 5. ollama 

              If dont want gemini can use ollama  local 

              https://github.com/ollama/ollama

              
