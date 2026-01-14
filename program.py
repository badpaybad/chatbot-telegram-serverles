from collections import defaultdict, deque
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from fastapi import FastAPI, Request, HTTPException
import subprocess
import re
import time
from typing import Any
from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from google import genai
from google.genai import types
from gemini_truyenkieu import chat_voi_cu_nguyen_du, chat_voi_cu_nguyen_du_memory

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH

import bot_telegram
import bot_discord

import my_telethon
import telegram_types
# --- CẤU HÌNH ---

# Biến toàn cục để quản lý tiến trình tunnel
tunnel_process = None
webhook_base_url = None

# --- LỊCH SỬ CHAT ---
# Sử dụng defaultdict để tự động tạo deque cho chat_id mới
# deque với maxlen=10 sẽ tự động xóa tin nhắn cũ nhất khi đầy
chat_history = defaultdict(lambda: deque(maxlen=10))

# --- HÀM GỬI TIN NHẮN (ASYNC) ---


async def wait_for_server_ready(url: str, timeout: int = 30):
    """Đợi cho đến khi server local thực sự phản hồi trước khi đăng ký webhook"""
    async with httpx.AsyncClient() as client:
        start_time = asyncio.get_event_loop().time()
        while True:
            await asyncio.sleep(1)
            try:
                # Kiểm tra thử xem port 8088 đã mở chưa
                response = await client.get(f"http://localhost:{PORT}")
                if response.status_code == 200:
                    print(f"Server đã sẵn sàng trên port {PORT}!")
                    return True
            except httpx.ConnectError:
                pass

            if (asyncio.get_event_loop().time() - start_time) > timeout:
                print("Quá thời gian chờ server khởi động.")
                return False

"""
# 1. Tải về file cài đặt (Phiên bản cho Linux 64-bit thông dụng)
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# 2. Cài đặt
sudo dpkg -i cloudflared.deb

# 3. Kiểm tra xem cài được chưa
cloudflared --version


cloudflared tunnel --url http://localhost:8088

"""


async def cloudflare_tunel_get_baseurl():

    global tunnel_process
    global webhook_base_url

    # 1. Khởi động Cloudflared
    print("Đang khởi tạo Cloudflare Tunnel...")
    tunnel_process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url",
            f"http://localhost:{PORT}", "--no-autoupdate"],
        stderr=subprocess.PIPE,
        text=True
    )

    await asyncio.sleep(0.5)
    # 2. Lấy URL từ log (non-blocking)
    for _ in range(500):
        line = tunnel_process.stderr.readline()
        if "https://" in line and ".trycloudflare.com" in line:
            match = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
            if match:
                webhook_base_url = match.group(0)
                break
        await asyncio.sleep(0.1)

    if not webhook_base_url:
        print("Không lấy được URL từ Cloudflare")
        return

    return webhook_base_url


async def background_tunnel_and_webhook():
    await cloudflare_tunel_get_baseurl()

    # 3. Đợi cho đến khi port 8088 thông (FastAPI đã boot xong)
    if await wait_for_server_ready(webhook_base_url):
        # 4. Cuối cùng mới đăng ký với Telegram
        full_url = f"{webhook_base_url}/webhook"
        print(f"Đang gửi Webhook tới Telegram: {full_url}")

        await asyncio.sleep(5)
        # await register_webhook_to_telegram(full_url)
        await bot_telegram.register_webhook(webhook_base_url)
        # await bot_discord.update_discord_endpoint(webhook_base_url)

        if TELEGRAM_BOT_CHATID is not None and TELEGRAM_BOT_CHATID != "" and TELEGRAM_BOT_CHATID != 0:
            await asyncio.sleep(2)
            await bot_telegram.send_telegram_message(TELEGRAM_BOT_CHATID, webhook_base_url)


@asynccontextmanager
async def lifespan(app: FastAPI):

    if TELEGRAM_BOT_TOKEN is None or TELEGRAM_BOT_TOKEN != "":
        print("Server đang khởi động, bắt đầu đăng ký Webhook...")
        asyncio.create_task(background_tunnel_and_webhook())

    if TELEGRAM_API_ID is not None and TELEGRAM_API_ID != "" and TELEGRAM_API_HASH is not None and TELEGRAM_API_HASH != "":
        # https://my.telegram.org/apps  nếu muốn nhận tất cả tin nhắn từ các nhóm mà bạn tham gia
        asyncio.create_task(my_telethon.run_until_disconnected())

    yield  # Sau từ khóa yield là nơi server đang chạy

    # --- Chạy khi SERVER TẮT ---
    print("Shutting down...")
    # --- TẮT SERVER ---
    print("Đang đóng Tunnel...")
    if tunnel_process:
        tunnel_process.terminate()
        tunnel_process.wait()
    print("Server đã tắt hoàn toàn.")

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Bot is running!"}


# Whitelist: Chỉ trả lời các ID này
ALLOWED_IDS = []  # [987654321, -100123456789]


# --- WEBHOOK ENDPOINT ---

