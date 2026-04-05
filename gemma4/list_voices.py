import json
import os
from kokoro_onnx import Kokoro

def list_voices():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "model", "kokoro", "kokoro-v1.0.onnx")
    voices_path = os.path.join(base_dir, "model", "kokoro", "voices.bin")
    
    if not os.path.exists(model_path) or not os.path.exists(voices_path):
        print("[-] Model or voices not found.")
        return
    
    kokoro = Kokoro(model_path, voices_path)
    voices = kokoro.get_voices()
    print(f"[*] Available voices ({len(voices)}):")
    for v in sorted(voices):
        print(f"  - {v}")

if __name__ == "__main__":
    list_voices()
