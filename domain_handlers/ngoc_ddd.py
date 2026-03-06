
import os
import sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import bot_telegram
from config import TELEGRAM_BOT_GROUP_CHATID,TELEGRAM_OWNER_USERID,TELEGRAM_OWNER_USERNAME,HISTORY_CHAT_MAX_LEN,TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME
import pandas as pd
import matplotlib.pyplot as plt
import telegram_types
import textwrap
import json 
import knowledgebase.dbconnect as dbconnect
import datetime
import time
import random

sqllite_user_mapping=dbconnect.SQLiteDB("excel_user_mapping")

def excel_to_csv(file_path):
    try:
        # Đọc sheet đầu tiên (index 0)
        # Nếu bạn muốn đọc sheet theo tên, dùng: sheet_name='Tên_Sheet'
        df = pd.read_excel(file_path, sheet_name=0)

        csv_file_path = file_path.replace(".xlsx", "sheet.0.csv")
        # Lưu thành file CSV
        # encoding='utf-8-sig' giúp hiển thị đúng tiếng Việt khi mở bằng Excel
        # index=False để không lưu cột số thứ tự mặc định của pandas
        df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

        print(f"Chuyển đổi thành công! File đã được lưu tại: {csv_file_path}")
        return csv_file_path

    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
        return None
    pass

def excel_capture_row(file_path):
    output_folder = 'phieu_luong_nhan_vien'
        
        # csv_file_path = excel_to_csv(file_path)
    output_folder = 'phieu_luong_nhan_vien'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. Đọc file Excel trực tiếp (sheet đầu tiên)
    df = pd.read_excel(file_path, sheet_name=0, header=None)

    # 3. Xử lý Header (dòng 5, 6 là tiêu đề - Index 4, 5 trong code nếu tính từ 0)
    # Lưu ý: Tùy vào file thực tế, bạn có thể điều chỉnh index (ở đây tôi dùng 5 và 6)
    header_row1 = df.iloc[5]
    header_row2 = df.iloc[6]

    def clean_val(val):
        if pd.isna(val) or str(val).lower() == 'nan':
            return ""
        return str(val).strip()

    # Hàm tự động xuống dòng để không bị mất chữ
    def wrap_text(text, width=12):
        if not text: return ""
        return "\n".join(textwrap.wrap(str(text), width=width))

    # Gộp tiêu đề và wrap text
    combined_headers = []
    for h1, h2 in zip(header_row1, header_row2):
        c1, c2 = clean_val(h1), clean_val(h2)
        label = f"{c1}\n({c2})" if c1 and c2 else (c1 or c2)
        combined_headers.append(wrap_text(label, width=15))

    # 4. Lấy dữ liệu nhân viên (Bắt đầu từ index 8, bỏ qua dòng Tổng index 7)
    employee_data = df.iloc[8:]

    results={}

    for index, row in employee_data.iterrows():
        # print("index=======",index)
        emp_name = clean_val(row[2]) # Cột C là tên nhân viên
        if not emp_name or emp_name.lower() == 'tổng':
            continue
        
        # Lọc các cột có dữ liệu
        indices = [i for i, (h, v) in enumerate(zip(combined_headers, row)) if h != "" or clean_val(v) != ""]
        final_headers = [combined_headers[i] for i in indices]
        final_values = [wrap_text(clean_val(row[i]), width=15) for i in indices]
        
        table_data = [final_headers, final_values]

        # 5. Vẽ ảnh với kích thước linh hoạt
        num_cols = len(indices)
        fig_width = max(20, num_cols * 1.5) # Tự động giãn chiều rộng theo số cột
        fig, ax = plt.subplots(figsize=(fig_width, 4))
        ax.axis('off')

        table = ax.table(
            cellText=table_data, 
            loc='center', 
            cellLoc='center',
            colWidths=[1.0/num_cols] * num_cols # Chia đều độ rộng các cột
        )

        # 6. Cấu hình để không mất chữ
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        
        for (r, c), cell in table.get_celld().items():
            cell.set_height(0.5) # Tăng độ cao của ô để chứa được text đã xuống dòng
            if r == 0: # Định dạng cho Header
                cell.set_facecolor('#4c72b0')
                cell.set_text_props(weight='bold', color='white')

        plt.title(f"PHIẾU LƯƠNG: {emp_name.upper()} ngày gửi: {datetime.datetime.now().strftime('%d/%m/%Y')}", fontsize=16, pad=30)

        # 7. Lưu ảnh chất lượng cao
        safe_name = emp_name.replace(' ', '_')
        fileimg4user=os.path.abspath( f"{output_folder}/{safe_name}.pdf")
        plt.savefig(fileimg4user, bbox_inches='tight', dpi=200)
        plt.close(fig)
        print(f"Đã xuất ảnh cho: {emp_name} {fileimg4user}")
        # results.append({
        #     "file":fileimg4user,
        #     "fullname":f"{emp_name}"
        # })

        results[f"{emp_name}".lower()]=fileimg4user

    return results
    pass

