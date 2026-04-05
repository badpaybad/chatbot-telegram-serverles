"""
Gemma4 Module - Cung cấp các chức năng AI cho Telegram Chatbot Serverless.
Bao gồm:
- STT (Speech to Text) sử dụng Gemma 4 Multimodal.
- LLM (Large Language Model) sử dụng Gemma 4.
- Tool Call (Scoring System) sử dụng Gemma 4.
- Embedding (Vector) sử dụng Gemma 4 cho cả Text và Image.
- Vision Analysis: Mô tả ảnh và VQA.
- File Analysis: Đọc và phân tích PDF, DOCX, PPTX, XLSX, CSV, TXT.
"""

from .stt import transcribe_audio
from .llm import generate_text
from .manager import get_manager, Gemma4Manager
from .tools import match_tools, Gemma4Tools
from .embeddings import get_text_embedding, get_image_embedding
from .vision import describe_image, query_image
from .files import process_file_with_prompt, read_file_content

__all__ = [
    "transcribe_audio",
    "generate_text",
    "get_manager",
    "Gemma4Manager",
    "match_tools",
    "Gemma4Tools",
    "get_text_embedding",
    "get_image_embedding",
    "describe_image",
    "query_image",
    "process_file_with_prompt",
    "read_file_content"
]
