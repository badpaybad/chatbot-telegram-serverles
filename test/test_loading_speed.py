import os
import sys
import time

# Simulation of environment setup
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"
os.environ["HSA_ENABLE_SDMA"] = "1"
os.environ["MIOPEN_DEBUG_DISABLE_FIND_DB"] = "1"

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemma4.manager import get_manager

def test_speed():
    print("--- Loading Speed Test ---")
    start_time = time.time()
    
    print("[*] Initializing Manager (this triggers model load)...")
    try:
        manager = get_manager()
        end_time = time.time()
        print(f"[+] Total load time: {end_time - start_time:.2f} seconds")
        
        print("[*] Running a warm-up prompt...")
        gen_start = time.time()
        response = manager.generate("Xin chào, bạn có khỏe không?")
        gen_end = time.time()
        print(f"[+] Response: {response}")
        print(f"[+] Generation time: {gen_end - gen_start:.2f} seconds")
        
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    test_speed()
