import sys
import os

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Mimic the import pattern used in the codebase
    from gemma4lib import genai, types
    print("Successfully imported genai and types from gemma4lib")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_client_init():
    print("\n--- Testing Client Initialization ---")
    client = genai.Client(api_key="mock-key")
    if hasattr(client, 'models') and hasattr(client, 'files'):
        print("Client initialized with models and files")
    else:
        print("Client initialization failed")

def test_types_structure():
    print("\n--- Testing Types Structure ---")
    try:
        part = types.Part.from_text(text="Hello")
        content = types.Content(role="user", parts=[part])
        config = types.GenerateContentConfig(temperature=0.7)
        tool = types.Tool(google_search=types.GoogleSearch())
        
        print(f"Part: {part}")
        print(f"Content: {content}")
        print(f"Config: {config}")
        print(f"Tool with Google Search: {tool}")
    except Exception as e:
        print(f"Types test failed: {e}")

def test_generate_content_mock():
    print("\n--- Testing Generate Content (Mock Response) ---")
    try:
        # Create a mock response
        resp = types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        role="model",
                        parts=[types.Part(text="Hello, I am Gemma!")]
                    ),
                    finish_reason="STOP"
                )
            ]
        )
        print(f"Response text property: {resp.text}")
        if resp.text == "Hello, I am Gemma!":
            print("Response text property works correctly")
        
        if resp.candidates[0].finish_reason == "STOP":
            print("Finish reason access works correctly")
    except Exception as e:
        print(f"Mock response test failed: {e}")

def test_generate_content_real():
    print("\n--- Testing Real Generate Content ---")
    client = genai.Client(api_key="mock-key")
    
    prompt = "Xin chào, bạn là ai?"
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    
    try:
        print(f"Calling generate_content with prompt: '{prompt}'")
        response = client.models.generate_content(
            model="gemma-4",
            contents=contents
        )
        print(f"Response received. text: {response.text}")
        if response.text and len(response.text) > 0:
            print("Real generation test passed!")
        else:
            print("Real generation test failed: empty response")
    except Exception as e:
        print(f"Real generation test failed with error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "config_dunp":
        test_client_init()
        test_types_structure()
        test_generate_content_mock()
        # test_generate_content_real() # Warning: This loads the real model weights
        test_generate_content_real()
    else:
        print("Missing required argument: config_dunp")
