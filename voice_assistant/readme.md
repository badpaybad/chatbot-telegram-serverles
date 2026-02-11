# Cài đặt python 3.10 cho hệ thống (nếu chưa có)
sudo apt update
sudo apt install python3.10 python3.10-venv

# Tạo môi trường ảo với đúng phiên bản 3.10
python3.10 -m venv voice_env

# Kích hoạt môi trường
source voice_env/bin/activate

# Bây giờ mới tiến hành cài đặt (trong môi trường này python sẽ là 3.10)
pip install --upgrade pip
pip install TTS faster-whisper ollama sounddevice
pip install faster-whisper soundfile
pip install TTS soundfile torch
              pip install --upgrade pip
              pip install fastapi uvicorn pydantic httpx pynacl google-genai telethon

pip uninstall transformers -y
pip install transformers==4.33.0
pip install tokenizers==0.13.3

pip install f5-tts
pip install soundfile

# Cài đặt các thư viện chính
pip install --upgrade pip
pip install faster-whisper ollama TTS RealtimeSTT sounddevice

# Cập nhật pip và setuptools trước
python -m pip install --upgrade pip setuptools wheel

# Cài đặt các thư viện bổ trợ cho âm thanh trên Windows/Linux
# Nếu là Linux (Ubuntu/Debian): sudo apt-get install espeak-ng libsndfile1

# Cài đặt TTS từ GitHub (cách này ổn định nhất cho bản XTTSv2)
pip install git+https://github.com/coqui-ai/TTS.git



 > Downloading model to /home/dunp/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2