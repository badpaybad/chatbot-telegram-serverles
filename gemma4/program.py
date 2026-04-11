import os
import sys
import base64
import io
import json
import uuid
import torch
from typing import List, Optional, Union, Dict, Any
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from PIL import Image
import uvicorn

# Thêm thư mục gốc vào path để import gemma4 như một package
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from gemma4.manager import get_manager
from gemma4.tools import Gemma4Tools
from gemma4.tts import save_tts
from gemma4.stt import transcribe_audio
from gemma4.files import read_file_content

app = FastAPI(title="Gemma 4 Omni-File API")

# Cấu hình folder
TEMP_DIR = os.path.join(project_root, "temp")
OUTPUT_DIR = os.path.join(project_root, "output")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Gemini API Schemas ---

class Blob(BaseModel):
    mime_type: str
    data: str  # base64 encoded string

class FunctionCall(BaseModel):
    name: str
    args: Dict[str, Any]

class FunctionResponse(BaseModel):
    name: str
    response: Dict[str, Any]

class Part(BaseModel):
    text: Optional[str] = None
    inline_data: Optional[Blob] = None
    function_call: Optional[FunctionCall] = None
    function_response: Optional[FunctionResponse] = None

class Content(BaseModel):
    role: str  # "user" or "model"
    parts: List[Part]

class Tool(BaseModel):
    function_declarations: Optional[List[Dict[str, Any]]] = None

class GenerateContentRequest(BaseModel):
    contents: List[Content]
    tools: Optional[List[Tool]] = None
    system_instruction: Optional[Content] = None
    # generationConfig, safetySettings ... (optional for now)

class Candidate(BaseModel):
    content: Content
    finishReason: str = "STOP"
    index: int = 0

class GenerateContentResponse(BaseModel):
    candidates: List[Candidate]
    # usageMetadata ...

# --- Helpers ---

def get_gemma_manager():
    return get_manager()

def process_omni_parts(parts: List[Part]):
    """
    Trích xuất text, images, audio từ các Part.
    Nếu là Document, sẽ parse text và gộp vào prompt.
    """
    prompt_segments = []
    images = []
    audios = []
    
    for part in parts:
        if part.text:
            prompt_segments.append(part.text)
        elif part.inline_data:
            mime = part.inline_data.mime_type
            raw_data = base64.b64decode(part.inline_data.data)
            
            if mime.startswith("image/"):
                img = Image.open(io.BytesIO(raw_data)).convert("RGB")
                images.append(img)
            elif mime.startswith("audio/"):
                import librosa
                audio_data, _ = librosa.load(io.BytesIO(raw_data), sr=16000)
                audios.append(audio_data)
            elif mime.startswith("video/"):
                # Sơ bộ: Trích xuất audio từ video bằng librosa (nếu có thể)
                # Tương lai: Frame sampling bằng opencv
                try:
                    import librosa
                    audio_data, _ = librosa.load(io.BytesIO(raw_data), sr=16000)
                    audios.append(audio_data)
                except:
                    pass
            else:
                # Xử lý Documents (PDF, Office, ...)
                # Lưu tạm file để gọi files.py
                ext = ".txt"
                if "pdf" in mime: ext = ".pdf"
                elif "docx" in mime: ext = ".docx"
                elif "xlsx" in mime: ext = ".xlsx"
                elif "pptx" in mime: ext = ".pptx"
                elif "csv" in mime: ext = ".csv"
                
                tmp_filename = f"upload_{uuid.uuid4()}{ext}"
                tmp_path = os.path.join(TEMP_DIR, tmp_filename)
                
                with open(tmp_path, "wb") as f:
                    f.write(raw_data)
                
                try:
                    file_text = read_file_content(tmp_path)
                    prompt_segments.append(f"\n[Nội dung file đính kèm ({mime})]:\n{file_text}\n")
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                
    return "\n".join(prompt_segments), images, audios

def convert_to_gemma_messages(request: GenerateContentRequest):
    """Chuyển đổi từ Gemini Contents sang Gemma 4 Messages format."""
    gemma_messages = []
    
    # Xử lý System Instruction nếu có
    if request.system_instruction and request.system_instruction.parts:
        sys_text = " ".join([p.text for p in request.system_instruction.parts if p.text])
        if sys_text:
            # Gemma 4 thường không có role 'system' riêng biệt mà gộp vào user message đầu tiên 
            # hoặc sử dụng template hỗ trợ. Ở đây ta giả định template của gemma 4 hỗ trợ role system
            # hoặc ta sẽ prepend vào tin nhắn đầu tiên.
            gemma_messages.append({"role": "system", "content": [{"type": "text", "text": sys_text}]})

    for content in request.contents:
        role = "user" if content.role == "user" else "assistant" # Gemini dùng 'model', Gemma dùng 'assistant' hoặc 'model' tùy template
        # Đối với Gemma 4 IT, role thường là 'user' và 'model'
        role = "user" if content.role == "user" else "model"
        
        parts_list = []
        for part in content.parts:
            if part.text:
                parts_list.append({"type": "text", "text": part.text})
            if part.inline_data:
                if part.inline_data.mime_type.startswith("image/"):
                    parts_list.append({"type": "image"})
                elif part.inline_data.mime_type.startswith("audio/"):
                    parts_list.append({"type": "audio"})
        
        gemma_messages.append({"role": role, "content": parts_list})
        
    return gemma_messages

