import os
import sys
from huggingface_hub import snapshot_download

# Define model and local path
MODEL_ID = "google/gemma-4-e4b-it"
LOCAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")

def download_model():
    print(f"[*] Starting download/sync of '{MODEL_ID}' to '{LOCAL_DIR}'...")
    
    # Ensure local directory exists
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR, exist_ok=True)
    
    try:
        # snapshot_download will check cache and download missing files
        # local_dir_use_symlinks=False to have actual files in the folder if desired, 
        # but "auto" is usually fine to save space.
        # Here we use local_dir to ensure it's in the subfolder.
        path = snapshot_download(
            repo_id=MODEL_ID,
            local_dir=LOCAL_DIR,
            local_dir_use_symlinks=False, # Copy files to local_dir instead of symlinking to cache
            trust_remote_code=True
        )
        print(f"[+] Model downloaded successfully to: {path}")
    except Exception as e:
        print(f"[-] Error downloading model: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    download_model()
