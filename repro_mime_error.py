from google import genai
from google.genai import types
import os
import json

# Replace with your API key from config_dunp.py
GEMINI_APIKEY = "AIzaSyBBYpY4f1pyMA5udl304s5FAMwOAx5RPLA"
GEMINI_MODEL = "gemini-2.0-flash"

client = genai.Client(api_key=GEMINI_APIKEY)

# Create a dummy JSON file
json_file = "test_data.json"
with open(json_file, "w") as f:
    json.dump({"test": "data"}, f)

print(f"--- Uploading {json_file}... ---")
try:
    uploaded_file = client.files.upload(file=json_file)
    print(f"Uploaded file: {uploaded_file.uri}, MIME: {uploaded_file.mime_type}")

    print("--- Calling generate_content with JSON file from URI... ---")
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="What is in this file?"),
                    types.Part.from_uri(
                        file_uri=uploaded_file.uri,
                        mime_type=uploaded_file.mime_type
                    )
                ]
            )
        ]
    )
    print("Response successful!")
    print(response.text)
except Exception as e:
    print(f"Caught expected error: {e}")
finally:
    if os.path.exists(json_file):
        os.remove(json_file)
