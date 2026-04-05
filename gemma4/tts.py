import os
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from gemma4.manager import project_root
# echo "📥 Downloading Kokoro models..." && \
#     curl -L --progress-bar -o kokoro-v1.0.int8.onnx \
#     https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx && \
#     curl -L --progress-bar -o voices-v1.0.bin \
#     https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin && \
#     echo "✅ Models downloaded successfully"
class Gemma4TTS:
    def __init__(self, model_id: str = "kokoro-v1.0"):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.base_dir, "model", "kokoro", "kokoro-v1.0.onnx")
        self.voices_path = os.path.join(self.base_dir, "model", "kokoro", "voices.bin")
        
        if not os.path.exists(self.model_path) or not os.path.exists(self.voices_path):
            raise FileNotFoundError("Kokoro ONNX model or voices not found. Please run download_kokoro.py first.")
        
        self.kokoro = Kokoro(self.model_path, self.voices_path)

    def text_to_speech(self, text: str, output_path: str, voice: str = "af_sky", speed: float = 1.0):
        """
        Chuyển đổi văn bản sang giọng nói và lưu thành file wav.
        Mặc định sử dụng 'af_sky' kết hợp với espeak-ng tiếng Việt (vi).
        """
        try:
            # Kokoro-onnx tự động sử dụng espeak-ng nếu được cài đặt.
            # Với tiếng Việt, ta cần chỉ định ngôn ngữ 'vi' cho phonemizer nếu thư viện hỗ trợ.
            # Lưu ý: Kokoro-onnx 0.5.0 sử dụng language='vi' thông qua phonemizer.
            samples, sample_rate = self.kokoro.create(
                text, 
                voice=voice, 
                speed=speed, 
                lang="vi"
            )
            
            sf.write(output_path, samples, sample_rate)
            return output_path
        except Exception as e:
            print(f"[-] TTS Error: {e}")
            raise e

_tts_instance = None

def save_tts(text: str, filename: str = "output.wav", voice: str = "af_sarah") -> str:
    """
    Hàm tiện ích để lưu file TTS.
    """
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = Gemma4TTS()
    
    # Đảm bảo folder output tồn tại
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    return _tts_instance.text_to_speech(text, output_path, voice=voice)
