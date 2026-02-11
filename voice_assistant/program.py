import os
import torch
import sounddevice as sd
from faster_whisper import WhisperModel
import ollama
from TTS.api import TTS

# --- CẤU HÌNH ---
MODEL_STT = "base" # Có thể dùng 'large-v3' nếu máy mạnh
LLM_NAME = "llama3" # Hoặc 'vistral' cho tiếng Việt tốt hơn
VOICE_SAMPLE = "my_voice.wav" # File record giọng của bạn (dài khoảng 10s)

# Khởi tạo mô hình STT (Chạy trên GPU/CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
# stt_model = WhisperModel(MODEL_STT, device=device, compute_type="float16")
# Cách 1: Sử dụng int8 (Khuyên dùng cho CPU để đạt tốc độ cao)
stt_model = WhisperModel(MODEL_STT, device="cpu", compute_type="int8")

# Cách 2: Sử dụng float32 (Chậm hơn nhưng độ chính xác cao nhất)
# stt_model = WhisperModel(MODEL_STT, device="cpu", compute_type="float32")

# Khởi tạo mô hình TTS (XTTSv2 hỗ trợ Clone Voice)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

def speak(text):
    """Hàm clone giọng nói và phát ra loa"""
    tts.tts_to_file(text=text, 
                    speaker_wav=VOICE_SAMPLE, 
                    language="vi", 
                    file_path="output.wav")
    # Lệnh chạy file audio trên Windows/Linux
    os.system("start output.wav") if os.name == "nt" else os.system("aplay output.wav")

def listen():
    """Hàm ghi âm và chuyển thành văn bản"""
    print("\n[Hệ thống] Đang nghe...")
    # Trong thực tế, bạn có thể dùng thư viện RealtimeSTT để bắt tiếng tự động
    # Ở đây giả định bạn dùng whisper để dịch đoạn vừa nghe
    segments, _ = stt_model.transcribe("input_audio.wav", beam_size=5)
    text = "".join(segment.text for segment in segments)
    return text

def main():
    while True:
        # 1. Nhận diện giọng nói (Giả định bạn đã có cơ chế trigger ghi âm)
        user_input = input("Nhấn Enter để bắt đầu nói (hoặc gõ text): ") 
        # (Để đơn giản, tôi dùng input text, bạn có thể tích hợp sounddevice ghi âm)
        
        if user_input.lower() in ['exit', 'quit']: break

        # 2. Gửi tới LLM
        print(f"Bạn: {user_input}")
        response = ollama.chat(model=LLM_NAME, messages=[
            {'role': 'user', 'content': user_input},
        ])
        answer = response['message']['content']
        print(f"AI: {answer}")

        # 3. Phản hồi bằng giọng clone
        speak(answer)

if __name__ == "__main__":
    main()