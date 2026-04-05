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
        result = transcribe_audio("non_existent_file.wav")
        self.assertIn("Lỗi", result)
        self.assertIn("không tồn tại", result)

    def test_transcribe_audio_empty_path(self):
        # Kiểm tra trường hợp path trống
        result = transcribe_audio("")
        self.assertIn("Lỗi", result)

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
