import os
import sys
from gemma4.manager import get_manager

# Import config based on project structure
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

def get_text_embedding(text: str, model_id: str = "google/gemma-4-e4b-it") -> list:
    """
    Hàm wrapper để lấy embedding của văn bản.
    """
    manager = get_manager(model_id)
    return manager.get_embeddings(text)

def get_image_embedding(image_path: str, model_id: str = "google/gemma-4-e4b-it") -> list:
    """
    Hàm wrapper để lấy embedding của hình ảnh.
    """
    manager = get_manager(model_id)
    return manager.get_image_embeddings(image_path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        embedding = get_text_embedding(text)
        print(f"Text: {text}")
        print(f"Embedding length: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    else:
        print("Sử dụng: python gemma4/embeddings.py <text>")
