from google import genai
import sys

GEMINI_APIKEY = "AIzaSyBBYpY4f1pyMA5udl304s5FAMwOAx5RPLA"
GEMINI_MODEL = "gemini-2.0-flash"

print("Initializing client...")
client = genai.Client(api_key=GEMINI_APIKEY)

print("Sending request...")
try:
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=["Say hello"]
    )
    print("Response received:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
