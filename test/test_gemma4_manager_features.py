import sys
import os
import unittest
import torch

# Thiết lập project root để import được gemma4 và config
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Kiểm tra tham số bắt buộc theo architecture.md
if len(sys.argv) < 2 or sys.argv[1] != "config_dunp":
    print("Sử dụng: python test/test_gemma4_manager_features.py config_dunp")
    sys.exit(1)

# Import các thành phần cần test
from gemma4 import (
    Gemma4Manager, 
    generate_text, 
    transcribe_audio, 
    match_tools, 
    get_text_embedding
)

class TestGemma4Features(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n[*] Đang khởi tạo Gemma4Manager cho bộ test...")
        cls.manager = Gemma4Manager()
        cls.audio_file = os.path.join(project_root, "voice_assistant", "giong_cua_toi.wav")

    def test_text_generation(self):
        print("\n[*] Đang test Text Generation...")
        prompt = "Xin chào, bạn là ai?"
        response = generate_text(prompt)
        print(f"Q: {prompt}")
        print(f"A: {response}")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        # Kiểm tra xem có phải tiếng Việt không (đơn giản bằng cách tìm từ phổ biến)
        vietnamese_keywords = ["tôi", "là", "bạn", "chào", "AI", "Gemma"]
        found = any(word.lower() in response.lower() for word in vietnamese_keywords)
        self.assertTrue(found, "Response should be in Vietnamese")

    def test_embeddings(self):
        print("\n[*] Đang test Embeddings...")
        text = "Học máy là một lĩnh vực của trí tuệ nhân tạo."
        embedding = get_text_embedding(text)
        print(f"Text: {text}")
        print(f"Embedding size: {len(embedding)}")
        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 2560) # Theo config.json: hidden_size = 2560

    def test_tool_calling(self):
        print("\n[*] Đang test Tool Calling...")
        def check_weather(location: str):
            """Lấy thông tin thời tiết tại một địa điểm cụ thể."""
            pass

        tools_def = [
            {
                "name": "check_weather",
                "description": "Lấy thông tin thời tiết tại một địa điểm cụ thể.",
                "parameters": {"location": "string"}
            }
        ]
        query = "Thời tiết ở Hà Nội hôm nay thế nào?"
        results = match_tools(query, tools_def)
        print(f"Query: {query}")
        print(f"Results: {results}")
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].get("function_name"), "check_weather")
        self.assertGreater(results[0].get("score", 0), 0.5)

    def test_stt(self):
        print("\n[*] Đang test Speech-To-Text...")
        if os.path.exists(self.audio_file):
            text = transcribe_audio(self.audio_file)
            print(f"File: {self.audio_file}")
            print(f"Transcription: {text}")
            self.assertIsInstance(text, str)
            self.assertNotEqual(text, "")
        else:
            print(f"[!] Bỏ qua test STT vì không tìm thấy file: {self.audio_file}")

if __name__ == "__main__":
    # Remove config_dunp from sys.argv so unittest.main() doesn't get confused
    sys.argv.pop(1)
    unittest.main()
