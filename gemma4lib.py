import os
import sys
import uuid
import base64
import io
import datetime
import json
import time

# ROCm Optimization for Radeon 780M (gfx1102)
# MUST set environment variables BEFORE importing torch or gemma4.manager
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Add the 'gemma4' directory to PATH so bitsandbytes can find our 'rocminfo' shim
current_dir = os.path.dirname(os.path.abspath(__file__))
gemma4_dir = os.path.join(current_dir, "gemma4")
os.environ["PATH"] = gemma4_dir + os.pathsep + os.environ.get("PATH", "")

# Point to bundled ROCm libraries in torch if they exist
# Since gemma4lib.py is in the root, project_root is current_dir
project_root = current_dir
torch_lib_path = os.path.join(project_root, "venv/lib/python3.12/site-packages/torch/lib")
if os.path.exists(torch_lib_path):
    os.environ["LD_LIBRARY_PATH"] = torch_lib_path + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["ROCM_PATH"] = torch_lib_path

from typing import List, Optional, Union, Dict, Any, Callable
from pydantic import BaseModel, Field
from PIL import Image

# Ensure project_root is in path for imports
if project_root not in sys.path:
    sys.path.append(project_root)

from gemma4.manager import get_manager
from gemma4.tools import Gemma4Tools
from gemma4.files import read_file_content

# --- Internal File Store (for simulated Files API) ---
_FILES_STORE: Dict[str, Dict[str, Any]] = {}
TEMP_DIR = os.path.join(project_root, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Types Module (GenAI Compatible) ---

class types:
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
        inline_data: Optional["types.Blob"] = None
        file_data: Optional["types.FileData"] = None
        function_call: Optional["types.FunctionCall"] = None
        function_response: Optional["types.FunctionResponse"] = None

        @classmethod
        def from_text(cls, text: str):
            return cls(text=text)

        @classmethod
        def from_uri(cls, file_uri: str, mime_type: str):
            return cls(file_data=types.FileData(file_uri=file_uri, mime_type=mime_type))

    class Content(BaseModel):
        role: Optional[str] = "user"  # "user" or "model"
        parts: List["types.Part"]

    class Schema(BaseModel):
        type: str
        format: Optional[str] = None
        description: Optional[str] = None
        nullable: Optional[bool] = None
        enum: Optional[List[str]] = None
        items: Optional["types.Schema"] = None
        properties: Optional[Dict[str, "types.Schema"]] = None
        required: Optional[List[str]] = None

    class FunctionDeclaration(BaseModel):
        name: str
        description: str
        parameters: Optional["types.Schema"] = None

    class GoogleSearch(BaseModel):
        pass

    class Tool(BaseModel):
        google_search: Optional["types.GoogleSearch"] = None
        function_declarations: Optional[List[Union[Dict[str, Any], "types.FunctionDeclaration"]]] = None

    class FunctionCallingConfig(BaseModel):
        mode: str = "AUTO"

    class ToolConfig(BaseModel):
        function_calling_config: Optional["types.FunctionCallingConfig"] = None

    class ThinkingConfig(BaseModel):
        include_thoughts: Optional[bool] = False

    class GenerateContentConfig(BaseModel):
        temperature: Optional[float] = 0.7
        top_p: Optional[float] = 0.9
        top_k: Optional[int] = 40
        candidate_count: Optional[int] = 1
        max_output_tokens: Optional[int] = 1024
        stop_sequences: Optional[List[str]] = None
        response_mime_type: Optional[str] = "text/plain"
        response_json_schema: Optional[Dict[str, Any]] = None
        thinking_config: Optional["types.ThinkingConfig"] = None
        system_instruction: Optional[Union[str, "types.Content"]] = None
        tools: Optional[List["types.Tool"]] = None
        tool_config: Optional["types.ToolConfig"] = None

    class Candidate(BaseModel):
        content: "types.Content"
        finish_reason: str = "STOP"
        index: int = 0

    class UsageMetadata(BaseModel):
        prompt_token_count: int = 0
        candidates_token_count: int = 0
        total_token_count: int = 0

    class GenerateContentResponse(BaseModel):
        candidates: List["types.Candidate"]
        usage_metadata: Optional["types.UsageMetadata"] = None

        @property
        def text(self) -> str:
            if not self.candidates:
                return ""
            parts = self.candidates[0].content.parts
            return "".join([p.text for p in parts if p.text])

    class UploadFileConfig(BaseModel):
        mime_type: Optional[str] = None
        display_name: Optional[str] = None

    class State(BaseModel):
        name: str

    class FileMetadata(BaseModel):
        name: str
        display_name: Optional[str] = None
        mime_type: str
        size_bytes: int
        uri: str
        state: "types.State" = Field(default_factory=lambda: types.State(name="ACTIVE"))

# Resolve forward references
types.Part.model_rebuild()
types.Content.model_rebuild()
types.Tool.model_rebuild()
types.GenerateContentConfig.model_rebuild()
types.Candidate.model_rebuild()
types.GenerateContentResponse.model_rebuild()

# --- Helper logic for processing parts ---

def _process_parts_to_data(parts: List[types.Part]):
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
            # Handle simulated "files/..." or local paths
            file_id = file_uri.split("/")[-1]
            if file_id in _FILES_STORE:
                file_info = _FILES_STORE[file_id]
                mime = file_info["mime_type"]
                file_path = file_info["path"]
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        raw_data = f.read()
            elif os.path.exists(file_uri):
                 # Fallback if file_uri is a direct path
                 import mimetypes
                 mime, _ = mimetypes.guess_type(file_uri)
                 with open(file_uri, "rb") as f:
                     raw_data = f.read()
                
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
                # Document processing (PDF, etc.)
                ext = ".txt"
                if "pdf" in mime: ext = ".pdf"
                elif "docx" in mime: ext = ".docx"
                
                tmp_path = os.path.join(TEMP_DIR, f"lib_proc_{uuid.uuid4()}{ext}")
                try:
                    with open(tmp_path, "wb") as f:
                        f.write(raw_data)
                    file_text = read_file_content(tmp_path)
                    prompt_segments.append(f"\n[Nội dung file đính kèm ({mime})]:\n{file_text}\n")
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                
    return "\n".join(prompt_segments), images, audios

# --- Client Implementation ---

class Models:
    def __init__(self, manager):
        self.manager = manager
        self.tool_engine = Gemma4Tools()

    def generate_content(self, model: str, contents: List[types.Content], config: Optional[types.GenerateContentConfig] = None) -> types.GenerateContentResponse:
        config = config or types.GenerateContentConfig()
        
        # 1. Build messages history for manager
        gemma_messages = []
        
        # Handle system instruction
        sys_prompt = ""
        if config.system_instruction:
            if isinstance(config.system_instruction, str):
                sys_prompt = config.system_instruction
            else:
                s_txt, _, _ = _process_parts_to_data(config.system_instruction.parts)
                sys_prompt = s_txt
        
        if sys_prompt:
            gemma_messages.append({"role": "system", "content": [{"type": "text", "text": sys_prompt}]})

        # Process conversation contents
        for content in contents:
            role = "user" if content.role == "user" else "model"
            text_content, images, audios = _process_parts_to_data(content.parts)
            
            parts_list = []
            if text_content:
                parts_list.append({"type": "text", "text": text_content})
            
            for _ in images: parts_list.append({"type": "image"})
            for _ in audios: parts_list.append({"type": "audio"})
            
            gemma_messages.append({"role": role, "content": parts_list})

        # 2. Extract current prompt and media for tool matching and multimodal input
        last_user_content = next((c for c in reversed(contents) if c.role == "user"), contents[-1])
        current_prompt, images, audios = _process_parts_to_data(last_user_content.parts)

        # 3. Handle Tools (Function Calling)
        available_funcs = []
        if config.tools:
            for tool in config.tools:
                if tool.function_declarations:
                    available_funcs.extend(tool.function_declarations)
        
        if available_funcs:
            match_results = self.tool_engine.match_tools(current_prompt, available_funcs)
            top_match = match_results[0] if match_results else None
            
            if top_match and top_match.get("score", 0) > 0.8 and top_match.get("function_name") != "none":
                func_name = top_match["function_name"]
                args = top_match.get("parameters", {})
                
                fc = types.FunctionCall(name=func_name, args=args)
                part = types.Part(function_call=fc)
                candidate = types.Candidate(content=types.Content(role="model", parts=[part]))
                return types.GenerateContentResponse(candidates=[candidate])

        # 4. Standard Generation
        try:
            response_text = self.manager.generate(
                input_data=gemma_messages,
                images_list=images,
                audio_list=audios,
                max_tokens=config.max_output_tokens or 1024
            )
        except Exception as e:
            response_text = f"Lỗi sinh nội dung: {str(e)}"

        return types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(role="model", parts=[types.Part(text=response_text)]))]
        )

