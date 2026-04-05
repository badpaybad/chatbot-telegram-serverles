import os
import sys
import librosa
import numpy as np

# Import config based on project structure
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

# Import shared manager
from gemma4.manager import get_manager

def transcribe_audio(audio_file_path: str, model_id: str = "google/gemma-4-e4b-it") -> str:
    """
    Chuyển đổi file âm thanh thành văn bản sử dụng mô hình Multimodal Gemma 4.
    Yêu cầu: nạp âm thanh 16kHz mono.
    
    Args:
        audio_file_path (str): Đường dẫn đến file âm thanh.
        model_id (str): ID của mô hình Gemma 4.
    
    Returns:
        str: Văn bản đã được chuyển đổi (Tiếng Việt).
    """
    if not os.path.exists(audio_file_path):
        return f"Lỗi: File {audio_file_path} không tồn tại."

    try:
        print(f"[*] Đang nạp và tiền xử lý âm thanh (16kHz, mono): {audio_file_path}")
        # Nạp âm thanh và tự động đưa về 16kHz, mono
        audio_array, sampling_rate = librosa.load(audio_file_path, sr=16000, mono=True)
        
        # Đảm bảo là float32 và nằm trong khoảng [-1, 1] (librosa mặc định thực hiện việc này)
        audio_array = audio_array.astype(np.float32)

        # Sử dụng manager singleton để lấy model/processor
        manager = get_manager(model_id)
        
        # Prompt yêu cầu trích xuất text từ âm thanh bằng tiếng Việt
        prompt = "Hãy lắng nghe âm thanh đính kèm và chuyển đổi nó thành văn bản tiếng Việt chính xác nhất. Không giải thích gì thêm, chỉ trả về nội dung audio."
        
        print(f"[*] Đang thực hiện Multimodal STT bằng {model_id}...")
        transcription = manager.generate(prompt, audio_array=audio_array, sampling_rate=sampling_rate)
        
        return transcription.strip()
        
    except Exception as e:
        return f"Lỗi khi thực hiện Multimodal STT: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(transcribe_audio(test_file))
    else:
        print("Sử dụng: python gemma4/stt.py <path_to_audio_file>")