@app.post("/webhook")
async def handle_webhook(request: Request):
    # Lấy toàn bộ dữ liệu JSON thô từ Telegram
    data = await request.json()
    print(data)
    update = telegram_types.TelegramUpdate.model_validate(data)
    # 1. Kiểm tra xem có phải là tin nhắn mới không
    if not update.message:
        return {"status": "ignored", "reason": "Not a new message"}

    # --- KIỂM TRA THỜI GIAN ---
    current_time = time.time()  # Thời gian hiện tại của server
    # Thời gian tin nhắn được gửi (Unix timestamp)
    message_time = update.message.date

    # Tính độ trễ (giây)
    time_diff = current_time - message_time

    if time_diff > 60*60*60:
        print(f"Bỏ qua tin nhắn cũ ({int(time_diff)} giây trước)")
        return {"status": "ignored", "reason": "Message too old"}

    chat_id = update.message.chat.id
    user_text = update.message.text

    # 2. Kiểm tra Whitelist (Bảo mật)
    if len(ALLOWED_IDS) > 0 and chat_id not in ALLOWED_IDS:
        print(f"Blocked ID: {chat_id}")
        return {"status": "ignored", "reason": "Unauthorized"}

    # 3. Xử lý Logic
    print(f"Nhận tin từ {chat_id}: {user_text}")

    # 2. Kiểm tra nếu tin nhắn có chứa nội dung và có tag tên bot
    # Cách đơn giản: Kiểm tra text có chứa @robotnotification_bot không
    # if user_text and TELEGRAM_BOT_USERNAME in user_text:
    #     # Xóa tên bot khỏi nội dung để lấy phần câu hỏi thực tế
    #     clean_message = user_text.replace(TELEGRAM_BOT_USERNAME, "").strip()

    #     # Lấy lịch sử cho chat_id này
    #     history = list(chat_history[chat_id])

    #     # Gọi AI với lịch sử
    #     reply_text, history1 = chat_voi_cu_nguyen_du_memory(
    #         clean_message, history=history)

    #     # Cập nhật lịch sử
    #     chat_history[chat_id].append(
    #         {"role": "user", "parts": [clean_message]})
    #     chat_history[chat_id].append({"role": "model", "parts": [reply_text]})

    #     # Gọi hàm gửi tin (dùng await để không chặn server)
    #     await send_telegram_message(chat_id, reply_text)

    # https://t.me/dunp_assitant_bot chat with your chatbot
    clean_message = user_text.replace(TELEGRAM_BOT_USERNAME, "").strip()

    # Lấy lịch sử cho chat_id này
    history = list(chat_history[chat_id])

    # Gọi AI với lịch sử
    reply_text, history1 = chat_voi_cu_nguyen_du(
        clean_message, history=history)

    # Cập nhật lịch sử
    chat_history[chat_id].append(
        {"role": "user", "parts": [clean_message]})
    chat_history[chat_id].append({"role": "model", "parts": [reply_text]})

    # Gọi hàm gửi tin (dùng await để không chặn server)
    await bot_telegram.send_telegram_message(chat_id, reply_text)

    return {"status": "ok"}


@app.post("/discord")
async def discord_interactions(request: Request):
    # 1. Bắt buộc phải xác thực chữ ký (Discord yêu cầu)
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    body = await request.body()
    print(f"DISCORD body: {body}")
    body_decode = body.decode()
    verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBKEY))
    try:
        verify_key.verify(
            timestamp.encode() + body,
            bytes.fromhex(signature))
        # verify_key.verify(f"{timestamp}".encode() + body, bytes.fromhex(signature))
    except Exception as ex:
        print(f"DISCORD: fail ping pong: {ex}")
        raise HTTPException(
            status_code=401, detail="Invalid request signature")

    print(f"DISCORD: {timestamp} {signature} {body_decode}")
    # 2. Xử lý gói tin PING từ Discord (Để lưu được URL)
    data = await request.json()
    print(f"DISCORD JSON : {data}")

    if data.get("type") == 1:
        return {"type": 1}  # Trả về PING thành công

    # 3. Xử lý tin nhắn chat của bạn ở đây...
    # 2. Xử lý khi có người dùng tương tác (Slash Command hoặc Mention)
    if data.get("type") == 2:  # Type 2 là Application Command (ví dụ lệnh /)
        command_data = data.get("data", {})
        # Lấy chat_id (channel_id trong discord)
        chat_id = data.get("channel", {}).get("id")
        user_input = ""

        # Lấy nội dung người dùng nhập (nếu dùng Slash Command)
        options = command_data.get("options", [])
        if options:
            user_input = options[0].get("value", "")
        if user_input == "":
            return {"type": 6}

        # Lấy lịch sử cho kênh này
        history = list(chat_history[chat_id])

        # Gọi hàm AI của bạn
        bot_reply, history1 = chat_voi_cu_nguyen_du(
            user_input, history=history)

        # Cập nhật lịch sử
        chat_history[chat_id].append({"role": "user", "parts": [user_input]})
        chat_history[chat_id].append({"role": "model", "parts": [bot_reply]})

        # Trả về kết quả cho Discord
        return {
            "type": 4,
            "data": {
                "content": f"{bot_reply}",
                "tts": False  # Text-to-speech
            }
        }

    return {"status": "ok"}

# Đoạn này để chạy trực tiếp bằng python main.py (hoặc dùng lệnh uvicorn ở ngoài)


if __name__ == "__main__":
    uvicorn.run("program:app", host="0.0.0.0", port=PORT, reload=False)

    # đăng ký bot callback  https://api.telegram.org/bot<TOKEN_CUA_BAN>/setWebhook?url=<LINK_NGROK>/webhook
