

# # import torch
# import functools

# # # Ghi đè phương thức torch.load để luôn đặt weights_only=False
# # torch.load = functools.partial(torch.load, weights_only=False)

# # from TTS.api import TTS # Import TTS sau khi đã ghi đè

# # 1. Thêm class này vào 'safe_globals' của PyTorch
# import torch
# torch.load = functools.partial(torch.load, weights_only=False)

# from TTS.api import TTS
# import os
# import torch
# from TTS.tts.configs.xtts_config import XttsConfig # Import class gây lỗi
# from TTS.api import TTS

# torch.serialization.add_safe_globals([XttsConfig])

# # Kiểm tra thiết bị xử lý (Ưu tiên GPU nếu có)
# device = "cuda" if torch.cuda.is_available() else "cpu"

# def generate_voice(reference_wav, text, output_path="output_clone.wav"):
#     """
#     Hàm clone giọng nói từ file gốc và lưu thành file mới.
    
#     Args:
#         reference_wav (str): Đường dẫn đến file giọng nói mẫu (.wav)
#         text (str): Nội dung văn bản cần đọc
#         output_path (str): Đường dẫn lưu file kết quả
#     """
#     try:
#         print(f"--- Đang khởi tạo mô hình XTTS v2 trên {device} ---")
#         # Khởi tạo model giống cách Voicebox backend thực hiện
#         tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

#         print(f"--- Đang xử lý Clone Voice ---")
#         # Voicebox sử dụng hàm tts_to_file để tối ưu tốc độ lưu trữ
#         tts.tts_to_file(
#             text=text,
#             speaker_wav=reference_wav,
#             language="vi", # Chuyển sang "en" nếu bạn đọc tiếng Anh
#             file_path=output_path
#         )
        
#         print(f"✅ Thành công! File đã lưu tại: {output_path}")
#         return os.path.abspath(output_path)

#     except Exception as e:
#         print(f"❌ Lỗi trong quá trình tạo giọng nói: {e}")
#         return None
    
# # # --- VÍ DỤ SỬ DỤNG ---
# # if __name__ == "__main__":
# #     # Đảm bảo file 'giong_cua_toi.wav' tồn tại ở cùng thư mục
# #     file_mau = "giong_cua_toi.wav" 
# #     noi_dung = "Xin chào, đây là giọng nói nhân bản của tôi chạy hoàn toàn trên máy tính cá nhân."
    
# #     if os.path.exists(file_mau):
# #         generate_voice(file_mau, noi_dung, "ket_qua_tieng_viet.wav")
# #     else:
# #         print(f"Vui lòng chuẩn bị file mẫu: {file_mau}")
import soundfile as sf
import os 
from f5_tts.api import F5TTS
def generate_voice_f5(reference_wav, text, output_path="output.wav"):
    """
    Sử dụng F5-TTS để clone giọng nói tiếng Việt.
    """
    try:
        print("--- Đang khởi tạo F5-TTS ---")
        # Khởi tạo model (Nên đưa ra ngoài nếu gọi nhiều lần)
        f5tts = F5TTS()

        print(f"--- Đang xử lý hội thoại (Tiếng Việt) ---")
        
        # F5-TTS .infer() trả về (wav, sample_rate, spectogram)
        wav, sr, _ = f5tts.infer(
            ref_file=reference_wav,
            # ref_text="Thông báo nhắc con làm tiếp vở bài tập toán tiếng Việt tuần 22, tiếp tục văn kể lại một sự việc học sinh chứng kiến hoặc tham gia học thuộc bảng chia 2 chia 5. học sinh chưa chụp ảnh mặc áo dài chụp tiếp", # Có thể để trống nếu không có script file mẫu
             ref_text="Thông báo nhắc con làm tiếp vở bài tập toán tiếng Việt tuần hai hai, tiếp tục văn kể lại một sự việc học sinh chứng kiến hoặc tham gia học thuộc bảng chia hai chia năm", # Có thể để trống nếu không có script file mẫu
          #  ref_text="",
           gen_text=text
           
        )

        # Lưu mảng âm thanh ra file .wav
        sf.write(output_path, wav, sr)
        
        print(f"✅ Thành công! File lưu tại: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Lỗi F5-TTS: {e}")
        return None
    
file_mau = "giong_cua_toi.wav" 
noi_dung = "Xin chào, đây là giọng nói nhân bản của tôi chạy hoàn toàn trên máy tính cá nhân."

if os.path.exists(file_mau):
    generate_voice_f5(file_mau, noi_dung, "ket_qua_tieng_viet.wav")
else:
    print(f"Vui lòng chuẩn bị file mẫu: {file_mau}")

# import torch
# from TTS.api import TTS
# import os

# # Khởi tạo Global để load model duy nhất 1 lần
# print("--- Đang nạp Model vào RAM/VRAM... ---")
# device = "cuda" if torch.cuda.is_available() else "cpu"
# # Dùng phiên bản XTTS v2
# tts_engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# def generate_voice(reference_wav, text, output_path="output.wav"):
#     """
#     Sử dụng tts_engine đã được nạp sẵn để tạo giọng nói.
#     """
#     try:
#         if not os.path.exists(reference_wav):
#             raise FileNotFoundError(f"Không tìm thấy file mẫu tại: {reference_wav}")

#         tts_engine.tts_to_file(
#             text=text,
#             speaker_wav=reference_wav,
#             language="vi",
#             file_path=output_path
#         )
#         return output_path
#     except Exception as e:
#         print(f"Lỗi: {e}")
#         return None