
import sys
import random
import socket
import subprocess
import shutil
import os
from pathlib import Path
PORT = 8888
HISTORY_CHAT_MAX_LEN=10

CONFIG_NAME="config_dunp"
print("sys.argv",sys.argv)
# sys.argv[0] là tên file (program.py)
# sys.argv[1] sẽ là 'config_dunp'
# if len(sys.argv) > 1 and sys.argv[1] == 'config_dunp':
if len(sys.argv) > 1 and sys.argv[1] == 'config_ngoc':
    CONFIG_NAME="config_ngoc"
    from config_ngoc import TELEGRAM_BOT_GROUP_CHATID,TELEGRAM_OWNER_USERID,TELEGRAM_OWNER_USERNAME,TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME,JIRA_PERSONAL_ACCESS_TOKEN,JIRA_SERVER_ISSUE_API,JIRA_PROJECT_KEY,JIRA_SERVER_WEBHOOK_API,SWAKSRC
elif len(sys.argv) < 2 or sys.argv[1] != "config_dunp":
    from config_dunp import TELEGRAM_BOT_GROUP_CHATID,TELEGRAM_OWNER_USERID,TELEGRAM_OWNER_USERNAME,TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME,JIRA_PERSONAL_ACCESS_TOKEN,JIRA_SERVER_ISSUE_API,JIRA_PROJECT_KEY,JIRA_SERVER_WEBHOOK_API,SWAKSRC
elif len(sys.argv) > 1 and sys.argv[1] == 'config_dunp':
    from config_dunp import TELEGRAM_BOT_GROUP_CHATID,TELEGRAM_OWNER_USERID,TELEGRAM_OWNER_USERNAME,TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME,JIRA_PERSONAL_ACCESS_TOKEN,JIRA_SERVER_ISSUE_API,JIRA_PROJECT_KEY,JIRA_SERVER_WEBHOOK_API,SWAKSRC
else:
    from config_dev import TELEGRAM_BOT_GROUP_CHATID,TELEGRAM_OWNER_USERID,TELEGRAM_OWNER_USERNAME,TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME,JIRA_PERSONAL_ACCESS_TOKEN,JIRA_SERVER_ISSUE_API,JIRA_PROJECT_KEY,JIRA_SERVER_WEBHOOK_API,SWAKSRC

print("config.CONFIG_NAME",CONFIG_NAME)

def setup_playwright():
    # 1. Kiểm tra và cài đặt thư viện python 'playwright'
    try:
        import playwright
        print("[*] Thư viện Playwright đã được cài đặt.")
    except ImportError:
        print("[!] Không tìm thấy thư viện Playwright. Đang tiến hành cài đặt...")
        try:
            # Lưu ý: pip install không cần -y
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            print("[+] Cài đặt thư viện Playwright thành công!")
        except Exception as e:
            print(f"[!] Lỗi cài đặt thư viện: {e}")
            return

    # 2. Kiểm tra và cài đặt trình duyệt Chromium
    # Chúng ta sử dụng lệnh 'playwright install --with-deps' để đảm bảo đủ thư viện hệ thống
    try:
        # Cách kiểm tra nhanh: Thử lấy đường dẫn thực thi của chromium
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Nếu chromium chưa cài, dòng này thường sẽ văng lỗi
            executable_path = p.chromium.executable_path
            
            if os.path.exists(executable_path):
                print(f"[*] Chromium đã sẵn sàng tại: {executable_path}")
            else:
                raise FileNotFoundError
                
    except (ImportError, Exception):
        print("[!] Chromium chưa được cài đặt hoặc bị lỗi. Đang tải xuống...")
        try:
            # Cài đặt chromium
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            # (Tùy chọn) Cài đặt dependencies hệ thống nếu bạn dùng Linux (cần sudo)
            # subprocess.run([sys.executable, "-m", "playwright", "install-deps", "chromium"], check=True)
            print("[+] Cài đặt Chromium thành công!")
        except subprocess.CalledProcessError as e:
            print(f"[!] Lỗi khi cài đặt trình duyệt: {e}. Vui lòng chạy 'playwright install chromium' thủ công.")

