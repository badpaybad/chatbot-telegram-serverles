import os
import sys
import requests
from huggingface_hub import snapshot_download

# Define model and local paths
MODEL_ID = "google/gemma-4-e4b-it"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: GEMMA_DIR is now dynamically determined in setup_gemma()
KOKORO_DIR = os.path.join(BASE_DIR, "model", "kokoro")

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        print(f"[*] {os.path.basename(dest_path)} already exists. Skipping.")
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
    print("\n[*] Checking/Setting up Kokoro ONNX assets...")
    os.makedirs(KOKORO_DIR, exist_ok=True)
    
    # Official ONNX model and voices (Stable GitHub Releases)
    model_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
    voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
    
    model_path = os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx")
    voices_path = os.path.join(KOKORO_DIR, "voices.bin")
    
    success = download_file(model_url, model_path)
    success = success and download_file(voices_url, voices_path)
    
    if success:
        print("[+] Kokoro ONNX assets are ready.")
    else:
        print("[-] Some Kokoro assets failed to download.")
    return success

def setup_gemma(repo_id=None):
    target_id = repo_id or MODEL_ID
    model_name = target_id.split("/")[-1]
    gemma_dir = os.path.join(BASE_DIR, "model", model_name)
    
    print(f"\n[*] Checking/Setting up Gemma 4 ('{target_id}')...")
    
    # Check if some key file exists to skip download (e.g. config.json)
    if os.path.exists(os.path.join(gemma_dir, "config.json")):
        print(f"[*] Gemma 4 already exists in '{gemma_dir}'. Skipping download.")
        return True

    os.makedirs(gemma_dir, exist_ok=True)
    
    try:
        # snapshot_download will check cache and download missing files
        path = snapshot_download(
            repo_id=target_id,
            local_dir=gemma_dir
        )
        print(f"[+] Gemma 4 downloaded successfully to: {path}")
        return True
    except Exception as e:
        print(f"[-] Error downloading Gemma 4: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Gemma 4 & Kokoro Setup System ===")
    
    # Setup Gemma 4
    gemma_ok = setup_gemma()
    
    # Setup Kokoro
    kokoro_ok = setup_kokoro()
    
    if not gemma_ok or not kokoro_ok:
        print("\n[!] Setup completed with one or more errors.")
        sys.exit(1)
    else:
        print("\n[+] Setup completed successfully! All models are ready.")
