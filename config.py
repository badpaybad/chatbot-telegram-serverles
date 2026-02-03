
import sys
import random
import socket
PORT = 8888


# sys.argv[0] là tên file (program.py)
# sys.argv[1] sẽ là 'config_dunp'
if len(sys.argv) > 1 and sys.argv[1] == 'config_dunp':
    from config_dunp import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME
else:
    from config_dev import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME


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
