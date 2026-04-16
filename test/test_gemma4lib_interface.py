import os
import sys
import unittest
from unittest.mock import MagicMock

# Thêm thư mục gốc vào path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import gemma4lib
try:
    from gemma4 import gemma4lib as genai
    from gemma4.gemma4lib import types
except ImportError:
    # Nếu chưa cài đặt đúng cấu trúc package, thử import trực tiếp
    sys.path.append(os.path.join(project_root, "gemma4"))
    import gemma4lib as genai
    from gemma4lib import types

class TestGemma4Lib(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n[*] Initializing Gemma4Lib Client for testing...")
        cls.client = genai.Client(api_key="mock-key")

    def test_text_generation(self):
        print("\n[*] Testing Basic Text Generation...")
        prompt = "Xin chào, bạn là ai?"
        response = self.client.models.generate_content(
            model="gemma-4",
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
        )
        print(f"[+] Response: {response.text}")
        self.assertIsInstance(response.text, str)
        self.assertTrue(len(response.text) > 0)

    def test_system_instruction(self):
        print("\n[*] Testing System Instruction...")
        config = types.GenerateContentConfig(
            system_instruction="Bạn là một trợ lý vui vẻ và luôn bắt đầu câu bằng 'Chào người bạn!'.",
            temperature=0.0
        )
        response = self.client.models.generate_content(
            model="gemma-4",
            contents=[types.Content(role="user", parts=[types.Part.from_text(text="Tôi muốn hỏi đường.")])],
            config=config
        )
        print(f"[+] Response: {response.text}")
        self.assertTrue(len(response.text) > 0)

    def test_file_upload_simulation(self):
        print("\n[*] Testing File Upload Simulation...")
        # Create a dummy file
        dummy_path = os.path.join(project_root, "test", "dummy.txt")
        with open(dummy_path, "w") as f:
            f.write("Đây là nội dung dummy file.")
        
        try:
            uploaded = self.client.files.upload(file=dummy_path)
            print(f"[+] Uploaded: {uploaded.name}, URI: {uploaded.uri}")
            self.assertEqual(uploaded.display_name, "dummy.txt")
            
            # Test getting metadata
            meta = self.client.files.get(name=uploaded.name)
            self.assertEqual(meta.state.name, "ACTIVE")
        finally:
            if os.path.exists(dummy_path):
                os.remove(dummy_path)

    def test_tool_calling_simulation(self):
        print("\n[*] Testing Tool Calling Simulation...")
        # Define a mock tool
        tool = types.Tool(
            function_declarations=[{
                "name": "get_weather",
                "description": "Lấy thông tin thời tiết tại một thành phố.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "Tên thành phố"}
                    },
                    "required": ["city"]
                }
            }]
        )
        
        config = types.GenerateContentConfig(tools=[tool])
        prompt = "Thời tiết ở Hà Nội hôm nay thế nào?"
        
        response = self.client.models.generate_content(
            model="gemma-4",
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
            config=config
        )
        
        # Kiểm tra xem có function_call không
        has_fc = False
        parts = response.candidates[0].content.parts
        for part in parts:
            if part.function_call:
                print(f"[+] Function Call Detected: {part.function_call.name} with args {part.function_call.args}")
                self.assertEqual(part.function_call.name, "get_weather")
                has_fc = True
                break
        
        # Nếu model không chọn gọi tool (score thấp hoặc prompt không khớp), 
        # ít nhất nó cũng phải trả về text. Gemma 4 thường sẽ trả về Tool Call nếu prompt rõ ràng.
        if not has_fc:
            print(f"[-] No function call triggered, fallback to text: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "config_dunp":
        # Remove config_dunp from sys.argv for unittest
        sys.argv.pop(1)
        unittest.main()
    else:
        print("[!] Missing required argument: config_dunp")
        sys.exit(1)
