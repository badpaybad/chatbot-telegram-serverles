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
from urllib.parse import urlparse
import importlib.util
import sys
from google import genai
from google.genai import types

from config import (
    HISTORY_CHAT_MAX_LEN, TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, 
    TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, GEMINI_MODEL, 
    DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN, TELEGRAM_API_ID, 
    TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME, JIRA_PERSONAL_ACCESS_TOKEN, 
    JIRA_PROJECT_KEY, JIRA_SERVER_ISSUE_API, JIRA_SERVER_WEBHOOK_API
)

import bot_telegram
# import bot_discord
# import telegram_types

import knowledgebase
import skills.common_question_answer.main as common_question_answer
from knowledgebase.orchestrationbuildprompt import build_system_instruction
import knowledgebase.dbcontext
import knowledgebase.orchestrationcontext 

# Initialize Gemini client
clientGemini = genai.Client(api_key=GEMINI_APIKEY)

current_date = time.strftime("%Y-%m-%d")
JIRA_SYSTEM_INSTRUCTION = f"""
Bạn là một trợ lý quản lý dự án chuyên nghiệp. 
Nhiệm vụ của bạn là phân tích ngữ cảnh hội thoại để quyết định xem có nên tạo một issue trên Jira hay không.

Hôm nay là ngày: {current_date}

Dữ liệu đầu vào sẽ bao gồm:
- [Summarized History]: Tóm tắt lịch sử hội thoại.
- [Recent Messages]: Các tin nhắn gần đây.
- [Current Message]: Tin nhắn hiện tại của người dùng.
- [URLs]: Các đường dẫn liên quan (nếu có).
- Các file được gửi kèm (nếu có).

Quy tắc:
1. Bạn phải phân tích xem người dùng có đang yêu cầu tạo một task, bug, hoặc issue nào đó không, hoặc nội dung hội thoại có dẫn tới một hành động cần theo dõi trong hệ thống quản lý task không.
2. Nếu CÓ, hãy trả về kết quả dưới dạng JSON trong khối mã Markdown ```json ... ``` với các trường sau:
   - "should_create": true
   - "summary": Một tiêu đề ngắn gọn cho issue (lấy từ ngữ cảnh).
   - "description": Mô tả chi tiết cho issue (lấy từ ngữ cảnh).
   - "issuetype": "Task" (mặc định là Task trừ khi ngữ cảnh là Bug).
   - "duedate": "YYYY-MM-DD" (Nếu người dùng nhắc đến deadline hoặc các từ như "ngày mai", "thứ hai tới", hãy tính toán dựa trên ngày hiện tại {current_date}. Nếu không có nhắc đến, hãy để null).
3. Nếu KHÔNG cần tạo issue, hãy trả về:
   - "should_create": false
   - "reason": Lý do tại sao không tạo (ví dụ: người dùng chỉ đang chào hỏi hoặc đặt câu hỏi thông thường).

4. Luôn trả lời bằng văn phong chuyên nghiệp, tiếng Việt.
5. Project Key hiện tại là: {JIRA_PROJECT_KEY}
"""

async def create_jira_issue(issue_data: dict) -> str:
    """Gửi request POST để tạo issue Jira."""
    headers = {
        "Authorization": f"Bearer {JIRA_PERSONAL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    def build_payload(include_duedate=True):
        payload = {
            "fields": {
                "project": {
                    "key": f"{JIRA_PROJECT_KEY}"
                },
                "summary": issue_data.get("summary", "New Task from AI Assistant"),
                "issuetype": {
                    "name": issue_data.get("issuetype", "Task")
                },
                "description": issue_data.get("description", "No description provided.")
            }
        }
        if include_duedate and issue_data.get("duedate"):
            payload["fields"]["duedate"] = issue_data["duedate"]
        return payload

    try:
        async with httpx.AsyncClient() as client:
            # Lần thử 1: Có duedate (nếu có)
            payload = build_payload(include_duedate=True)
            response = await client.post(JIRA_SERVER_ISSUE_API, headers=headers, json=payload, timeout=30.0)
            
            # Nếu lỗi 400 liên quan đến duedate, thử lại không có duedate
            if response.status_code == 400 and "duedate" in response.text:
                print("Jira Error: duedate field not allowed. Retrying without duedate...")
                payload = build_payload(include_duedate=False)
                response = await client.post(JIRA_SERVER_ISSUE_API, headers=headers, json=payload, timeout=30.0)

            if response.status_code == 201:
                res_json = response.json()
                issue_key = res_json.get("key")
                base_url = JIRA_SERVER_ISSUE_API.split("/rest/api/")[0]
                issue_link = f"{base_url}/browse/{issue_key}"
                return f"✅ Issue đã được tạo thành công: [{issue_key}]({issue_link})"
            else:
                return f"❌ Lỗi khi tạo issue trên Jira: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Lỗi hệ thống khi gọi Jira API: {str(e)}"

async def exec(skill, curret_message, list_current_msg, list_summary_chat, unique_urls,contents_from_url):
    """
    Hành động chính của skill Jira:
    1. Phân tích ngữ cảnh.
    2. Gọi Gemini để quyết định tạo issue.
    3. Thực hiện tạo issue nếu cần.
    4. Gửi kết quả lại cho người dùng.
    """
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
    
    # 3. Gọi Gemini
    try:
        response = clientGemini.models.generate_content(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(
                temperature=0.0,
                system_instruction=JIRA_SYSTEM_INSTRUCTION,
                response_mime_type="application/json"
            ),
            contents=[types.Content(role="user", parts=user_parts)]
        )
        
        gemini_reply = response.text
        if not gemini_reply:
             return
             
        decision = json.loads(gemini_reply)
        print(f"Jira Skill Decision: {decision}")
        
        if decision.get("should_create"):
            result_msg = await create_jira_issue(decision)
            await bot_telegram.send_telegram_message(chat_id, result_msg)
        else:
            # Nếu không tạo, có thể không cần gửi gì hoặc chỉ log
            print(f"Jira Skill: Not creating issue. Reason: {decision.get('reason')}")
            
    except Exception as e:
        print(f"Jira Skill overall error: {e}")
        # Không nhất thiết phải báo lỗi cho user nếu đây là hậu trường, 
        # nhưng nếu user yêu cầu trực tiếp mà lỗi thì nên báo.
        # Ở đây ta báo lỗi để dễ debug.
        await bot_telegram.send_telegram_message(chat_id, f"Đã xảy ra lỗi khi xử lý yêu cầu Jira: {str(e)}")
