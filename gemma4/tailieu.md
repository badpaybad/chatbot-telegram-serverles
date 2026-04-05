# Tài liệu và Tổng hợp Code Gemma 4

File này tổng hợp toàn bộ mã nguồn của module `gemma4` phục vụ cho hệ thống Telegram Chatbot Serverless.

## 1. Cấu trúc thư mục
```
gemma4/
├── __init__.py      # Khởi tạo package
├── manager.py       # Quản lý Singleton Model & Processor
├── llm.py           # Text Generation
├── stt.py           # Speech to Text
├── tools.py         # Tool Call Scoring
├── embeddings.py    # Text Embedding
└── requirements.md  # Yêu cầu hệ thống
```

---

## 2. Mã nguồn chi tiết

### 2.1. `gemma4/__init__.py`
```python
"""
Gemma4 Module - Cung cấp các chức năng AI cho Telegram Chatbot Serverless.
Bao gồm:
- STT (Speech to Text) sử dụng Gemma 4 Multimodal.
- LLM (Large Language Model) sử dụng Gemma 4.
- Tool Call (Scoring System) sử dụng Gemma 4 để ánh xạ yêu cầu người dùng.
- Embedding (Vector representation) sử dụng Gemma 4.
"""

from .stt import transcribe_audio
from .llm import generate_text
from .manager import get_manager, Gemma4Manager
from .tools import match_tools, Gemma4Tools
from .embeddings import get_text_embedding

__all__ = [
    "transcribe_audio",
    "generate_text",
    "get_manager",
    "Gemma4Manager",
    "match_tools",
    "Gemma4Tools",
    "get_text_embedding"
]
```

---

### 2.2. `gemma4/manager.py`
```python
import os
import torch
import sys
import threading
from transformers import AutoProcessor, AutoModelForMultimodalLM, AutoConfig

# Import config based on project structure
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

class Gemma4Manager:
    """
    Singleton Manager for loading the multimodal Gemma 4 model and processor once.
    Optimized for 16GB RAM constraints using low_cpu_mem_usage.
    Thread-safe implementation using Double-checked locking.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, model_id: str = "google/gemma-4-e4b-it"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # 1. Check HF Cache (Prio Offline)
                    cache_base = "/home/dunp/.cache/huggingface/hub/models--google--gemma-4-e4b-it/snapshots"
                    if os.path.exists(cache_base):
                        subfolders = [f for f in os.listdir(cache_base) if os.path.isdir(os.path.join(cache_base, f))]
                        if subfolders:
                            model_id = os.path.join(cache_base, subfolders[-1])
                            print(f"[*] Found HF cache snapshot: {model_id}")

                    # 2. Check Local Project Folder (fallback) 
                    if not os.path.isabs(model_id) or not os.path.exists(model_id):
                        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
                        if os.path.isdir(local_path) and os.listdir(local_path):
                             print(f"[*] Local project Gemma 4 model found: {local_path}")
                             model_id = local_path
                    
                    print(f"[*] Initializing Gemma4Manager for {model_id}...")
                    new_instance = super(Gemma4Manager, cls).__new__(cls)
                    new_instance._load_model(model_id)
                    cls._instance = new_instance
        return cls._instance

    def _load_model(self, model_id: str):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"[*] Loading Multimodal Model: {model_id} on {self.device}...")
        
        if self.device == "cuda":
            self.dtype = torch.bfloat16
        else:
            self.dtype = "auto"

        try:
            config = AutoConfig.from_pretrained(self.model_id, trust_remote_code=True)
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            self.model = AutoModelForMultimodalLM.from_pretrained(
                self.model_id,
                config=config,
                device_map=self.device,
                torch_dtype=self.dtype,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            ).eval() 
            print(f"[+] Multimodal model {model_id} loaded successfully.")
        except Exception as e:
            print(f"[-] ERROR loading gemma4 model: {str(e)}")
            raise e

    def generate(self, user_input: str, audio_array=None, max_tokens: int = 512, sampling_rate: int = 16000) -> str:
        if not hasattr(self, 'model') or self.model is None:
             return "Lỗi: Hệ thống AI chưa sẵn sàng."

        messages = [{"role": "user", "content": []}]
        if audio_array is not None:
            messages[0]["content"].append({"type": "audio"})
        
        messages[0]["content"].append({"type": "text", "text": f"{user_input}\n\nNote: Always answer in Vietnamese, naturally and concisely."})

        text_prompt = self.processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        
        if audio_array is not None:
            inputs = self.processor(text=text_prompt, audio=audio_array, sampling_rate=sampling_rate, return_tensors="pt").to(self.device)
        else:
            inputs = self.processor(text=text_prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            
        response = self.processor.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        return response.strip()

    def get_embeddings(self, text: str) -> list:
        if not hasattr(self, 'model') or self.model is None:
            raise RuntimeError("Lỗi: Hệ thống AI chưa sẵn sàng.")

        inputs = self.processor(text=text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
            last_hidden_state = outputs.hidden_states[-1] if hasattr(outputs, 'hidden_states') else outputs[0]

            attention_mask = inputs.get('attention_mask')
            if attention_mask is not None:
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
                sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, 1)
                sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                embeddings = sum_embeddings / sum_mask
            else:
                embeddings = torch.mean(last_hidden_state, dim=1)
            
            return embeddings[0].cpu().tolist()

def get_manager(model_id: str = "google/gemma-4-e4b-it"):
    return Gemma4Manager(model_id)
```

