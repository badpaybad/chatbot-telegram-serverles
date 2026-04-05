import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import json
from gemma4.tools import Gemma4Tools

class TestGemma4ToolsRegistration(unittest.TestCase):
    """
    Kiểm thử việc đăng ký tool động và trích xuất từ docstring trong Gemma4Tools.
    """
    
    def setUp(self):
        self.gtool = Gemma4Tools()

    def test_add_tool_manual(self):
        # Đăng ký thủ công
        tool_def = {
            "name": "test_tool",
            "description": "Mô tả tool test",
            "parameters": {"param1": "string"}
        }
        print(f"\n[*] Đăng ký tool thủ công: {tool_def['name']}")
        self.gtool.add_tool(tool_def)
        print(f"[+] Tool list sau khi đăng ký: {len(self.gtool.tools)} cá thể.")
        self.assertIn(tool_def, self.gtool.tools)

    def test_add_tool_from_func(self):
        # Hàm mẫu có docstring và type hints
        def calculate_bmi(weight: float, height: float):
            """
            Tính chỉ số khối cơ thể (BMI) từ cân nặng và chiều cao.
            """
            return weight / (height ** 2)

        print(f"\n[*] Đăng ký tool từ hàm: {calculate_bmi.__name__}")
        self.gtool.add_tool_from_func(calculate_bmi)
        
        # Tìm tool vừa đăng ký
        tool = next((t for t in self.gtool.tools if t["name"] == "calculate_bmi"), None)
        print(f"[+] Tool trích xuất metadata: {json.dumps(tool, indent=2, ensure_ascii=False)}")
        self.assertIsNotNone(tool)
        self.assertEqual(tool["name"], "calculate_bmi")
        self.assertIn("Tính chỉ số khối cơ thể", tool["description"])
        self.assertEqual(tool["parameters"]["weight"], "float")
        self.assertEqual(tool["parameters"]["height"], "float")

    def test_match_tools_with_registered(self):
        # Đăng ký hàm và test matching
        def gui_tin_nhan(sdt: str, noi_dung: str):
            """
            Gửi tin nhắn SMS đến số điện thoại người nhận.
            """
            pass

        self.gtool.add_tool_from_func(gui_tin_nhan)
        
        query = "Gửi tin nhắn cho 0912345678 nội dung là Chúc mừng sinh nhật."
        print(f"\n[*] Query: {query}")
        # Chạy match_tools (sẽ sử dụng list self.tools nội bộ)
        results = self.gtool.match_tools(query)
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