def setup_swaks_tool():
    home_dir = Path.home()
    swaksrc_path = home_dir / ".swaksrc"
    
    # 1. Kiểm tra và tạo file .swaksrc
    if swaksrc_path.exists():
        print(f"[*] File {swaksrc_path} đã tồn tại. Bỏ qua bước khởi tạo.")
    else:
        print(f"[*] Đang tạo file cấu hình mẫu tại {swaksrc_path}...")
        # Nội dung mẫu cho .swaksrc (Lưu ý: Swaks dùng định dạng option per line)
        swaksrc_content =  SWAKSRC
        try:
            swaksrc_path.write_text(swaksrc_content)
            # Bảo mật: Chỉ user hiện tại mới có quyền đọc/ghi file này (600)
            os.chmod(swaksrc_path, 0o600)
            print("[+] Đã tạo file .swaksrc và phân quyền an toàn.")
        except Exception as e:
            print(f"[!] Lỗi khi tạo file cấu hình: {e}")

    # 2. Kiểm tra và cài đặt Swaks (dành cho Debian/Ubuntu)
    print("[*] Đang kiểm tra cài đặt swaks...")
    try:
        # Kiểm tra xem lệnh swaks có tồn tại không
        subprocess.run(["swaks", "--version"], capture_output=True, check=True)
        print("[+] Swaks đã được cài đặt sẵn.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[!] Không tìm thấy swaks. Đang tiến hành cài đặt via APT...")
        try:
            # Chạy lệnh cài đặt (Yêu cầu quyền sudo)
            subprocess.run(["sudo", "apt-get", "update", "-y"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "swaks", "-y"], check=True)
            print("[+] Cài đặt swaks thành công!")
        except subprocess.CalledProcessError as e:
            print(f"[!] Lỗi khi cài đặt swaks: {e}. Vui lòng cài đặt thủ công.")

def setup_curl():
    print("--- [Bước 1] Kiểm tra curl trên hệ thống ---")
    
    # Cách 1: Sử dụng shutil.which (Nhanh và không cần gọi shell)
    curl_path = shutil.which("curl")
    
    if curl_path:
        print(f"[+] curl đã được cài đặt tại: {curl_path}")
        # Kiểm tra version để đảm bảo nó hoạt động tốt
        try:
            result = subprocess.run(["curl", "--version"], capture_output=True, text=True)
            print(f"[i] Phiên bản: {result.stdout.splitlines()[0]}")
        except Exception:
            print("[!] curl có tồn tại nhưng gặp lỗi khi thực thi.")
    else:
        print("[!] Không tìm thấy curl. Đang tiến hành cài đặt...")
        try:
            # Cập nhật danh sách gói (Update)
            print("[*] Đang chạy 'sudo apt-get update'...")
            subprocess.run(["sudo", "apt-get", "update", "-y"], check=True)
            
            # Cài đặt curl
            print("[*] Đang chạy 'sudo apt-get install curl'...")
            subprocess.run(["sudo", "apt-get", "install", "curl", "-y"], check=True)
            
            print("[+] Cài đặt curl thành công!")
        except subprocess.CalledProcessError as e:
            print(f"[!] Lỗi khi cài đặt curl: {e}")
        except FileNotFoundError:
            print("[!] Lỗi: Không tìm thấy trình quản lý gói 'apt-get'. Bạn có đang dùng Linux (Debian/Ubuntu) không?")

def init():
    # skills/cli/tool_call_cli.py , các tool phục vụ skill cli cần được cài và cấu hình trước 
    setup_curl()
    setup_swaks_tool()

    setup_playwright()

init()

def get_random_free_port(start=8999, end=9999):
    while True:
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Thử bind (chiếm) port này
                s.bind(('', port))
                return port
            except OSError:
                # Nếu port đã bận, tiếp tục vòng lặp
                continue


PORT = get_random_free_port()
