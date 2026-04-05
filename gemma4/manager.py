import os
import torch
import sys
from transformers import AutoProcessor, AutoModelForMultimodalLM, AutoConfig

# Import config based on project structure
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *

class Gemma4Manager:
    """
    Singleton Manager for loading the multimodal Gemma 4 model and processor once.
    Optimized for 16GB RAM constraints using low_cpu_mem_usage.
    """
    _instance = None

    def __new__(cls, model_id: str = "google/gemma-4-e4b-it"):
        if cls._instance is None:
            # Check for local storage presence in gemma4 subfolder 
            local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
            if os.path.isdir(local_path) and os.listdir(local_path):
                 print(f"[*] Local Gemma 4 model found: {local_path}")
                 model_id = local_path
            
            print(f"[*] Initializing Gemma4Manager for {model_id}...")
            cls._instance = super(Gemma4Manager, cls).__new__(cls)
            cls._instance._load_model(model_id)
        return cls._instance

    def _load_model(self, model_id: str):
        self.model_id = model_id
        # Automatically detect device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"[*] Loading Multimodal Model: {model_id} on {self.device}...")
        
        # Determine optimal dtype
        # bfloat16 to optimize memory usage (half precision)
        if self.device == "cuda":
            self.dtype = torch.bfloat16
        else:
            # CPU usually prefers float32, but bfloat16/float16 can save half memory
            # We'll use "auto" to let transformers choose based on safetensors
            self.dtype = "auto"

        try:
            # Load config with custom architecture support (gemma4)
            print(f"[*] Fetching configuration...")
            config = AutoConfig.from_pretrained(self.model_id, trust_remote_code=True)
            
            # Use AutoProcessor for multimodal inputs (Text + Audio)
            print(f"[*] Loading Processor...")
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            
            # Load model with memory-efficient settings
            # low_cpu_mem_usage=True: Only load weights when needed, reduces peak RAM
            print(f"[*] Instantiating model with low_cpu_mem_usage=True...")
            self.model = AutoModelForMultimodalLM.from_pretrained(
                self.model_id,
                config=config,
                device_map=self.device,
                torch_dtype=self.dtype,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            ).eval() 
            
            print(f"[+] Multimodal model {model_id} loaded successfully.")
        except Exception as e:
            print(f"[-] ERROR loading gemma4 model: {str(e)}")
            # Raise so the app knows it failed to initialize AI
            raise e

    def generate(self, user_input: str, audio_array=None, max_tokens: int = 512, sampling_rate: int = 16000) -> str:
        """
        Processes text and optional audio input to generate a response in Vietnamese.
        """
        if not hasattr(self, 'model') or self.model is None:
             return "Lỗi: Hệ thống AI chưa sẵn sàng."

        # Build multimodal prompt
        messages = [{"role": "user", "content": []}]
        
        if audio_array is not None:
            messages[0]["content"].append({"type": "audio"})
        
        # Enforce Vietnamese constraints
        messages[0]["content"].append({"type": "text", "text": f"{user_input}\n\nNote: Always answer in Vietnamese, naturally and concisely."})

        # Apply chat template (tokenize=False to ensure text input)
        text_prompt = self.processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        
        if audio_array is not None:
            inputs = self.processor(text=text_prompt, audio=audio_array, sampling_rate=sampling_rate, return_tensors="pt").to(self.device)
        else:
            inputs = self.processor(text=text_prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            
        # Decode and strip prompt
        response = self.processor.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        return response.strip()

def get_manager(model_id: str = "google/gemma-4-e4b-it"):
    """Helper function for singleton access."""
    return Gemma4Manager(model_id)
