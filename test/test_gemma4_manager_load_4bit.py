import os
import sys
import torch

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from gemma4.manager import get_manager

def test_load_4bit():
    print("=== Testing Gemma 4-bit (Q4_K_M) Loading ===")
    try:
        # We use a mocked model ID or the local one if exists, but we want to check if the config is applied
        # For a unit-like test, we just check if the manager can be initialized
        manager = get_manager()
        
        print(f"[+] Manager Device: {manager.device}")
        
        if hasattr(manager, 'model'):
            print("[+] Model loaded successfully.")
            # Check quantization config in the model
            if hasattr(manager.model, 'config') and hasattr(manager.model.config, 'quantization_config'):
                q_config = manager.model.config.quantization_config
                print(f"[+] Quantization Config: {q_config}")
                if q_config.load_in_4bit:
                    print("[SUCCESS] Model is running in 4-bit mode.")
                else:
                    print("[FAILURE] Model is NOT running in 4-bit mode.")
            else:
                # Some models might store it differently
                print("[!] Quantization config not found in model.config. Checking bitsandbytes status...")
        
        # Test a simple generation if possible (might take time on CPU)
        # result = manager.generate("Xin chào, bạn khỏe không?")
        # print(f"Response: {result}")
        
    except Exception as e:
        print(f"[-] Error during 4-bit load test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "config_dunp":
        test_load_4bit()
    else:
        print("Usage: python test/test_gemma4_manager_load_4bit.py config_dunp")
