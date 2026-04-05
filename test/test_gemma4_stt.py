import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from gemma4.stt import transcribe_audio

class TestGemma4STT(unittest.TestCase):
    """
    Kiểm thử chức năng Speech-to-Text của gemma4.
    Yêu cầu: đưa 1 file audio lấy ra text.
    """
    
    def test_transcribe_audio_not_found(self):
        # Kiểm tra trường hợp file không tồn tại
        audio_path = "non_existent_file.wav"
        print(f"\n[*] Audio Path: {audio_path}")
        result = transcribe_audio(audio_path)
        print(f"[+] Result: {result}")
        self.assertIn("Lỗi", result)
        self.assertIn("không tồn tại", result)

    def test_transcribe_audio_empty_path(self):
        # Kiểm tra trường hợp path trống
        audio_path = ""
        print(f"\n[*] Audio Path: {audio_path}")
        result = transcribe_audio(audio_path)
        print(f"[+] Result: {result}")
        self.assertIn("Lỗi", result)

    def test_transcribe_audio_path_wav(self):
        # Kiểm tra trường hợp nạp file audio thật
        audio_path = "test/Quang-cao-thuoc.wav"
        print(f"\n[*] Audio Path: {audio_path}")
        result = transcribe_audio(audio_path)
        print(f"[+] Result: {result}")
        self.assertIn("công việc", result.lower())

    def test_transcribe_audio_path_mp3(self):
        # Kiểm tra trường hợp nạp file audio thật
        audio_path = "test/Quang-cao-thuoc.mp3"
        print(f"\n[*] Audio Path: {audio_path}")
        result = transcribe_audio(audio_path)
        print(f"[+] Result: {result}")
        self.assertIn("công việc", result.lower())


if __name__ == "__main__":
    # Tự động gán config_dunp nếu thiếu
    if len(sys.argv) < 2:
        sys.argv.append("config_dunp")
        print("[!] Tự động sử dụng: config_dunp")
    
    # Loại bỏ config_name để không làm gãy unittest.main()
    if len(sys.argv) > 1 and (sys.argv[1] == "config_dunp" or sys.argv[1] == "config_ngoc"):
        config_name = sys.argv.pop(1)
        print(f"[*] Đang thực thi {os.path.basename(__file__)} với {config_name}...")
        
    unittest.main()
