# Tài liệu và Tổng hợp Code Gemma 4 (Cập nhật 2)

File này tổng hợp toàn bộ mã nguồn của module `gemma4` phục vụ cho hệ thống Telegram Chatbot Serverless, bao gồm hỗ trợ **Image Embedding**.

## 1. Cấu trúc thư mục
```
gemma4/
├── __init__.py      # Khởi tạo package
├── manager.py       # Quản lý Singleton Model & Processor (Text, Audio, Vision)
├── llm.py           # Text Generation
├── stt.py           # Speech to Text
├── tools.py         # Tool Call Scoring
├── embeddings.py    # Text/Image Embedding Wrapper
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
- Tool Call (Scoring System) sử dụng Gemma 4.
- Embedding (Vector) sử dụng Gemma 4 cho cả Text và Image.
"""

from .stt import transcribe_audio
from .llm import generate_text
from .manager import get_manager, Gemma4Manager
from .tools import match_tools, Gemma4Tools
from .embeddings import get_text_embedding, get_image_embedding

__all__ = [
    "transcribe_audio",
    "generate_text",
    "get_manager",
    "Gemma4Manager",
    "match_tools",
    "Gemma4Tools",
    "get_text_embedding",
    "get_image_embedding"
]
```

---

### 2.2. `gemma4/manager.py` (Trích đoạn xử lý Embedding)
```python
    def get_image_embeddings(self, image_path: str) -> list:
        """Trích xuất embedding từ hình ảnh, hỗ trợ Mean Pooling linh hoạt."""
        if not os.path.exists(image_path): raise FileNotFoundError(image_path)
        image = Image.open(image_path).convert("RGB")
        
        # Cung cấp text="" để tránh lỗi NoneType trong processor của Gemma 4
        inputs = self.processor(text="", images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            if hasattr(self.model, "model") and hasattr(self.model.model, "vision_tower"):
                # Lấy pixel_values và image_position_ids từ processor
                p_vals = inputs.get("pixel_values")
                p_pos = inputs.get("image_position_ids") or inputs.get("pixel_position_ids")
                
                vision_outputs = self.model.model.vision_tower(pixel_values=p_vals, pixel_position_ids=p_pos)
                image_features = vision_outputs.last_hidden_state
                
                # Chiếu sang không gian multimodal (2560 dims) nếu có projector
                if hasattr(self.model.model, "embed_vision"):
                    image_features = self.model.model.embed_vision(image_features)
            else:
                outputs = self.model(**inputs, output_hidden_states=True)
                image_features = outputs.hidden_states[0] if outputs.hidden_states else outputs[0]

            # Mean pooling xử lý linh hoạt 2D [tokens, hidden] hoặc 3D [batch, tokens, hidden]
            if image_features.dim() == 3:
                embeddings = torch.mean(image_features, dim=1)[0]
            elif image_features.dim() == 2:
                embeddings = torch.mean(image_features, dim=0)
            else:
                embeddings = image_features.flatten()

            return embeddings.cpu().tolist()
```

### 2.3. `gemma4/embeddings.py`
```python
import os
import sys
from gemma4.manager import get_manager

def get_text_embedding(text: str, model_id: str = "google/gemma-4-e4b-it") -> list:
    manager = get_manager(model_id)
    return manager.get_embeddings(text)

def get_image_embedding(image_path: str, model_id: str = "google/gemma-4-e4b-it") -> list:
    manager = get_manager(model_id)
    return manager.get_image_embeddings(image_path)
```
