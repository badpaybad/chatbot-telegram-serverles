import os
import sys

# ROCm Optimization for Radeon 780M (gfx1102)
# Using 11.0.0 as it is the most compatible target for GFX11 kernels
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"
os.environ["HSA_ENABLE_SDMA"] = "1" # Speeds up CPU-GPU transfers
os.environ["MIOPEN_DEBUG_DISABLE_FIND_DB"] = "1" # Prevents slow MIOpen tuning lag
os.environ["ROCM_RELAXED_ASIC_CHECK"] = "1" # Compatibility for mobile APUs
os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "0" # Disabled to reduce peak VRAM during startup
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:128"

# Add current directory to PATH so bitsandbytes can find our 'rocminfo' shim
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = current_dir + os.pathsep + os.environ.get("PATH", "")

# Point to bundled ROCm libraries in torch if they exist
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
torch_lib_path = os.path.join(project_root, "venv/lib/python3.12/site-packages/torch/lib")
if os.path.exists(torch_lib_path):
    os.environ["LD_LIBRARY_PATH"] = torch_lib_path + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["ROCM_PATH"] = torch_lib_path # bitsandbytes ROCm might look here

import torch
import threading
import numpy as np
from typing import List, Dict, Optional, Any, Union
from PIL import Image
from transformers import AutoProcessor, AutoModelForMultimodalLM, AutoConfig, BitsAndBytesConfig

# Import config based on project structure
if project_root not in sys.path:
    sys.path.append(project_root)
from config import *
from .download_model import setup_gemma, setup_kokoro

