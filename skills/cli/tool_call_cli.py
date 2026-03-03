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

# Prompt for generating bash commands 6. Nếu một lệnh không khả dụng hoặc chưa có sẵn trong máy tính, hãy cố gắng không dùng sudo để cài đặt nó bằng `apt-get install -y <package>` hoặc  `pip install -y <package>` hoặc `npm install -y <package>`. Nếu việc cài đặt thất bại hoặc không thể thực hiện, hãy thông báo rõ ràng cho người dùng biết họ cần cài đặt thủ công.

CLI_SYSTEM_INSTRUCTION = """
Bạn là một chuyên gia về Linux Bash Shell. 
Nhiệm vụ của bạn là chuyển đổi yêu cầu từ người dùng thành các lệnh bash shell thực thi được trên môi trường Linux.

Dữ liệu đầu vào sẽ bao gồm:
- [Summarized History]: Tóm tắt lịch sử hội thoại.
- [Recent Messages]: Các tin nhắn gần đây.
- [Current Message]: Tin nhắn hiện tại của người dùng.
- [URLs]: Các đường dẫn liên quan (nếu có).
- Các file được gửi kèm (nếu có).

Yêu cầu kỹ thuật:
1. **BẮT BUỘC**: Đặt toàn bộ các lệnh bash shell cần thực thi vào trong các khối mã Markdown (ví dụ: ```bash [lệnh ở đây] ```).
2. Giải thích ngắn gọn mục đích của các lệnh bên ngoài khối mã.
3. Chỉ sử dụng các lệnh an toàn. Tuyệt đối không chạy các lệnh nguy hiểm tới hệ thống và phá vỡ bảo mật (ví dụ: sudo rm -rf /).
4. Nếu yêu cầu không liên quan đến CLI hoặc không thể thực hiện qua bash shell, hãy trả lời bình thường.
5. Luôn trả lời bằng tiếng Việt.
6. Nếu một lệnh chạy quá 15 giây hoặc không thể dừng lại, hãy kill process đó, rồi thông báo rõ ràng cho người dùng biết họ cần cài đặt thủ công.
7. Không cho phép đọc nội dung file source code python, c# , java, typescript,php ... 
8. Không cho phép đọc nội dung file cấu hình vd .env appsettings.json ... các folder file hiden vd ở linux .git, .vscode, .idea, .swaksrc ...
9. **Bắt buộc** các lệnh sinh ra sẽ không cần sudo để chạy 
10. Nếu có gửi email thì dùng swaks và ~/.swaksrc
11. Các nội dung sinh ra để trả về hoặc gửi đi cho người dùng phải là tiếng việt unicode đầy đủ dấu câu
12. Nếu gọi api lấy dữ liệu hay lấy nội dung từ url thì dùng curl


Ví dụ:
Người dùng: "liệt kê các file trong thư mục hiện tại"
Trả lời:
"Dưới đây là lệnh để liệt kê các file:
```bash
ls -la
```"
"""

CLI_INTERPRETER_INSTRUCTION = """
Bạn là một trợ lý AI chuyên về giải thích kết quả thực thi lệnh Linux Bash Shell.
Nhiệm vụ của bạn là nhận vào [Lệnh đã thực hiện] và [Kết quả thực thi] (bao gồm Output và Error), sau đó diễn giải kết quả đó một cách dễ đọc, súc tích và có ý nghĩa cho người dùng.

Yêu cầu:
1. Tập trung vào ý nghĩa của kết quả đối với yêu cầu ban đầu của người dùng.
2. Nếu có lỗi (Error), hãy giải thích ngắn gọn nguyên nhân và gợi ý hướng khắc phục nếu có thể.
3. Nếu output quá dài, hãy tóm tắt các điểm quan trọng nhất.
4. Trả lời bằng tiếng Việt, ngôn ngữ tự nhiên, súc tích.
5. Không cần nhắc lại toàn bộ output nếu không cần thiết.
6. Nếu kết quả là rỗng nhưng lệnh chạy thành công, hãy xác nhận lệnh đã thực hiện xong mục tiêu.
"""

