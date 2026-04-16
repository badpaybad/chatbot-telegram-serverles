from collections import defaultdict, deque
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from fastapi import FastAPI, Request, HTTPException
import subprocess
import re
import os
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

from config import HISTORY_CHAT_MAX_LEN,TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME

import config
import domain_handlers
import domain_handlers.ngoc_ddd

import bot_telegram
import bot_discord

import my_telethon
import telegram_types
import knowledgebase
import knowledgebase.dbcontext

import knowledgebase.orchestrationcontext 

from knowledgebase.orchestrationcontext import set_dir_program, skills_decision
import jira_helper

DIR_PROGRAM=os.path.dirname(os.path.abspath(__file__))

set_dir_program(DIR_PROGRAM)

# --- CẤU HÌNH ---

# Biến toàn cục để quản lý tiến trình tunnel
tunnel_process = None
webhook_base_url = None

# --- LỊCH SỬ CHAT ---
# Sử dụng defaultdict để tự động tạo deque cho chat_id mới
# deque với maxlen=10 sẽ tự động xóa tin nhắn cũ nhất khi đầy
# chat_history = defaultdict(lambda: deque(maxlen=HISTORY_CHAT_MAX_LEN))

# Buffer cho media group (nhiều ảnh gửi cùng lúc)
# {media_group_id: {"files": [path1, path2], "text": "caption", "chat_id": 123, "processed": False}}
media_group_buffer = {}
media_group_lock = asyncio.Lock()

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

async def jira_register_webhook(base_url):

    full_url = f"{base_url}/webhook-jira"

    jira_helper.create_or_update_webhook("chatbot-jira", full_url)
    
    pass
async def zalo_oa_register_webhook(base_url):

    full_url = f"{base_url}/webhook-zalo-oa"
    # todo: cần gọi lên zalo để update webhook url mới theo tunnel base_url
    
    pass

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
        await jira_register_webhook(webhook_base_url)
        await zalo_oa_register_webhook(webhook_base_url)

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

async def process_chat_history_and_received_msg(user_text: str, chat_id,listFilePath:list[str]  =None,currentmsg=None):

    if user_text is None or user_text == "":
        return ""
        
    clean_message = user_text.replace(TELEGRAM_BOT_USERNAME, "").strip()

    # Lấy lịch sử cho chat_id này
    # history = list(chat_history[chat_id])

    # Gọi AI với lịch sử
    reply_text, history1 = chat_voi_cu_nguyen_du_memory(clean_message, history=[],listPathFiles=listFilePath)

    # # Cập nhật lịch sử
    # chat_history[chat_id].append(
    #     {"role": "user", "parts": [clean_message]})
    # chat_history[chat_id].append({"role": "model", "parts": [reply_text]})

    return reply_text


# --- WEBHOOK ENDPOINT ---
# 
# Đang gửi Webhook tới Telegram: https://testing-sonic-profiles-deserve.trycloudflare.com/webhook-jira

@app.post("/webhook-jira")
async def handle_jira(request: Request):
    print("Đang nhận Webhook từ Jira...")
    jiradata=await request.json()
    # print(jiradata)
    # knowledgebase.dbcontext.db_jira.insert(jiradata)
    # todo: cần thao tác xử lý gì cần dùng dbcontext.py để lưu vào db, ở skills/jira cần lưu chat_id và jira url để sau có thể update và kiểm tra trạng thái rồi gửi message lên nhóm chát 
    pass

@app.post("/webhook-zalo-oa")
async def handle_zalo_oa(request: Request):
    print("Đang nhận Zalo từ Jira...")
    # print(await request.json())
    # todo: tất cả các loại chát khác, zalo, discord, whatsapp ... cần convert về dạng message của telegram, dùng để hỗ trợ cho zalo group chat tương tự telegram chat bot 
    pass


