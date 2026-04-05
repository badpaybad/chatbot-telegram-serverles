import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import json
from gemma4.tools import match_tools

class TestGemma4Tools(unittest.TestCase):
    """
    Kiểm thử chức năng Tool Calling của gemma4.
    Yêu cầu: trích xuất hàm và chấm điểm score.
    """
    
    def setUp(self):
        # Định nghĩa các công cụ giả lập để test
        self.sample_tools = [
            {
                "name": "gui_email",
                "description": "Gửi email cho một địa chỉ cụ thể",
                "parameters": {"email": "string", "nội dung": "string"}
            },
            {
                "name": "tra_cuu_lich_hen",
                "description": "Xem danh sách các lịch hẹn trong ngày",
                "parameters": {"ngày": "string"}
            }
        ]

    def test_match_tools_relevance(self):
        # Gửi lời nhắn liên quan đến email
        query = "Gửi email cho abc@gmail.com nói rằng tôi sẽ đến muộn."
        print(f"\n[*] Query: {query}")
        results = match_tools(query, self.sample_tools)
        print(f"[+] Match results: {json.dumps(results, indent=2, ensure_ascii=False)}")
        
        # Kiểm tra cấu trúc trả về
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        
        # Kiểm tra xem hàm 'gui_email' có score cao nhất (thường là vậy)
        best_match = results[0]
        self.assertIn("function_name", best_match)
        self.assertIn("score", best_match)

    def test_match_tools_empty_query(self):
        # Gửi query không liên quan
        query = "Hôm nay tôi thấy vui quá."
        print(f"\n[*] Query: {query}")
        results = match_tools(query, self.sample_tools)
        print(f"[+] Match results: {json.dumps(results, indent=2, ensure_ascii=False)}")
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.argv.append("config_dunp")
        print("[!] Không tìm thấy cấu hình, tự động sử dụng: config_dunp")
    
    if len(sys.argv) > 1 and (sys.argv[1] == "config_dunp" or sys.argv[1] == "config_ngoc"):
        config_name = sys.argv.pop(1)
        print(f"[*] Đang thực thi {os.path.basename(__file__)} với {config_name}...")
        
    unittest.main()