class Gemma4Manager:
    """
    Singleton Manager for loading the multimodal Gemma 4 model and processor once.
    Optimized for 16GB RAM constraints using low_cpu_mem_usage.
    Thread-safe implementation using Double-checked locking.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, model_id: str = "google/gemma-4-e4b-it"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # Resolve priority path: 1. Local project, 2. HF cache, 3. Automated Setup
                    model_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
                    
                    # Tự động xác định thư mục local dựa trên tên model
                    model_name = model_id.split("/")[-1]
                    local_model_dir = os.path.join(model_root, model_name)
                    
                    # 1. Prioritize Local Project Folder
                    if os.path.isdir(local_model_dir) and os.path.exists(os.path.join(local_model_dir, "config.json")):
                         print(f"[*] Using local project model: {local_model_dir}")
                         model_id = local_model_dir
                    
                    # 3. Trigger setup if absolutely nothing found
                    if not os.path.exists(os.path.join(local_model_dir, "config.json")) and (not os.path.isabs(model_id) or not os.path.exists(model_id)):
                        print(f"[*] Model {model_id} not found locally. Triggering automated setup...")
                        from .download_model import setup_gemma
                        setup_gemma(model_id)
                        if os.path.exists(os.path.join(local_model_dir, "config.json")):
                             model_id = local_model_dir
                    
                    # Also ensure Kokoro is ready if needed, though tts.py might use it
                    kokoro_model_path = os.path.join(model_root, "kokoro", "kokoro-v1.0.onnx")
                    if not os.path.exists(kokoro_model_path):
                        print("[*] Kokoro ONNX assets not found. Triggering automated setup...")
                        setup_kokoro()
                    
                    print(f"[*] Initializing Gemma4Manager for {model_id}...")
                    
                    # Create the actual instance
                    new_instance = super(Gemma4Manager, cls).__new__(cls)
                    # Load model BEFORE assigning to _instance to prevent race condition
                    new_instance._load_model(model_id)
                    cls._instance = new_instance
        return cls._instance

    def _load_model(self, model_id: str):
        self.model_id = model_id
        # Automatically detect device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"[*] Loading Multimodal Model: {model_id} on {self.device}...")
        
        # Determine optimal dtype
        # float16 is often more stable and faster for inference on RDNA3 iGPUs
        if self.device == "cuda":
            self.dtype = torch.float16
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
            print(f"[*] Instantiating model with 4-bit (NF4) quantization...")
            
            # Configure 4-bit quantization (NF4)
            # Optimized for ROCm and RDNA3 (780M)
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16, # RDNA3 (780M) is optimized for FP16
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True
                # Removed llm_int8_enable_fp32_cpu_offload which is less efficient for 4-bit
            )

            import time
            start_load = time.time()
            print(f"[*] Starting weights loading (this may take a few minutes for 15GB)...")

            self.model = AutoModelForMultimodalLM.from_pretrained(
                self.model_id,
                config=config,
                torch_dtype=torch.float16, # Explicitly use float16 for ROCm speed
                device_map="auto" if self.device == "cuda" else None, 
                quantization_config=quantization_config if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                attn_implementation="sdpa" # Modern attention implementation
            ).eval() 
            
            load_duration = time.time() - start_load
            print(f"[+] Weights loaded and quantized in {load_duration:.2f} seconds.")

            # Force garbage collection and empty CUDA cache
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            print(f"[+] Multimodal model {model_id} initialization complete.")

        except Exception as e:
            print(f"[-] ERROR loading gemma4 model: {str(e)}")
            # Raise so the app knows it failed to initialize AI
            raise e

    def generate(self, input_data: any, audio_array=None, image_path=None, images_list: List[Image.Image] = None, audio_list: List[np.ndarray] = None, max_tokens: int = 512, sampling_rate: int = 16000) -> str:
        """
        Processes chat history (list of messages) or single text prompt with optional audio/image.
        input_data: str (prompt) or list (messages history)
        images_list: List of PIL Image objects
        audio_list: List of numpy arrays
        """
        if not hasattr(self, 'model') or self.model is None:
             return "Lỗi: Hệ thống AI chưa sẵn sàng."

        messages = []
        if isinstance(input_data, list):
            messages = input_data
        else:
            user_input = str(input_data)
            msg_content = []
            
            # backward compatibility for single file/array
            if (image_path is not None and os.path.exists(image_path)) or (images_list and len(images_list) > 0):
                msg_content.append({"type": "image"})
            
            if audio_array is not None or (audio_list and len(audio_list) > 0):
                msg_content.append({"type": "audio"})
            
            msg_content.append({"type": "text", "text": f"{user_input}\n\nNote: Always answer in Vietnamese, naturally and concisely."})
            messages = [{"role": "user", "content": msg_content}]

        # Apply chat template
        text_prompt = self.processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        
        # Prepare multimodal inputs
        final_images = []
        if images_list:
            final_images.extend(images_list)
        
        if image_path is not None and os.path.exists(image_path):
            try:
                final_images.append(Image.open(image_path).convert("RGB"))
            except Exception as e:
                print(f"[-] Warning: Failed to load image {image_path}: {e}")
        
        final_audio = None
        if audio_list and len(audio_list) > 0:
            final_audio = audio_list[0] # Gemma 4 current processor usually takes one audio array
        elif audio_array is not None:
            final_audio = audio_array

        inputs = self.processor(
            text=text_prompt, 
            images=final_images if final_images else None, 
            audio=final_audio, 
            sampling_rate=sampling_rate, 
            return_tensors="pt"
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            
        # Decode and strip prompt
        input_len = inputs['input_ids'].shape[1]
        response = self.processor.decode(outputs[0][input_len:], skip_special_tokens=True)
        return response.strip()

    def generate_with_image(self, image_path: str, prompt: str, max_tokens: int = 512) -> str:
        """Helper specifically for Image + Text interaction."""
        return self.generate(user_input=prompt, image_path=image_path, max_tokens=max_tokens)

    def get_embeddings(self, text: str) -> list:
        """
        Tạo vector embedding từ văn bản đầu vào sử dụng Gemma 4 (Text Tower).
        Sử dụng mean pooling từ last_hidden_state.
        """
        if not hasattr(self, 'model') or self.model is None:
            raise RuntimeError("Lỗi: Hệ thống AI chưa sẵn sàng.")

        # Chuẩn bị input cho text
        inputs = self.processor(text=text, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            # Yêu cầu trả về hidden states
            outputs = self.model(**inputs, output_hidden_states=True)
            
            # Lấy last_hidden_state từ language_model hoặc từ output chính
            # Đối với Gemma4ForConditionalGeneration, last_hidden_state thường ở outputs.hidden_states[-1]
            # của phần language_model nếu nó là wrapper, hoặc trực tiếp nếu là decoder-only.
            
            if hasattr(outputs, 'hidden_states') and outputs.hidden_states is not None:
                last_hidden_state = outputs.hidden_states[-1]
            else:
                # Fallback nếu model trả về trực tiếp (tùy thuộc vào implementation của Gemma4)
                last_hidden_state = outputs[0]

            # Mean pooling qua chiều sequence (dim=1)
            # last_hidden_state shape: [batch, seq_len, hidden_size]
            attention_mask = inputs.get('attention_mask')
            if attention_mask is not None:
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
                sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, 1)
                sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                embeddings = sum_embeddings / sum_mask
            else:
                embeddings = torch.mean(last_hidden_state, dim=1)
            
            return embeddings[0].cpu().tolist()

    def get_image_embeddings(self, image_path: str) -> list:
        """
        Tạo vector embedding từ hình ảnh sử dụng Gemma 4 (Vision Tower).
        Sử dụng mean pooling từ các token hình ảnh sau khi qua Vision Tower.
        """
        if not hasattr(self, 'model') or self.model is None:
            raise RuntimeError("Lỗi: Hệ thống AI chưa sẵn sàng.")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Lỗi: File ảnh {image_path} không tồn tại.")

        try:
            # Load và chuẩn bị ảnh
            image = Image.open(image_path).convert("RGB")
            
            # Sử dụng processor để xử lý ảnh
            # Đối với Gemma 4, cung cấp text="" để tránh lỗi NoneType trong processor.
            inputs = self.processor(text="", images=image, return_tensors="pt").to(self.model.device)
            
            with torch.no_grad():
                # Đường dẫn chính xác cho kiến trúc Gemma4: self.model.model.vision_tower
                if hasattr(self.model, "model") and hasattr(self.model.model, "vision_tower"):
                    # Gemma 4 processor trả về "image_position_ids" thay vì "pixel_position_ids"
                    pixel_values = inputs.get("pixel_values")
                    pixel_position_ids = inputs.get("image_position_ids")
                    if pixel_position_ids is None:
                        pixel_position_ids = inputs.get("pixel_position_ids")
                    
                    if pixel_values is None or pixel_position_ids is None:
                        raise RuntimeError("Thiếu pixel_values hoặc position_ids trong processor output.")

                    vision_outputs = self.model.model.vision_tower(
                        pixel_values=pixel_values, 
                        pixel_position_ids=pixel_position_ids
                    )
                    # vision_outputs là BaseModelOutput, lấy last_hidden_state [1, tokens, 768]
                    image_features = vision_outputs.last_hidden_state
                    
                    # Nếu có lớp chiếu (multimodal projector) để sang không gian 2560
                    if hasattr(self.model.model, "embed_vision"):
                        image_features = self.model.model.embed_vision(image_features)
                elif hasattr(self.model, "get_image_features"):
                    image_features = self.model.get_image_features(**inputs)
                else:
                    # Fallback cuối cùng
                    outputs = self.model(**inputs, output_hidden_states=True)
                    if hasattr(outputs, "hidden_states") and outputs.hidden_states:
                        image_features = outputs.hidden_states[0]
                    else:
                        raise RuntimeError("Không thể trích xuất đặc trưng hình ảnh từ mô hình này.")

                # Mean pooling qua các token hình ảnh
                # image_features có thể là [batch, tokens, hidden] hoặc [tokens, hidden]
                if image_features.dim() == 3:
                    embeddings = torch.mean(image_features, dim=1)[0]
                elif image_features.dim() == 2:
                    embeddings = torch.mean(image_features, dim=0)
                else:
                    embeddings = image_features.flatten()

                return embeddings.cpu().tolist()
        except Exception as e:
            raise RuntimeError(f"Lỗi khi trích xuất embedding ảnh: {str(e)}")

def get_manager(model_id: str = "google/gemma-4-e4b-it"):
    """Helper function for singleton access."""
    return Gemma4Manager(model_id)
