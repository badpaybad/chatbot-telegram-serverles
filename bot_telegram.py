from config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH


import re
import time
from typing import Any
import httpx


async def send_telegram_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id, "text": text}
        try:
            await client.post(TELEGRAM_API_URL, json=payload)
        except Exception as e:
            print(f"Lỗi khi gửi tin: {e}")


async def register_webhook(webhook_base_url: str):
    # 1. Khởi tạo tunnel tới cổng 8088
    if not webhook_base_url:
        print(f"Không lấy được webhook_url")
        return

    # 2. Bắt đầu chạy tunnel và lấy URL
    # Lệnh này sẽ trả về URL có dạng https://xxx.trycloudflare.com
    webhook_url = f"{webhook_base_url}/webhook"

    print(f"Webhook đang cần đăng ký: {webhook_url}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
            params={"url": webhook_url}
        )
        print("Telegram Response:", response.json())
        if response.status_code != 200:
            raise Exception("Không đăng ký webhook cho telegram được")

    print(f"Webhook đang chạy: {webhook_url}")
    # Lưu ý: Khi dùng cách này, tunnel sẽ chạy song song với ứng dụng của bạn.