---

### 2.3. `gemma4/llm.py`
```python
import os
import sys
from gemma4.manager import get_manager

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

def generate_text(prompt: str, model_id: str = "google/gemma-4-e4b-it") -> str:
    manager = get_manager(model_id)
    return manager.generate(prompt)
```

---

### 2.4. `gemma4/stt.py`
```python
import os
import sys
import librosa
import numpy as np

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

from gemma4.manager import get_manager

def transcribe_audio(audio_file_path: str, model_id: str = "google/gemma-4-e4b-it") -> str:
    if not os.path.exists(audio_file_path):
        return f"Lỗi: File {audio_file_path} không tồn tại."

    try:
        audio_array, sampling_rate = librosa.load(audio_file_path, sr=16000, mono=True)
        audio_array = audio_array.astype(np.float32)
        manager = get_manager(model_id)
        prompt = "Hãy lắng nghe âm thanh đính kèm và chuyển đổi nó thành văn bản tiếng Việt chính xác nhất. Không giải thích gì thêm, chỉ trả về nội dung audio."
        transcription = manager.generate(prompt, audio_array=audio_array, sampling_rate=sampling_rate)
        return transcription.strip()
    except Exception as e:
        return f"Lỗi khi thực hiện Multimodal STT: {str(e)}"
```

---

### 2.5. `gemma4/tools.py`
```python
import json
import re
import os
import sys
import inspect
from typing import List, Dict, Any, Callable
from gemma4.manager import get_manager

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

class Gemma4Tools:
    def __init__(self, model_id: str = "google/gemma-4-e4b-it"):
        self.manager = get_manager(model_id)
        self.tools = []

    def add_tool(self, tool_def: Dict[str, Any]):
        if tool_def not in self.tools:
            self.tools.append(tool_def)

    def add_tool_from_func(self, func: Callable):
        try:
            name = func.__name__
            doc = inspect.getdoc(func) or "Không có mô tả."
            signature = inspect.signature(func)
            parameters = {k: (v.annotation.__name__ if hasattr(v.annotation, "__name__") else str(v.annotation)) 
                         for k, v in signature.parameters.items()}
            self.add_tool({"name": name, "description": doc, "parameters": parameters})
        except Exception as e:
            print(f"[-] Error: {str(e)}")

    def match_tools(self, user_input: str, tools_definitions: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        tools_list = tools_definitions if tools_definitions is not None else self.tools
        if not tools_list:
            return [{"function_name": "none", "score": 0, "reason": "Không có tool nào được đăng ký."}]

        tools_json = json.dumps(tools_list, indent=2, ensure_ascii=False)
        prompt = f"Phân tích intent và trích xuất tham số. Tools: {tools_json}. Yêu cầu: \"{user_input}\". Trả về JSON array [{{'function_name':..., 'score':..., 'reason':..., 'parameters':...}}]."
        raw_response = self.manager.generate(prompt, max_tokens=1024)
        
        try:
            match = re.search(r"(\[.*\])", raw_response, re.DOTALL) or re.search(r"(\{.*\})", raw_response, re.DOTALL)
            if match:
                result = json.loads(match.group(0))
                if isinstance(result, dict): result = [result]
                result.sort(key=lambda x: x.get('score', 0), reverse=True)
                return result
            return [{"function_name": "unknown", "score": 0, "reason": "Không phân tích được JSON"}]
        except Exception as e:
            return [{"function_name": "error", "score": 0, "reason": str(e)}]

def match_tools(user_input: str, tools_definitions: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return Gemma4Tools().match_tools(user_input, tools_definitions)
```

---

### 2.6. `gemma4/embeddings.py`
```python
import os
import sys
from gemma4.manager import get_manager

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

def get_text_embedding(text: str, model_id: str = "google/gemma-4-e4b-it") -> list:
    manager = get_manager(model_id)
    return manager.get_embeddings(text)
```
