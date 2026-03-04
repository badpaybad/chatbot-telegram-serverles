from config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH


import re
import time
from typing import Any
import httpx
import os
import aiofiles

import telegram_types

if not os.path.isdir("downloads"):
    os.makedirs("downloads")
async def download_telegram_file(file_id: str, chat_id: int, custom_file_name: str | None = None, sub_dir: str | None = None):
    """
    Downloads a file from Telegram and saves it to a directory named after the chat_id.
    If sub_dir is provided, saves it in a nested directory.
    Returns the absolute path of the saved file.
    """
    async with httpx.AsyncClient() as client:
        # 1. Get file path from Telegram
        get_file_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
        try:
            response = await client.post(get_file_url, json={"file_id": file_id})
            response.raise_for_status()
            file_info = response.json()
            file_path = file_info["result"]["file_path"]
        except (httpx.HTTPStatusError, KeyError) as e:
            print(f"Error getting file path from Telegram: {e}")
            return None

        # 2. Download the file
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        try:
            response = await client.get(file_url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"Error downloading file: {e}")
            return None

        # 3. Save the file
        save_dir = f"downloads/{chat_id}"
        if sub_dir:
            save_dir = os.path.join(save_dir, sub_dir)
            
        os.makedirs(save_dir, exist_ok=True)
        
        if custom_file_name:
            file_name = custom_file_name
        else:
            file_name = os.path.basename(file_path)
            
        save_path = os.path.join(save_dir, file_name)

        try:
            async with aiofiles.open(save_path, "wb") as f:
                await f.write(response.content)
            print(f"File saved to {save_path}")
            return os.path.abspath(save_path)
        except Exception as e:
            print(f"Error saving file: {e}")
            return None

import knowledgebase
import knowledgebase.orchestrationcontext
import knowledgebase.dbcontext

async def send_telegram_welcome(chat_id: int , text:str|None=None):
    botuname=TELEGRAM_BOT_USERNAME.replace("@","")
    async with httpx.AsyncClient() as client:
        try:
            boturl=f"t.me/{botuname}?start=welcome"
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            text=f"Bot AI @{botuname}, {text if text else ''}, gửi link https://{boturl} để cho người dùng kích hoạt bot"
          
            response = await client.post(url, json={"chat_id": chat_id, "text": text,
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "Kích hoạt Bot (Inbox)", "url": boturl}]
                ]
            }
            }, timeout=30.0)
        
            pass
        except:
            pass
    pass

async def send_telegram_message(chat_id: int, text: str, files: list[str] | None = None, isSendToGroup: bool = True) -> telegram_types.TelegramUpdate | None:
    """_summary_

    Args:
        chat_id (int): group chat_id vd -5251554348 or user_id individual vd 730806080 
        text (str): _description_
        files (list[str] | None, optional): _description_. Defaults to None.
        isSendToGroup (bool, optional): _description_. Defaults to True.

    Returns:
        telegram_types.TelegramUpdate | None: _description_
    """
    if (text is None or text == "") and not files:
        return None

    # if chat_id == -1:
    #     chat_id = int(TELEGRAM_BOT_CHATID)

    async with httpx.AsyncClient() as client:
        try:
            if files and len(files) > 0:
                # Determine which method to use based on file extension
                file_path = files[0]
                if not os.path.exists(file_path):
                    print(f"File không tồn tại: {file_path}")
                    # Fallback to sendMessage if text exists
                    if text:
                        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                        response = await client.post(url, json={"chat_id": chat_id, "text": text}, timeout=30.0)
                    else:
                        return None
                else:
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                        method = "sendPhoto"
                        file_key = "photo"
                    else:
                        method = "sendDocument"
                        file_key = "document"

                    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
                    
                    # Read file content
                    async with aiofiles.open(file_path, "rb") as f:
                        file_content = await f.read()
                    
                    files_payload = {file_key: (os.path.basename(file_path), file_content)}
                    data_payload = {"chat_id": chat_id, "caption": text}
                    
                    response = await client.post(url, data=data_payload, files=files_payload, timeout=30.0)
            else:
                # No files, just send message
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data_payload = {"chat_id": chat_id, "text": text}
                response = await client.post(url, json=data_payload, timeout=30.0)

            # print(f"send_telegram_message Response: {response.json()}")
            response.raise_for_status()

            telegram_response = telegram_types.TelegramUpdate(**response.json())

            if telegram_response:
                knowledgebase.dbcontext.sqllite_all_message.insert(telegram_response.json())
                knowledgebase.orchestrationcontext.summarychat.enqueue_update(telegram_response)

            return telegram_response
        except Exception as e:
            print(f"Lỗi khi gửi tin: {e}")
            if 'response' in locals() and response is not None:
                try:
                    print(f"Chi tiết lỗi từ Telegram: {response.text}")
                except:
                    pass
            return None


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
