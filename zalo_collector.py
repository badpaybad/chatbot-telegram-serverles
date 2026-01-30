import pyautogui
import time
import os
import subprocess
from PIL import ImageGrab


def close_and_open_zalo():
    print("Đang đóng tất cả tiến trình Chrome...")
    try:
        # pkill -f sẽ tìm và đóng mọi tiến trình có tên 'chrome'
        subprocess.run(['pkill', '-f', 'chrome'], check=False)
        # Chờ 2 giây để các tiến trình giải phóng bộ nhớ hoàn toàn
        time.sleep(2)
    except Exception as e:
        print(f"Lỗi khi đóng Chrome: {e}")

    print("Đang khởi động lại Chrome và mở Zalo Web...")
    # Mở Chrome với trang Zalo Web
    # Sử dụng subprocess để có thể thêm các tham số như --start-maximized
    try:
        subprocess.Popen(
            ['google-chrome', '--start-maximized', 'https://chat.zalo.me/'])
    except:
        # Dự phòng nếu máy dùng Chromium
        subprocess.Popen(
            ['chromium-browser', '--start-maximized', 'https://chat.zalo.me/'])


# --- Thực thi ---
close_and_open_zalo()

# Chờ trình duyệt mở và bạn đăng nhập
print("Chờ 5 giây để đăng nhập Zalo...")
time.sleep(5)

# 2. Tọa độ (Sử dụng xdotool để lấy nếu cần)
# Lưu ý: Trên Linux, tọa độ 0,0 là góc trên cùng bên trái màn hình
group_x, group_y = 173, 367


def capture_full_screen(filename):
    # Cách này đảm bảo lấy hết tất cả những gì đang hiển thị
    screenshot = ImageGrab.grab()
    screenshot.save(filename)
    print(f"Đã lưu toàn bộ màn hình vào: {filename}")


def capture_linux_chat(filename):
    # PyAutoGUI trên Linux chụp toàn màn hình bằng scrot
    # Ta dùng Pillow để cắt vùng mong muốn hoặc dùng trực tiếp ImageGrab
    chat_region = (450, 150, 1200, 900)  # (left, top, right, bottom)
    screenshot = ImageGrab.grab(bbox=chat_region)
    screenshot.save(filename)
    print(f"Đã lưu: {filename}")



def input_vietnamese(text):
    # Sử dụng lệnh 'xclip' trên Linux để copy text vào bộ nhớ tạm
    # Cài đặt nếu chưa có: sudo apt-get install xclip
    os.system(f'echo "{text}" | xclip -selection clipboard')

    # Dán (Ctrl + V)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')

# # 2. Nhập văn bản
# # 'interval' là thời gian trễ giữa các phím để giống người gõ hơn, tránh bị bắt spam
# pyautogui.write("Chao ban, day la tin nhan tu dong!", interval=0.1)

# # 3. Nhấn Enter để gửi
# pyautogui.press('enter')
import easyocr
# 1. Khởi tạo Reader (Chỉ làm 1 lần để tiết kiệm RAM)
# 'vi' là tiếng Việt, 'en' là tiếng Anh
reader = easyocr.Reader(['vi', 'en'], gpu=False) # Nếu có card NVIDIA thì để gpu=True

def get_text_from_image(image_path):
    print(f"--- Đang phân tích ảnh: {image_path} ---")
    # Đọc văn bản từ ảnh
    # detail=0 sẽ chỉ trả về danh sách các câu, không trả về tọa độ
    results = reader.readtext(image_path, detail=0)
    
    full_text = "\n".join(results)
    return full_text

def get_window_id():
# 3. Dùng xdotool để tìm Window ID dựa trên tên cửa sổ
    try:
        # Lệnh này tìm cửa sổ có tiêu đề chứa "Zalo"
        window_id = subprocess.check_output(["xdotool", "search", "--name", "Zalo"]).decode().strip().split('\n')[-1]
        print(f"Window ID tìm thấy: {window_id}")
        return window_id
    except:
        print("Chưa tìm thấy cửa sổ Zalo.")
        return None
    
def force_activate(wid):
    if wid:
        # --sync đảm bảo cửa sổ hiện lên rồi mới chạy lệnh tiếp theo trong Python
        subprocess.run(["xdotool", "windowactivate", "--sync", wid])
        # subprocess.run(["xdotool", "windowfocus", wid])
        # # Đảm bảo nó luôn chiếm toàn màn hình
        subprocess.run(["xdotool", "windowsize", wid, "100%", "100%"])
        # subprocess.run(["xdotool", "windowminimize", wid])
        subprocess.run(["xdotool", "windowactivate", wid])

# 3. Thao tác
for i in range(1):
    # Di chuyển và Click
    pyautogui.moveTo(group_x, group_y + (i * 60), duration=0.5)
    pyautogui.click()

    # time.sleep(2)  # Chờ load nội dung
    # capture_linux_chat(f"zalo_linux_group_{i}.png")
    screenshot_name = f"zalo_group_{i}.png"
    capture_full_screen(screenshot_name)

    content = get_text_from_image(screenshot_name)

    wid=get_window_id()

    print("Nội dung đã lấy được:")
    print(content)

    subprocess.run(["xdotool", "windowminimize", wid])

    time.sleep(2)

    force_activate(wid)
    
    # Có thể dùng phím mũi tên xuống để chuyển nhóm tiếp theo
    # pyautogui.press('down')

    # pyautogui.press('f11')

    time.sleep(1)  # Chờ một chút để con trỏ chuột focus vào ô nhập



exit(0)