def process_user_mapping(msg:telegram_types.OrchestrationMessage):
    text = msg.text or ""

    # Handle fullname after tên: or ten: or name:
    # Use (?i) for case-insensitive, and \s* for optional spaces
    fullname_match = re.search(r"(?i)(?:\s+tên|\s+ten|\s+name)\s*:\s*(.+)", text)
    fullname=None
    if not fullname_match: 
        idx2cham= text.find(":")
        if idx2cham > -1:
            fullname = text[idx2cham+1:].strip()
    else:
        fullname = fullname_match.group(1).strip()

    if not fullname or fullname=="":
        print("Không tìm thấy tên, cần theo mẫu vd: @username tên: fullname here")
        print("msg.message.message.entities ------",msg.message.message.entities)
        return None

    if msg.message.message.entities:
        for entity in msg.message.message.entities:
            if str(entity["type"]).lower() == "text_mention":
                # username = entity["user"]["username"] or ""   
                # fullname = entity["user"]["first_name"] + " " + entity["user"]["last_name"]
                return {
                    "id": entity["user"]["id"],
                    "username": "",
                    "fullname": fullname,
                    "is_bot": entity["user"]["is_bot"],
                    "first_name": entity["user"]["first_name"],
                    "last_name": entity["user"]["last_name"]
                }
    
    # Handle username in text (e.g., @badpaybad)
    username_match = re.search(r"@(\w+)", text)
    if not username_match:
        print("Không tìm thấy username thiếu @ vd @username tên: fullname here")
        return None
    username = username_match.group(1)
    
    dbuser = sqllite_user_mapping.search_json("username",username)
    if dbuser and len(dbuser) > 0:
        dbuser = dbuser[0]
        dbuser = dbuser["json"]
        dbuser["fullname"] = fullname
        return dbuser
    else:
        fromuser= msg.message.get_message_from_user()
        user_id = fromuser.id if fromuser else None
        first_name = fromuser.first_name if fromuser else None
        last_name = fromuser.last_name if fromuser else None
        is_bot = fromuser.is_bot if fromuser else None

        return {
            "id": user_id,
            "username": username,
            "fullname": fullname,
            "is_bot": is_bot,
            "first_name": first_name,
            "last_name": last_name
        }
    

async def handle(msg:telegram_types.OrchestrationMessage):

    fromuser=msg.message.get_message_from_user()
    print("fromuser",fromuser)
    # int(msg.chat_id) == int(fromuser.id) đang chat trực tiếp private với bot TELEGRAM_BOT_CHATID

    if int(msg.chat_id) != int(TELEGRAM_BOT_GROUP_CHATID) and int(msg.chat_id) != int(fromuser.id): 
        print("Nhóm không hợp lệ TELEGRAM_BOT_GROUP_CHATID: ",TELEGRAM_BOT_GROUP_CHATID, " Nhóm đúng: ",msg.chat_id)
        print(msg)
        return

        # for member in msg.new_chat_members:
        #     print("member",member)
        #     if member["username"]!=TELEGRAM_OWNER_USERNAME:
        #         print("Tài khoản không có quyền làm, cần là tài khoản:",TELEGRAM_OWNER_USERNAME)
        #         return
    
    if msg.message.new_chat_members:
        await bot_telegram.send_telegram_welcome(msg.chat_id)

    # if fromuser and fromuser.username!=TELEGRAM_OWNER_USERNAME:
    if fromuser and int(fromuser.id) != int(TELEGRAM_OWNER_USERID):
        print("Tài khoản không có quyền làm, cần là tài khoản:",TELEGRAM_OWNER_USERNAME,TELEGRAM_OWNER_USERID)
        return
        pass


    user_mapping = process_user_mapping(msg)
    print("user_mapping",user_mapping)
    if user_mapping:
        existedUser= sqllite_user_mapping.search_json("id",user_mapping["id"])
        print("existedUser",existedUser)
        if existedUser and len(existedUser) > 0:
            existedUser=existedUser[0]
            oldusername =f"{existedUser['json']['fullname']}"
            existedUser["json"]["fullname"] = f"{user_mapping["fullname"]}".strip()
            sqllite_user_mapping.update(existedUser["id"],existedUser["json"])
            await bot_telegram.send_telegram_message(msg.chat_id, f"Cập nhật User {oldusername} đã tồn tại thành {user_mapping['fullname']}")
        else:  
            sqllite_user_mapping.insert(user_mapping)
            await bot_telegram.send_telegram_message(msg.chat_id, f"Đã thêm user {user_mapping['fullname']}")
        return

    if not msg.files and len(msg.files) == 0:
        await bot_telegram.send_telegram_message(msg.chat_id, "Bạn chưa có file excel")
        return 
    
    fileimages=excel_capture_row(msg.files[0])

    alluser= sqllite_user_mapping.select()

    for rec in alluser:
        user=rec["json"]
        print("user",user)
        if fileimages[user["fullname"].lower()]:
            # await bot_telegram.send_telegram_message(msg.chat_id, f"Lương {user['fullname']} ngày gửi: {datetime.datetime.now().strftime('%d/%m/%Y')}",[fileimages[user["fullname"].lower()]])
            rrrr=await bot_telegram.send_telegram_message(user["id"], f"Lương {user['fullname']} ngày gửi: {datetime.datetime.now().strftime('%d/%m/%Y')}",[fileimages[user["fullname"].lower()]])
            if rrrr ==None:
                await bot_telegram.send_telegram_welcome(msg.chat_id,f"{user["fullname"]} chưa tham gia bot chat ")    
                
            wait_time = random.uniform(1, 3)
            time.sleep(wait_time)
        pass

    pass


