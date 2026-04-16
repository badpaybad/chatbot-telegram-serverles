import os
import sys

# Simulation of a user script importing gemma4lib
print("--- GEMMA4LIB VERIFICATION ---")

try:
    import gemma4lib
    print("[+] Successfully imported gemma4lib")
    
    # Check if environment variables were set by gemma4lib
    hsa_version = os.environ.get("HSA_OVERRIDE_GFX_VERSION")
    print(f"[i] HSA_OVERRIDE_GFX_VERSION: {hsa_version}")
    
    if hsa_version == "11.0.0":
        print("[+] Environment variable set correctly before import")
    else:
        print("[-] Environment variable NOT set or incorrect")
        
    # Check if PATH includes gemma4 (for rocminfo shim)
    path = os.environ.get("PATH", "")
    if "gemma4" in path:
        print("[+] gemma4 directory added to PATH")
    else:
        print("[-] gemma4 directory NOT found in PATH")
        
    # Test Client instantiation (this will trigger model manager loading)
    print("[*] Instantiating Client (this might take a moment if it loads model)...")
    # We use a dummy api_key
    client = gemma4lib.genai.Client(api_key="test")
    print("[+] Client instantiated successfully")
    
    import torch
    print(f"[i] PyTorch version: {torch.__version__}")
    print(f"[i] CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
         print(f"[i] Device: {torch.cuda.get_device_name(0)}")

except Exception as e:
    print(f"[-] Verification FAILED: {e}")
    import traceback
    traceback.print_exc()