def extract_bash_commands(text: str) -> str:
    """Trích xuất các lệnh từ khối mã ```bash ... ``` hoặc ``` ... ```."""
    if not text:
        return ""
    # Tìm ```bash ... ```
    bash_matches = re.findall(r"```bash\s+(.*?)\s+```", text, re.DOTALL)
    if bash_matches:
        return "\n".join(bash_matches).strip()
    
    # Tìm khối mã không có nhãn ``` ... ```
    generic_matches = re.findall(r"```\s+(.*?)\s+```", text, re.DOTALL)
    if generic_matches:
        return "\n".join(generic_matches).strip()
    
    return ""

async def execute_bash_shell(commands: str) -> str:
    """Thực thi chuỗi lệnh bash và trả về output/error."""
    if not commands:
        return ""
        
    print(f"--- Đang thực thi lệnh CLI: ---\n{commands}")
    output = ""
    try:
        process = await asyncio.create_subprocess_shell(
            commands,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            # Thiết lập timeout 60 giây cho việc thực thi lệnh
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15.0)
        except asyncio.TimeoutError:
            # Nếu quá thời gian, kill process
            try:
                process.kill()
            except ProcessLookupError:
                pass
            output += "**Cảnh báo:** Lệnh thực thi quá lâu (vượt quá 15 giây) nên hệ thống đã tự động dừng nó. Vui lòng kiểm tra lại lệnh hoặc thực hiện cài đặt/chạy thủ công trên terminal của bạn."

        if stdout:
            output += f"**Output:**\n```\n{stdout.decode().strip()}\n```\n"
        if stderr:
            output += f"**Error:**\n```\n{stderr.decode().strip()}\n```\n"
            
        if not output:
            output += "Lệnh đã chạy xong nhưng không có output trả về."
            
    except Exception as e:
        output += f"Lỗi hệ thống khi thực thi: {str(e)}"

    return output

async def exec(skill, curret_message, list_current_msg, list_summary_chat, unique_urls,contents_from_url):
    """
    Hành động chính của skill CLI:
    1. Xây dựng prompt context.
    2. Gọi Gemini để sinh lệnh.
    3. Parse lệnh và thực thi.
    4. Gửi kết quả lại cho người dùng.
    """
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

    # 3. Gọi Gemini
    try:
        response = clientGemini.models.generate_content(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(
                temperature=0.0,
                system_instruction=CLI_SYSTEM_INSTRUCTION
            ),
            contents=[types.Content(role="user", parts=user_parts)]
        )
        
        gemini_reply = response.text
        if not gemini_reply:
             gemini_reply = "Gemini không trả về nội dung nào."
             
        print(f"Gemini CLI Response: {gemini_reply}")
        
        # 4. Trích xuất và thi hành
        commands = extract_bash_commands(gemini_reply)
        exec_result = ""
        interpreted_result = ""
        if commands:
            exec_result = await execute_bash_shell(commands)
            
            # 4.5 Gọi Gemini để diễn giải kết quả
            try:
                interpretation_context = f"### [Lệnh đã thực hiện]\n```bash\n{commands}\n```\n\n### [Kết quả thực thi]\n{exec_result}"
                interpretation_response = clientGemini.models.generate_content(
                    model=GEMINI_MODEL,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        system_instruction=CLI_INTERPRETER_INSTRUCTION
                    ),
                    contents=[types.Content(role="user", parts=[types.Part.from_text(text=interpretation_context)])]
                )
                interpreted_result = interpretation_response.text
            except Exception as e:
                print(f"CLI Result Interpretation error: {e}")
                interpreted_result = f"(Không thể diễn giải kết quả do lỗi AI: {str(e)})"
            
        # 5. Phản hồi người dùng
        final_msg = gemini_reply
        if interpreted_result:
            final_msg += f"\n\n---\n### [Giải thích kết quả]\n{interpreted_result}"
        elif exec_result:
            # Fallback nếu không có diễn giải nhung có kết quả thô
            final_msg += f"\n\n---\n### [Kết quả thực thi]\n{exec_result}"
            
        await bot_telegram.send_telegram_message(chat_id, final_msg)
        
    except Exception as e:
        print(f"CLI Skill overall error: {e}")
        await bot_telegram.send_telegram_message(chat_id, f"Đã xảy ra lỗi khi thực thi yêu cầu CLI: {str(e)}")
