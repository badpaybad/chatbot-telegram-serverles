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
