import requests
import json
import base64
import sys
import time
import os

def test_omni_api():
    url = "http://127.0.0.1:8000/v1beta/models/gemma-4:generateContent"
    
    # --- 1. Test RAG (Text + TXT File) ---
    print("\n[*] Testing RAG (Text + TXT)...")
    txt_content = "Công ty TNHH AI Assistant được thành lập năm 2024, trụ sở tại Hà Nội. CEO là ông Nguyễn Văn A."
    txt_base64 = base64.b64encode(txt_content.encode('utf-8')).decode('utf-8')
    
    payload_rag = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": "text/plain", "data": txt_base64}},
                    {"text": "Công ty AI Assistant được thành lập năm nào và ai là CEO?"}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload_rag)
        print(f"Response: {response.json()['candidates'][0]['content']['parts'][0]['text']}")
    except Exception as e:
        print(f"Error RAG: {e}")

    # --- 2. Test File Generation Tool ---
    print("\n[*] Testing File Generation Tool...")
    payload_gen = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "Tạo một file txt tên là 'hello.txt' với nội dung 'Chào mừng bạn đến với thế giới AI'."}]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload_gen)
        text_resp = response.json()['candidates'][0]['content']['parts'][0]['text']
        print(f"Response: {text_resp}")
        
        # Kiểm tra nếu link download có trong response
        if "http" in text_resp:
            download_url = text_resp.split(":")[-1].strip()
            if not download_url.startswith("http"):
                 download_url = "http:" + download_url
            print(f"[*] Verifying download from: {download_url}")
            dl_resp = requests.get(download_url)
            print(f"Downloaded content: {dl_resp.text}")
    except Exception as e:
        print(f"Error Gen: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "config_dunp":
        print("Lỗi: Thiếu tham số config_dunp")
        sys.exit(1)
        
    test_omni_api()
