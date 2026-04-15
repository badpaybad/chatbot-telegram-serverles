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

# --- Gemini API Schemas (v1beta Compatible) ---

class Blob(BaseModel):
    mime_type: str
    data: str  # base64 encoded string

class FileData(BaseModel):
    mime_type: Optional[str] = None
    file_uri: str

class FunctionCall(BaseModel):
    name: str
    args: Dict[str, Any]

class FunctionResponse(BaseModel):
    name: str
    response: Dict[str, Any]

class Part(BaseModel):
    text: Optional[str] = None
    inline_data: Optional[Blob] = None
    file_data: Optional[FileData] = None
    function_call: Optional[FunctionCall] = None
    function_response: Optional[FunctionResponse] = None

class Content(BaseModel):
    role: Optional[str] = "user"  # "user" or "model"
    parts: List[Part]

class Tool(BaseModel):
    function_declarations: Optional[List[Dict[str, Any]]] = None

class ThinkingConfig(BaseModel):
    include_thoughts: Optional[bool] = False

class GenerationConfig(BaseModel):
    temperature: Optional[float] = 0.7
    topP: Optional[float] = 0.9
    topK: Optional[int] = 40
    candidateCount: Optional[int] = 1
    maxOutputTokens: Optional[int] = 1024
    stopSequences: Optional[List[str]] = None
    responseMimeType: Optional[str] = "text/plain"
    responseJsonSchema: Optional[Dict[str, Any]] = None
    thinkingConfig: Optional[ThinkingConfig] = None

class GenerateContentRequest(BaseModel):
    contents: List[Content]
    tools: Optional[List[Tool]] = None
    system_instruction: Optional[Content] = None
    generationConfig: Optional[GenerationConfig] = None

class Candidate(BaseModel):
    content: Content
    finishReason: str = "STOP"
    index: int = 0

class UsageMetadata(BaseModel):
    promptTokenCount: int = 0
    candidatesTokenCount: int = 0
    totalTokenCount: int = 0

class GenerateContentResponse(BaseModel):
    candidates: List[Candidate]
    usageMetadata: Optional[UsageMetadata] = None

# --- Files API Schemas ---

class FileMetadata(BaseModel):
    name: str # e.g. "files/abc-123"
    displayName: Optional[str] = None
    mimeType: str
    sizeBytes: int
    createTime: str
    updateTime: str
    expirationTime: str
    uri: str # e.g. "https://domain/v1beta/files/abc-123"
    state: str = "ACTIVE"

# --- In-memory File Store (Simulating Files API) ---
# In a real scenario, this would be a DB or persistent storage
FILES_STORE: Dict[str, Dict[str, Any]] = {}

def get_file_path(file_id: str):
    return os.path.join(TEMP_DIR, file_id)

# --- Helpers ---

def get_gemma_manager():
    return get_manager()

