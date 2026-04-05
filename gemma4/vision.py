import os
from gemma4.manager import get_manager

def describe_image(image_path: str, model_id: str = "google/gemma-4-e4b-it") -> str:
    """
    Tạo mô tả chi tiết cho hình ảnh bằng tiếng Việt.
    """
    if not os.path.exists(image_path):
        return f"Lỗi: Không tìm thấy file ảnh tại {image_path}"
    
    manager = get_manager(model_id)
    prompt = "Mô tả hình ảnh này một cách chi tiết và sinh động bằng tiếng Việt."
    return manager.generate_with_image(image_path, prompt)

def query_image(image_path: str, prompt: str, model_id: str = "google/gemma-4-e4b-it") -> str:
    """
    Thao tác với file ảnh (hỏi đáp, phân tích) theo yêu cầu (prompt).
    """
    if not os.path.exists(image_path):
        return f"Lỗi: Không tìm thấy file ảnh tại {image_path}"
    
    manager = get_manager(model_id)
    return manager.generate_with_image(image_path, prompt)
