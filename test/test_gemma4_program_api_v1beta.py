import requests
import json
import base64
import sys
import os
import time

# --- Mẫu ảnh 1x1 pixel trắng ---
WHITE_PIXEL_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1FMAAAAAElFTkSuQmCC"

def test_api():
    base_url = "http://localhost:8000/v1beta"
    
    print("\n--- 1. Testing Files API (Upload) ---")
    files_url = f"{base_url}/files"
    # Tạo dummy file
    with open("test/dummy_test.txt", "w") as f:
        f.write("Đây là nội dung của file test upload lên Gemini API.")
    
    with open("test/dummy_test.txt", "rb") as f:
        files = {"file": ("dummy_test.txt", f, "text/plain")}
        resp = requests.post(files_url, files=files)
        file_metadata = resp.json()
        print(f"File Metadata: {json.dumps(file_metadata, indent=2)}")
        file_uri = file_metadata["uri"]
        file_id = file_uri.split("/")[-1]

    print("\n--- 2. Testing generateContent with file_data ---")
    gen_url = f"{base_url}/models/gemma-4:generateContent"
    payload = {
        "contents": [{
            "parts": [
                {"text": "Tóm tắt file này cho tôi"},
                {"file_data": {"file_uri": file_uri}}
            ]
        }]
    }
    resp = requests.post(gen_url, json=payload)
    print(f"Response: {json.dumps(resp.json(), indent=2)}")

    print("\n--- 3. Testing generateContent with system_instruction ---")
    payload_sys = {
        "system_instruction": {
            "parts": [{"text": "Bạn là một trợ lý ảo của công ty Dunp Corp. Hãy luôn bắt đầu câu trả lời bằng 'Chào mừng đến với Dunp!'"}]
        },
        "contents": [{
            "parts": [{"text": "Bạn là ai?"}]
        }]
    }
    resp = requests.post(gen_url, json=payload_sys)
    print(f"Response: {json.dumps(resp.json(), indent=2)}")

    print("\n--- 4. Testing streamGenerateContent ---")
    stream_url = f"{base_url}/models/gemma-4:streamGenerateContent"
    payload_stream = {
        "contents": [{"parts": [{"text": "Hãy viết một đoạn văn ngắn về vẻ đẹp của Hà Nội."}]}]
    }
    resp = requests.post(stream_url, json=payload_stream, stream=True)
    print("Stream output:")
    for line in resp.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            text = chunk["candidates"][0]["content"]["parts"][0].get("text", "")
            print(text, end="", flush=True)
    print("\n[Stream finished]")

    print("\n--- 5. Testing Files API (Delete) ---")
    resp = requests.delete(f"{files_url}/{file_id}")
    print(f"Delete Response: {resp.json()}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "config_dunp":
        print("Lỗi: Thiếu tham số config_dunp")
        sys.exit(1)
        
    try:
        test_api()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