def process_omni_parts(parts: List[Part]):
    """
    Trích xuất text, images, audio từ các Part.
    Hỗ trợ inline_data và file_data.
    Nếu là Document, sẽ parse text và gộp vào prompt.
    """
    prompt_segments = []
    images = []
    audios = []
    
    for part in parts:
        if part.text:
            prompt_segments.append(part.text)
        
        raw_data = None
        mime = None
        
        if part.inline_data:
            mime = part.inline_data.mime_type
            raw_data = base64.b64decode(part.inline_data.data)
        elif part.file_data:
            file_uri = part.file_data.file_uri
            file_id = file_uri.split("/")[-1]
            if file_id in FILES_STORE:
                file_info = FILES_STORE[file_id]
                mime = file_info["mimeType"]
                file_path = file_info["path"]
                with open(file_path, "rb") as f:
                    raw_data = f.read()
            else:
                continue # Hoặc báo lỗi file không tồn tại
                
        if raw_data and mime:
            if mime.startswith("image/"):
                img = Image.open(io.BytesIO(raw_data)).convert("RGB")
                images.append(img)
            elif mime.startswith("audio/"):
                import librosa
                audio_data, _ = librosa.load(io.BytesIO(raw_data), sr=16000)
                audios.append(audio_data)
            elif mime.startswith("video/"):
                try:
                    import librosa
                    audio_data, _ = librosa.load(io.BytesIO(raw_data), sr=16000)
                    audios.append(audio_data)
                except:
                    pass
            else:
                # Xử lý Documents (PDF, Office, ...)
                ext = ".txt"
                if "pdf" in mime: ext = ".pdf"
                elif "docx" in mime: ext = ".docx"
                elif "xlsx" in mime: ext = ".xlsx"
                elif "pptx" in mime: ext = ".pptx"
                elif "csv" in mime: ext = ".csv"
                
                tmp_filename = f"proc_{uuid.uuid4()}{ext}"
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
    
    # Pre-process system instructions
    merged_system_parts = []
    if request.system_instruction and request.system_instruction.parts:
        merged_system_parts.extend(request.system_instruction.parts)
        
    if merged_system_parts:
        sys_prompt, _, _ = process_omni_parts(merged_system_parts)
        if sys_prompt:
            gemma_messages.append({"role": "system", "content": [{"type": "text", "text": sys_prompt}]})

    for content in request.contents:
        role = "user" if content.role == "user" else "model"
        
        text_content, _, _ = process_omni_parts(content.parts)
        
        parts_list = []
        if text_content:
            parts_list.append({"type": "text", "text": text_content})
            
        # Kiểm tra media trong parts
        for part in content.parts:
            mime = None
            if part.inline_data: mime = part.inline_data.mime_type
            elif part.file_data:
                 fid = part.file_data.file_uri.split("/")[-1]
                 if fid in FILES_STORE: mime = FILES_STORE[fid]["mimeType"]
            
            if mime:
                if mime.startswith("image/"):
                    parts_list.append({"type": "image"})
                elif mime.startswith("audio/"):
                    parts_list.append({"type": "audio"})
        
        gemma_messages.append({"role": role, "content": parts_list})
        
    return gemma_messages

# --- Files API Endpoints ---
from fastapi import UploadFile, File
import datetime