# --- Endpoints ---

from fastapi.responses import FileResponse

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.post("/v1beta/models/gemma-4:generateContent", response_model=GenerateContentResponse)
async def generate_content(request: GenerateContentRequest, req: Request):
    manager = get_gemma_manager()
    
    # Base URL cho download
    base_url = str(req.base_url).rstrip("/")
    
    # 1. Trích xuất dữ liệu đa phương thức từ tin nhắn cuối cùng (nếu có)
    last_user_msg = None
    for msg in reversed(request.contents):
        if msg.role == "user":
            last_user_msg = msg
            break
            
    if not last_user_msg:
        raise HTTPException(status_code=400, detail="No user message found.")
        
    current_prompt, images, audios = process_omni_parts(last_user_msg.parts)
    
    # 2. Định nghĩa Tool mặc định cho việc tạo file
    file_gen_tool = {
        "name": "generate_file",
        "description": "Tạo một file mới (csv, txt, md, v.v.) từ nội dung văn bản được cung cấp.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Tên file (ví dụ: data.csv)"},
                "content": {"type": "string", "description": "Nội dung văn bản bên trong file"}
            },
            "required": ["filename", "content"]
        }
    }

    # Gom tất cả tools từ request và thêm mặc định của hệ thống
    available_funcs = [file_gen_tool]
    if request.tools:
        for tool in request.tools:
            if tool.function_declarations:
                available_funcs.extend(tool.function_declarations)
    
    # 3. Kiểm tra Tool Call
    tool_engine = Gemma4Tools()
    match_results = tool_engine.match_tools(current_prompt, available_funcs)
    top_match = match_results[0] if match_results else None
    
    if top_match and top_match.get("score", 0) > 0.7 and top_match.get("function_name") != "none":
        func_name = top_match["function_name"]
        args = top_match.get("parameters", {})
        
        # Xử lý riêng tool generate_file
        if func_name == "generate_file":
            fname = args.get("filename", f"file_{uuid.uuid4()}.txt")
            fcontent = args.get("content", "")
            fpath = os.path.join(OUTPUT_DIR, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(fcontent)
            
            download_url = f"{base_url}/download/{fname}"
            response_text = f"Tôi đã tạo file thành công. Bạn có thể tải xuống tại đây: {download_url}"
            
            return GenerateContentResponse(
                candidates=[
                    Candidate(
                        content=Content(
                            role="model",
                            parts=[Part(text=response_text)]
                        ),
                        finishReason="STOP"
                    )
                ]
            )

        # Trả về Function Call chuẩn Gemini cho các tool khác
        return GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        role="model",
                        parts=[
                            Part(
                                function_call=FunctionCall(
                                    name=func_name,
                                    args=args
                                )
                            )
                        ]
                    ),
                    finishReason="STOP"
                )
            ]
        )

    # 4. Nếu không có tool call, sinh text bình thường (có hỗ trợ history)
    gemma_msgs = convert_to_gemma_messages(request)
    
    # Nếu prompt có kèm nội dung Document (đã được chèn vào current_prompt trong process_omni_parts)
    # Ta cần cập nhật lại phần text trong tin nhắn cuối của gemma_msgs
    if gemma_msgs and gemma_msgs[-1]["role"] == "user":
        for part in gemma_msgs[-1]["content"]:
            if part["type"] == "text":
                part["text"] = current_prompt
                break

    try:
        response_text = manager.generate(
            input_data=gemma_msgs, 
            audio_list=audios, 
            images_list=images
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

    return GenerateContentResponse(
        candidates=[
            Candidate(
                content=Content(
                    role="model",
                    parts=[Part(text=response_text)]
                ),
                finishReason="STOP"
            )
        ]
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "gemma-4"}

if __name__ == "__main__":
    # Load model pre-emptively
    print("[*] Pre-loading Gemma 4 model...")
    get_gemma_manager()
    
    port = 8000
    print(f"[*] Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