@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        
        # Lấy toàn bộ dữ liệu JSON thô từ Telegram
        data = await request.json()

        msg_id_guid = knowledgebase.dbcontext.sqllite_all_message.insert(data)
        update = telegram_types.TelegramUpdate.model_validate(data)

        knowledgebase.orchestrationcontext.summarychat.enqueue_update(update)

        print(update)

        if not update.message:
            if update.edited_message:
                update.message=update.edited_message
                pass
        # 1. Kiểm tra xem có phải là tin nhắn mới không
        if not update.message:
            return {"status": "ignored", "reason": "Not a new message"}

        # --- KIỂM TRA THỜI GIAN ---
        current_time = time.time()  # Thời gian hiện tại của server
        # Thời gian tin nhắn được gửi (Unix timestamp)
        message_time = update.message.date

        # Tính độ trễ (giây)
        time_diff = current_time - message_time

        # if time_diff > 60*60*60:
        #     print(f"Bỏ qua tin nhắn cũ ({int(time_diff)} giây trước)")
        #     return {"status": "ignored", "reason": "Message too old"}

        chat_id = update.message.chat.id
        user_text = update.message.text

        if update.message.caption:
            user_text=f"{user_text}\n\nCaption: {update.message.caption}"

        if update.message.reply_to_message:
            user_text=f"{user_text}\n\nReply to: {update.message.reply_to_message.text}"

        media_group_id = update.message.media_group_id

        # 2. Kiểm tra Whitelist (Bảo mật)
        if len(ALLOWED_IDS) > 0 and chat_id not in ALLOWED_IDS:
            print(f"Blocked ID: {chat_id}")
            return {"status": "ignored", "reason": "Unauthorized"}

        # 3. Xử lý file đính kèm
        listFilePath=[]
        media_files = []
        db_file_rec=[]
        if update.message.photo:
            # Lấy ảnh chất lượng cao nhất (cuối cùng trong list)
            media_files.append((update.message.photo[-1].file_id, None))
        
        if update.message.document:
            media_files.append((update.message.document.file_id, update.message.document.file_name))
            
        if update.message.video:
            media_files.append((update.message.video.file_id, update.message.video.file_name))
            
        if update.message.voice:
            media_files.append((update.message.voice.file_id, None))
            
        if update.message.audio:
            media_files.append((update.message.audio.file_id, update.message.audio.file_name))
            
        if update.message.animation:
            media_files.append((update.message.animation.file_id, update.message.animation.file_name))

        for file_id, custom_name in media_files:
            fpath=await bot_telegram.download_telegram_file(file_id, chat_id, custom_name, sub_dir=media_group_id)
            if fpath:
                listFilePath.append(fpath)
                db_file_rec.append({"msg_id":msg_id_guid,"chat_id":chat_id, "file_id": file_id, "file_path": fpath})

        if len(db_file_rec) > 0:
            knowledgebase.dbcontext.sqllite_all_message_file.insert(db_file_rec)
        print(f"Nhận tin từ {chat_id}: {user_text}")

        # 4. Xử lý Media Group logic (Buffering)
        if media_group_id:
            async with media_group_lock:
                if media_group_id not in media_group_buffer:
                    media_group_buffer[media_group_id] = {
                        "files": [],
                        "text": None,
                        "chat_id": chat_id,
                        "processed": False
                    }
                
                if user_text:
                    if media_group_buffer[media_group_id]["text"]:
                        temp_gtext=f"{media_group_buffer[media_group_id]["text"]}"
                    else:
                        temp_gtext=None

                    if temp_gtext:
                        media_group_buffer[media_group_id]["text"] = f"{temp_gtext}\n\n{user_text}"
                    else:
                        media_group_buffer[media_group_id]["text"] = user_text
                
                if listFilePath:
                    media_group_buffer[media_group_id]["files"].extend(listFilePath)
            
            # Đợi một chút để gom các tin nhắn khác trong album
            await asyncio.sleep(2)
            
            async with media_group_lock:
                # Chỉ xử lý nếu chưa được xử lý bởi request khác (cùng album)
                if media_group_buffer[media_group_id]["processed"]:
                    return {"status": "ok", "reason": "Handled by another request in group"}
                
                # Đánh dấu đã xử lý
                media_group_buffer[media_group_id]["processed"] = True
                
                # Lấy dữ liệu đã gom
                final_user_text = media_group_buffer[media_group_id]["text"]
                final_file_paths = media_group_buffer[media_group_id]["files"]

                user_text=final_user_text
                listFilePath=final_file_paths
                
            # # 5. Xử lý Logic AI cho Media Group
            # if final_user_text or final_file_paths:
            #     if REPLY_ON_TAG_BOT_USERNAME is not None and REPLY_ON_TAG_BOT_USERNAME:
            #         if (final_user_text and TELEGRAM_BOT_USERNAME in final_user_text):
            #             reply_text = await process_chat_history_and_received_msg(final_user_text or "", chat_id, final_file_paths,update)
            #             await bot_telegram.send_telegram_message(chat_id, reply_text)
            #     else:
            #         reply_text = await process_chat_history_and_received_msg(final_user_text or "", chat_id, final_file_paths,update)
            #         await bot_telegram.send_telegram_message(chat_id, reply_text)
                    
            # return {"status": "ok"}
        
        # # 4. Xử lý Logic (Tin nhắn đơn lẻ)
        # if user_text or listFilePath:
        #     telegram_response=None
        #     # 2. Kiểm tra nếu tin nhắn có chứa nội dung và có tag tên bot
        #     if REPLY_ON_TAG_BOT_USERNAME is not None and REPLY_ON_TAG_BOT_USERNAME:
        #         if user_text and TELEGRAM_BOT_USERNAME in user_text:
        #             reply_text = await process_chat_history_and_received_msg(user_text or "", chat_id, listFilePath,update)
        #             telegram_response = await bot_telegram.send_telegram_message(chat_id, reply_text)
        #     else:
        #         reply_text = await process_chat_history_and_received_msg(user_text or "", chat_id, listFilePath,update)
        #         telegram_response = await bot_telegram.send_telegram_message(chat_id, reply_text)   

        #     if telegram_response:
        #         #.model_dump_json(by_alias=True)
        #         sqllite_all_message.insert(telegram_response.json())
        #         summarychat.enqueue_update(telegram_response)

        orchestration_message=telegram_types.OrchestrationMessage()
        orchestration_message.message=update
        orchestration_message.msg_id=msg_id_guid
        orchestration_message.files=listFilePath
        orchestration_message.files_type= []
        for f in listFilePath:
            # if f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png") or f.endswith(".gif") or f.endswith(".webp"):
            #     orchestration_message.files_type.append("image")
            # elif f.endswith(".mp4") or f.endswith(".avi") or f.endswith(".mov") or f.endswith(".mkv"):
            #     orchestration_message.files_type.append("video")
            # elif f.endswith(".mp3") or f.endswith(".wav") or f.endswith(".aac") or f.endswith(".flac"):
            #     orchestration_message.files_type.append("audio")
            # elif f.endswith(".pdf") or f.endswith(".doc") or f.endswith(".docx") or f.endswith(".txt"):
            #     orchestration_message.files_type.append("document")
            # else:                
            #     orchestration_message.files_type.append("file")
            orchestration_message.files_type.append("file")
            
        orchestration_message.text=user_text
        orchestration_message.chat_id=chat_id
        orchestration_message.webhook_base_url=webhook_base_url

        if config.CONFIG_NAME=="config_ngoc":
            await domain_handlers.ngoc_ddd.handle(orchestration_message)
            # return  {"status": "ok"}
            pass
        
        if REPLY_ON_TAG_BOT_USERNAME is not None and REPLY_ON_TAG_BOT_USERNAME :
            if orchestration_message.text and TELEGRAM_BOT_USERNAME in orchestration_message.text:
                await skills_decision(orchestration_message)

        return {"status": "ok"}
    except Exception as ex:
        print(f"Lỗi khi xử lý tin nhắn: {ex}")
        # return {"status": "error", "reason": str(ex)}

        return {"status": "ok"}
