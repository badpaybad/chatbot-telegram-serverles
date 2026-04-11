import requests
import json
import base64
import sys
import time
import os

def test_generate_content():
    url = "http://127.0.0.1:8000/v1beta/models/gemma-4:generateContent"
    
    # 1. Test Text Only
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "Chào bạn, bạn là ai?"}]
            }
        ]
    }
    print("[*] Testing Text Only...")
    try:
        response = requests.post(url, json=payload)
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test Multimodal (Image) - Giả lập bằng 1 pixel ảnh trắng base64
    # R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7 is 1x1 white pixel gif
    # We use a small JPEG base64 for better compatibility
    # PNG 1x1 white pixel
    white_pixel_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1FMAAAAAElFTkSuQmCC"
    
    payload_multimodal = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": "image/png", "data": white_pixel_png.strip()}},
                    {"text": "Mô tả bức ảnh này."}
                ]
            }
        ]
    }
    print("\n[*] Testing Multimodal (Image)...")
    try:
        response = requests.post(url, json=payload_multimodal)
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. Test Tool Calling
    payload_tools = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "Thời tiết tại Hà Nội hôm nay thế nào?"}]
            }
        ],
        "tools": [
            {
                "function_declarations": [
                    {
                        "name": "get_weather",
                        "description": "Lấy thông tin thời tiết tại một địa điểm cụ thể.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string", "description": "Tên thành phố hoặc địa danh"}
                            },
                            "required": ["location"]
                        }
                    }
                ]
            }
        ]
    }
    print("\n[*] Testing Tool Calling...")
    try:
        response = requests.post(url, json=payload_tools)
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "config_dunp":
        print("Lỗi: Thiếu tham số config_dunp")
        sys.exit(1)
        
    test_generate_content()
