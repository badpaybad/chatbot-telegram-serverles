import os
import sys
from gemma4.manager import get_manager

# Import config based on project structure
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

def generate_text(prompt: str, model_id: str = "google/gemma-4-e4b-it") -> str:
    """
    Hàm wrapper để tạo text từ input, sử dụng Gemma4Manager.
    """
    manager = get_manager(model_id)
    return manager.generate(prompt)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Câu hỏi: {query}")
        print(f"Trả lời: {generate_text(query)}")
    else:
        print("Sử dụng: python gemma4/llm.py <content>")