@app.post("/v1beta/files", response_model=FileMetadata)
async def upload_file(req: Request, file: UploadFile = File(...)):
    file_id = f"file-{uuid.uuid4()}"
    file_info = {
        "name": f"files/{file_id}",
        "displayName": file.filename,
        "mimeType": file.content_type,
        "path": os.path.join(TEMP_DIR, file_id),
        "createTime": datetime.datetime.now().isoformat() + "Z",
        "updateTime": datetime.datetime.now().isoformat() + "Z",
        "expirationTime": (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat() + "Z",
        "state": "ACTIVE"
    }
    
    # Save file
    with open(file_info["path"], "wb") as f:
        f.write(await file.read())
    
    file_info["sizeBytes"] = os.path.getsize(file_info["path"])
    
    base_url = str(req.base_url).rstrip("/")
    file_info["uri"] = f"{base_url}/v1beta/files/{file_id}"
    
    FILES_STORE[file_id] = file_info
    
    # Return metadata according to Gemini spec
    return FileMetadata(**file_info)

@app.get("/v1beta/files/{file_id}", response_model=FileMetadata)
async def get_file_metadata(file_id: str):
    if file_id not in FILES_STORE:
        raise HTTPException(status_code=404, detail="File not found")
    return FileMetadata(**FILES_STORE[file_id])

@app.delete("/v1beta/files/{file_id}")
async def delete_file(file_id: str):
    if file_id in FILES_STORE:
        path = FILES_STORE[file_id]["path"]
        if os.path.exists(path):
            os.remove(path)
        del FILES_STORE[file_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="File not found")

# --- Endpoints ---

from fastapi.responses import FileResponse, StreamingResponse

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.post("/v1beta/models/{model}:generateContent", response_model=GenerateContentResponse)
async def generate_content(model: str, request: GenerateContentRequest, req: Request):
    manager = get_gemma_manager()
    base_url = str(req.base_url).rstrip("/")
    
    # 1. Trích xuất input data (Messages, Images, Audios)
    gemma_msgs = convert_to_gemma_messages(request)
    
    # Lấy prompt, images, audios từ tin nhắn cuối để hỗ trợ multimodal engine của manager
    last_user_msg = None
    for msg in reversed(request.contents):
        if msg.role == "user":
            last_user_msg = msg
            break
            
    if not last_user_msg:
         raise HTTPException(status_code=400, detail="No user message found.")
         
    current_prompt, images, audios = process_omni_parts(last_user_msg.parts)
    
    # 2. Xử lý Tools / Function Calling
    available_funcs = []
    if request.tools:
        for tool in request.tools:
            if tool.function_declarations:
                available_funcs.extend(tool.function_declarations)
    
    # Thêm default tool generate_file nếu chưa có
    if not any(f["name"] == "generate_file" for f in available_funcs):
        available_funcs.append({
            "name": "generate_file",
            "description": "Tạo một file mới (csv, txt, md) từ nội dung văn bản.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Tên file"},
                    "content": {"type": "string", "description": "Nội dung văn bản"}
                },
                "required": ["filename", "content"]
            }
        })

    tool_engine = Gemma4Tools()
    match_results = tool_engine.match_tools(current_prompt, available_funcs)
    top_match = match_results[0] if match_results else None
    
    if top_match and top_match.get("score", 0) > 0.7 and top_match.get("function_name") != "none":
        func_name = top_match["function_name"]
        args = top_match.get("parameters", {})
        
        if func_name == "generate_file":
            fname = args.get("filename", f"file_{uuid.uuid4()}.txt")
            fcontent = args.get("content", "")
            fpath = os.path.join(OUTPUT_DIR, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(fcontent)
            download_url = f"{base_url}/download/{fname}"
            response_text = f"Tôi đã tạo file thành công: {download_url}"
            return GenerateContentResponse(candidates=[Candidate(content=Content(role="model", parts=[Part(text=response_text)]))])

        # Trả về Function Call chuẩn Gemini
        return GenerateContentResponse(
            candidates=[Candidate(content=Content(role="model", parts=[Part(function_call=FunctionCall(name=func_name, args=args))]))]
        )

    # 3. Thực hiện sinh text
    config = request.generationConfig or GenerationConfig()
    try:
        response_text = manager.generate(
            input_data=gemma_msgs, 
            audio_list=audios, 
            images_list=images,
            max_tokens=config.maxOutputTokens or 1024
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

    return GenerateContentResponse(
        candidates=[Candidate(content=Content(role="model", parts=[Part(text=response_text)]))],
        usageMetadata=UsageMetadata(promptTokenCount=0, candidatesTokenCount=0, totalTokenCount=0)
    )

@app.post("/v1beta/models/{model}:streamGenerateContent")
async def stream_generate_content(model: str, request: GenerateContentRequest, req: Request):
    manager = get_gemma_manager()
    gemma_msgs = convert_to_gemma_messages(request)
    
    last_user_msg = next((msg for msg in reversed(request.contents) if msg.role == "user"), None)
    if not last_user_msg:
        raise HTTPException(status_code=400, detail="No user message found.")
    
    current_prompt, images, audios = process_omni_parts(last_user_msg.parts)
    config = request.generationConfig or GenerationConfig()

    async def event_generator():
        # Giả lập streaming bằng cách sinh toàn bộ text và chia nhỏ (do manager hiện tại không hỗ trợ stream generator)
        # Trong thực tế, manager.generate nên trả về một iterator
        try:
            full_response = manager.generate(
                input_data=gemma_msgs, 
                audio_list=audios, 
                images_list=images,
                max_tokens=config.maxOutputTokens or 1024
            )
            
            # Chia nhỏ text để giả lập stream
            words = full_response.split(" ")
            for i in range(0, len(words), 5):
                chunk_text = " ".join(words[i:i+5]) + (" " if i+5 < len(words) else "")
                chunk_resp = GenerateContentResponse(
                    candidates=[Candidate(content=Content(role="model", parts=[Part(text=chunk_text)]), finishReason="NONE")]
                )
                yield json.dumps(chunk_resp.dict()) + "\n"
                
            # Gửi chunk cuối cùng với STOP
            final_resp = GenerateContentResponse(
                candidates=[Candidate(content=Content(role="model", parts=[Part(text="")]), finishReason="STOP")]
            )
            yield json.dumps(final_resp.dict()) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "gemma-4", "capabilities": ["text", "audio", "vision", "files", "tools"]}

if __name__ == "__main__":
    print("[*] Pre-loading Gemma 4 model...")
    get_gemma_manager()
    port = 8000
    print(f"[*] Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
