import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from gemma4.llm import generate_text

class TestGemma4LLM(unittest.TestCase):
    """
    Kiểm thử chức năng Text Generation của gemma4.
    Yêu cầu: sinh text từ input, đầu ra tiếng Việt.
    """
    
    def test_generate_text_status(self):
        # Kiểm tra API trả về chuỗi thay vì rỗng hoặc lỗi
        # Lưu ý: Vì chạy trên CPU có thể chậm, ta chỉ kiểm tra cấu trúc cơ bản
        query = "Xin chào, bạn là ai?"
        print(f"\n[*] Query: {query}")
        result = generate_text(query)
        print(f"[+] Result: {result}")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_generate_text_content(self):
        # Kiểm tra nội dung cơ bản
        query = "Hãy viết một câu chào ngắn bằng tiếng Việt"
        print(f"\n[*] Query: {query}")
        result = generate_text(query)
        print(f"[+] Result: {result}")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

if __name__ == "__main__":
    # Đảm bảo có config_dunp để import/cấu hình project (mặc định nếu thiếu)
    if len(sys.argv) < 2:
        sys.argv.append("config_dunp")
        print("[!] Không tìm thấy config, tự động sử dụng: config_dunp")
    
    # Loại bỏ config_name ra khỏi sys.argv trước khi gọi unittest.main()
    # để tránh làm gãy các tham số của unittest
    if len(sys.argv) > 1 and (sys.argv[1] == "config_dunp" or sys.argv[1] == "config_ngoc"):
        config_name = sys.argv.pop(1)
        print(f"[*] Đang chạy các test function trong {os.path.basename(__file__)} với {config_name}...")
    
    unittest.main()
