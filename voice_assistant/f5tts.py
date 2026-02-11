import os
import soundfile as sf
from faster_whisper import WhisperModel
from f5_tts.api import F5TTS

# --- KHỞI TẠO CÁC MODEL (LOAD 1 LẦN DUY NHẤT) --- pip install faster-whisper soundfile
print("--- Đang nạp mô hình STT (Whisper) và TTS (F5)... ---")
device = "cuda"
# Dùng bản 'base' để nhanh, hoặc 'large-v3' để cực chính xác
stt_model = WhisperModel("base", device=device, compute_type="float16")
f5_tts = F5TTS(device=device)

def transcribe_voice(audio_path):
    """Hàm trích xuất Text từ âm thanh (STT)"""
    print(f"--- Đang nhận diện âm thanh: {audio_path} ---")
    segments, info = stt_model.transcribe(audio_path, beam_size=5, language="vi")
    text = "".join(segment.text for segment in segments)
    return text.strip()

def generate_voice_f5(reference_wav, text, output_path="response.wav"):
    """Hàm tạo giọng nói clone (TTS)"""
    try:
        # F5-TTS tự động nhận diện ngôn ngữ trong text
        wav, sr, _ = f5_tts.infer(
            ref_file=reference_wav,
            ref_text="",  # Có thể để trống
            gen_text=text
        )
        sf.write(output_path, wav, sr)
        return output_path
    except Exception as e:
        print(f"❌ Lỗi TTS: {e}")
        return None

# --- QUY TRÌNH CHẠY THỬ ---
if __name__ == "__main__":
    # 1. Giả sử bạn có file âm thanh người dùng gửi đến bot Telegram
    file_nguoi_dung = "user_voice_input.wav" 
    
    if os.path.exists(file_nguoi_dung):
        # BƯỚC 1: NGHE
        text_nhan_dien = transcribe_voice(file_nguoi_dung)
        print(f"💬 Nội dung bạn vừa nói: {text_nhan_dien}")

        # BƯỚC 2: XỬ LÝ (Bạn có thể đưa text này vào Ollama/Llama 3 ở đây)
        cau_tra_loi_cua_ai = f"Tôi đã nghe thấy bạn nói là: {text_nhan_dien}"

        # BƯỚC 3: NÓI (Clone lại bằng giọng của bạn)
        file_mau = "my_voice_sample.wav" # File giọng gốc của bạn
        if os.path.exists(file_mau):
            result = generate_voice_f5(file_mau, cau_tra_loi_cua_ai, "ai_reply.wav")
            print(f"✅ Đã tạo xong file phản hồi bằng giọng của bạn: {result}")
    else:
        print(f"Vui lòng chuẩn bị file {file_nguoi_dung} để thử nghiệm.")