# Đoạn này để chạy trực tiếp bằng python main.py (hoặc dùng lệnh uvicorn ở ngoài)


if __name__ == "__main__":
    uvicorn.run("program:app", host="0.0.0.0", port=PORT, reload=False)

    # đăng ký bot callback  https://api.telegram.org/bot<TOKEN_CUA_BAN>/setWebhook?url=<LINK_NGROK>/webhook

# @app.post("/discord")
# async def discord_interactions(request: Request):
#     # 1. Bắt buộc phải xác thực chữ ký (Discord yêu cầu)
#     signature = request.headers.get("X-Signature-Ed25519")
#     timestamp = request.headers.get("X-Signature-Timestamp")
#     body = await request.body()
#     print(f"DISCORD body: {body}")
#     body_decode = body.decode()
#     verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBKEY))
#     try:
#         verify_key.verify(
#             timestamp.encode() + body,
#             bytes.fromhex(signature))
#         # verify_key.verify(f"{timestamp}".encode() + body, bytes.fromhex(signature))
#     except Exception as ex:
#         print(f"DISCORD: fail ping pong: {ex}")
#         raise HTTPException(
#             status_code=401, detail="Invalid request signature")

#     print(f"DISCORD: {timestamp} {signature} {body_decode}")
#     # 2. Xử lý gói tin PING từ Discord (Để lưu được URL)
#     data = await request.json()
#     print(f"DISCORD JSON : {data}")

#     if data.get("type") == 1:
#         return {"type": 1}  # Trả về PING thành công

#     # 3. Xử lý tin nhắn chat của bạn ở đây...
#     # 2. Xử lý khi có người dùng tương tác (Slash Command hoặc Mention)
#     if data.get("type") == 2:  # Type 2 là Application Command (ví dụ lệnh /)
#         command_data = data.get("data", {})
#         # Lấy chat_id (channel_id trong discord)
#         chat_id = data.get("channel", {}).get("id")
#         user_input = ""

#         # Lấy nội dung người dùng nhập (nếu dùng Slash Command)
#         options = command_data.get("options", [])
#         if options:
#             user_input = options[0].get("value", "")
#         if user_input == "":
#             return {"type": 6}

#         bot_reply = await process_chat_history_and_received_msg(user_input, chat_id)

#         # Trả về kết quả cho Discord
#         return {
#             "type": 4,
#             "data": {
#                 "content": f"{bot_reply}",
#                 "tts": False  # Text-to-speech
#             }
#         }

#     return {"status": "ok"}