class Files:
    def upload(self, file: str, config: Optional[types.UploadFileConfig] = None) -> types.FileMetadata:
        if not os.path.exists(file):
            raise FileNotFoundError(f"File not found: {file}")
            
        file_id = f"file-{uuid.uuid4()}"
        dest_path = os.path.join(TEMP_DIR, file_id)
        
        import shutil
        shutil.copy2(file, dest_path)
        
        import mimetypes
        mime_type = (config and config.mime_type) or mimetypes.guess_type(file)[0] or "application/octet-stream"
        
        meta = {
            "name": f"files/{file_id}",
            "display_name": (config and config.display_name) or os.path.basename(file),
            "mime_type": mime_type,
            "path": dest_path,
            "size_bytes": os.path.getsize(dest_path),
            "uri": f"files/{file_id}"
        }
        _FILES_STORE[file_id] = meta
        return types.FileMetadata(**meta)

    def get(self, name: str) -> types.FileMetadata:
        file_id = name.split("/")[-1]
        if file_id not in _FILES_STORE:
            raise KeyError(f"File metadata not found: {name}")
        return types.FileMetadata(**_FILES_STORE[file_id])

class Client:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.manager = get_manager()
        self.models = Models(self.manager)
        self.files = Files()

# --- Drop-in Compatibility Exports ---

class genai:
    Client = Client

# Ensure 'from gemma4lib import types' and 'from gemma4lib import genai' works
__all__ = ["genai", "types", "Client"]
