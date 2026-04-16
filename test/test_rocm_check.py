import os
import sys

# MUST set environment variables BEFORE importing torch for ROCm
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

import torch

def check_rocm():
    print("--- ROCM CHECK ---")
    print(f"Python Version: {sys.version}")
    print(f"PyTorch Version: {torch.__version__}")
    
    cuda_available = torch.cuda.is_available()
    print(f"CUDA (ROCm) Available: {cuda_available}")
    
    if cuda_available:
        print(f"Device Count: {torch.cuda.device_count()}")
        print(f"Current Device Name: {torch.cuda.get_device_name(0)}")
        
        # Test tensor on GPU
        try:
            x = torch.tensor([1.0, 2.0]).to("cuda")
            print(f"Tensor on GPU: {x}")
            print("Successfully moved tensor to GPU!")
        except Exception as e:
            print(f"Error moving tensor to GPU: {e}")
    else:
        print("GPU not detected. Please check if PyTorch ROCm version is installed and HSA_OVERRIDE_GFX_VERSION is set.")

if __name__ == "__main__":
    check_rocm()
