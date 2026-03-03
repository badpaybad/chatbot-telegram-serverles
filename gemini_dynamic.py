import subprocess
import re
import os
import json
import uuid
import time
from typing import Any
import httpx
import asyncio
from contextlib import asynccontextmanager
import mimetypes
import httpx
from urllib.parse import urlparse
import importlib.util
import sys
from google import genai
from google.genai import types

from config import HISTORY_CHAT_MAX_LEN,TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY,GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME

# Imports moved inside exec for robustness and easier testing

# Initialize Gemini client
clientGemini = genai.Client(api_key=GEMINI_APIKEY)
# Khai báo công cụ Google Search
google_search_tool = types.Tool(
    google_search=types.GoogleSearch()
)

async def exec(skill, curret_message, list_current_msg, list_summary_chat, unique_urls,contents_from_url,system_instruction):
    # Import inside to avoid circular dependencies and allow isolated testing
    import bot_telegram
    import knowledgebase.orchestrationcontext 

    user_text = curret_message.text
    chat_id = curret_message.chat_id
    
    # 1. Tạo Context Block
    summary_text = "### [Summarized History]\n"
    if list_summary_chat:
        for item in list_summary_chat:
            if isinstance(item, dict) and "json" in item:
                summary_text += f"- {item['json'].get('summary', '')}\n"
            else:
                summary_text += f"- {str(item)}\n"
    else:
        summary_text += "(Không có lịch sử tóm tắt)\n"
            
    recent_text = "### [Recent Messages]\n"
    for msg in list_current_msg:
        recent_text += f"- {getattr(msg, 'text', str(msg))}\n"
        
    context_block = f"{summary_text}\n{recent_text}\n### [Current Message]\n{user_text}"
    
    if unique_urls:
        context_block += "\n### [URLs]\n" + "\n".join(unique_urls)
    if contents_from_url:
        context_block += "\n### [Contents from URL]\n" + "\n".join(contents_from_url)

    # 2. Chuẩn bị Gemini Input
    user_parts = [types.Part.from_text(text=context_block)]
    
    # Xử lý file nếu có trong context
    if hasattr(curret_message, 'files') and curret_message.files:
        print(f"--- Uploading {len(curret_message.files)} files for CLI skill ---")
        for fpath in curret_message.files:
            try:
                mime_type_guess, _ = mimetypes.guess_type(fpath)
                mtype = knowledgebase.orchestrationcontext.map_mime_type(mime_type_guess)
                uploaded = clientGemini.files.upload(file=fpath, config=types.UploadFileConfig(mime_type=mtype))

                # 2. Vòng lặp kiểm tra trạng thái (Check state)
                while True:
                    # Lấy lại thông tin file để cập nhật thuộc tính 'state'
                    file_info = clientGemini.files.get(name=uploaded.name)
                    
                    state = file_info.state.name # Trạng thái trả về: 'PROCESSING', 'ACTIVE', hoặc 'FAILED'
                    
                    if state == "ACTIVE":
                        print(f"{fpath} File đã sẵn sàng!")
                        break
                    elif state == "FAILED":
                        print(f"{fpath} Google không thể xử lý video này. Lỗi: FAILED")
                        break
                    else:
                        print(f"{fpath} Video đang được xử lý (PROCESSING)...")
                        time.sleep(3)

                user_parts.append(types.Part.from_uri(file_uri=uploaded.uri, mime_type=uploaded.mime_type))
            except Exception as e:
                print(f"CLI Skill file upload error: {e}")
    system_instruction="""
    Dựa vào dữ liệu đầu vào bạn sẽ trả lời lại cho người dùng. Có thể gọi các công cụ (tool call) để thực hiện hành động.
    Bạn có thể dùng các công cụ để gọi qua lại lấy đủ thông tin đầu vào cho từng công cụ cho đến khi có kết quả 
    
    Dữ liệu đầu vào sẽ bao gồm:
        - [Summarized History]: Tóm tắt lịch sử hội thoại.
        - [Recent Messages]: Các tin nhắn gần đây.
        - [Current Message]: Tin nhắn hiện tại của người dùng.
        - [URLs]: Các đường dẫn liên quan (nếu có).
        - Các file được gửi kèm (nếu có).
    """
    # 3. Gọi Gemini
    try:
        response = clientGemini.models.generate_content(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(
                temperature=0.0,
                system_instruction=system_instruction,
                tools= [google_search_tool]
            ),
            contents=[types.Content(role="user", parts=user_parts)]
        )
        
        gemini_reply = response.text
        if not gemini_reply:
             gemini_reply = "Gemini không trả về nội dung nào."
           
        final_msg = gemini_reply

        # todo: may be defind tool call, cli, http request, db connect ...
            
        await bot_telegram.send_telegram_message(chat_id, final_msg)
        
    except Exception as e:
        print(f"Dynamic gemini overall error: {e}")
        await bot_telegram.send_telegram_message(chat_id, f"Đã xảy ra lỗi khi thực thi yêu cầu: {str(e)}")
