import os
import requests
import sys

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        print(f"[*] {dest_path} already exists. Skipping.")
        return True
    
    print(f"[*] Downloading {url} to {dest_path}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[+] Download complete: {dest_path}")
        return True
    except Exception as e:
        print(f"[-] Error downloading {url}: {e}")
        return False

def setup_kokoro():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "model", "kokoro")
    os.makedirs(model_dir, exist_ok=True)
    
    # Official ONNX model and voices (Stable GitHub Releases)
    model_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
    voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
    
    model_path = os.path.join(model_dir, "kokoro-v1.0.onnx")
    voices_path = os.path.join(model_dir, "voices.bin")
    
    success = download_file(model_url, model_path)
    success = success and download_file(voices_url, voices_path)
    
    if success:
        print("[+] Kokoro ONNX assets are ready.")
    else:
        print("[-] Some assets failed to download.")
        sys.exit(1)

if __name__ == "__main__":
    setup_kokoro()
