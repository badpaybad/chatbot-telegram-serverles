import sys
import os
# Thêm thư mục gốc vào sys.path để có thể import các module bot_telegram, config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import asyncio
from playwright.async_api import async_playwright

import random
import os
import time
import base64
import requests
import bot_telegram
import queue

import knowledgebase.dbcontext


from config import TELEGRAM_OWNER_USERID,TELEGRAM_BOT_GROUP_CHATID,HISTORY_CHAT_MAX_LEN,TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, PORT, TELEGRAM_BOT_CHATID, TELEGRAM_BOT_USERNAME, GEMINI_APIKEY,GEMINI_MODEL, DISCORD_PUBKEY, DISCORD_APPID, DISCORD_TOKEN,  TELEGRAM_API_ID, TELEGRAM_API_HASH, REPLY_ON_TAG_BOT_USERNAME

import bot_telegram

"""_summary_
các action queue vào sẽ thực hiện lần lượt, vd nếu có while true ở action trước thì đến sau sẽ đợi xong phía trước break while 
"""
browserActionBlockQueue= asyncio.Queue()
isStop=False
page=None
context=None
playwright_instance=None

browser_lock = asyncio.Lock()

async def loop_run_browser_agent():
    global browserActionBlockQueue
    global isStop
    global page
    global context
    global playwright_instance

    async with async_playwright() as p:
        playwright_instance=p
        # 1. Khởi chạy trình duyệt (headless=False để quan sát)
        # browser = await p.chromium.launch(headless=False)
        # context = await browser.new_context()
        # page = await context.new_page()
        # Playwright sẽ tự tìm Chrome trong các đường dẫn mặc định của Ubuntu

        # Lấy username để tạo đường dẫn chính xác
        user_home = os.path.expanduser("~")
        user_data_dir = f"{user_home}/.config/google-chrome/Zalo"
        print("user_data_dir",user_data_dir)

        # browser = await p.chromium.launch(channel="chrome", headless=False,
        # args=["--no-sandbox"])
        # page = await browser.new_page()

        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            # headless=True, # chạy ngầm
            headless=False, # xem được thao tác 
            args=["--no-sandbox"] # Cần thiết nếu chạy với quyền root hoặc môi trường đặc biệt
        )
        async with browser_lock:
            page = context.pages[0] # Persistent context tạo sẵn 1 page

        try:
            # 2. Đi tới trang Login

            # 3. Nhập liệu (Playwright tự đợi selector này xuất hiện)
            # await page.fill('input[id="inputA"]', f"{random.randint(0, 1000) }")
            # await page.fill('input[id="inputB"]', f"{random.randint(0, 1000) }")

            # 4. Click Submit và đợi chuyển hướng (Redirect)
            # print("Đang nhấn đăng nhập và đợi chuyển hướng...")
            # # Playwright có cơ chế thông minh: nhấn và đợi URL thay đổi
            # await asyncio.gather(
                # page.click('#checkBtn'),
            #     #page.wait_for_url("**/dashboard", timeout=10000) # Đợi tới khi URL chứa chữ 'dashboard'
            # )

            # # 5. Đợi nội dung ở trang mới load xong
            # print(f"Đã tới trang: {page.url}")
            # await page.wait_for_selector(".balance-amount") 

            # # 6. Lấy dữ liệu (Scraping)
            # balance = await page.inner_text(".balance-amount")
            # print(f"Dữ liệu lấy được: {balance}")

            # # Lấy cấu trúc trang web dưới dạng đơn giản nhất để AI đọc
            # snapshot = await page.accessibility.snapshot()
            # print(snapshot)

            # 7. Chụp ảnh làm bằng chứng cho AI Agent
            # await page.screenshot(path="dashboard_result.png")

            while not isStop:

                if browserActionBlockQueue.empty():
                    await asyncio.sleep(1)
                    continue

                nextact= await browserActionBlockQueue.get()

                if not nextact:
                    await asyncio.sleep(1)
                    continue
                
                if asyncio.iscoroutinefunction(nextact):
                    await nextact()
                else :
                    nextact()


            await asyncio.sleep(1)
            print("Done")

        except Exception as e:
            print(f"Lỗi loop_run_browser_agent: {e}")
        finally:
            # await browser.close()
            await context.close()
            pass
async def open_zalo_web():

    async with browser_lock:
        print("Đang mở trang đăng nhập...")
        await page.goto("https://chat.zalo.me/")
        await page.wait_for_load_state("networkidle")
    await asyncio.sleep(3)



async def download_qr_code():

    async with browser_lock:
        await page.wait_for_load_state("networkidle")
        file_name="zalo_qr.png"
    # 1. Tìm selector: tìm img bên trong class .qr-container
    qr_selector = ".qr-container img"
    
    try:
        # Đợi QR xuất hiện
        # await page.wait_for_selector(qr_selector, timeout=10000)
        
        async with browser_lock:
            # 2. Lấy thuộc tính src của thẻ img
            qr_src = await page.locator(qr_selector).get_attribute("src")
                    
        if not qr_src:
            print("Không tìm thấy thuộc tính src của QR")

            try:    
                async with browser_lock:
                    await page.get_by_text("Đã hiểu").click(force=True)    
                    print(f"Click nút Đã hiểu") 

                await asyncio.sleep(3)
            except Exception as e:
                print(f"Không tìm thấy nút Đã hiểu")
            

            async with browser_lock:
                qr_src = await page.locator(qr_selector).get_attribute("src", timeout=10000)    

            if not qr_src:
                print("Không tìm thấy thuộc tính src của QR")
            return None

        # 3. Xử lý nếu là Base64 (Zalo thường dùng cái này cho QR)
        if "base64," in qr_src:
            header, encoded = qr_src.split(",", 1)
            data = base64.b64decode(encoded)
            with open(file_name, "wb") as f:
                f.write(data)
            print(f"Đã lưu QR từ Base64: {file_name}")
            
        # 4. Xử lý nếu là URL thông thường
        else:
            response = requests.get(qr_src)
            if response.status_code == 200:
                with open(file_name, "wb") as f:
                    f.write(response.content)
                print(f"Đã tải QR từ URL: {file_name}")

        return file_name
    except Exception as e:
        print(f"Lỗi khi tải QR: {e}")

        return None

async def sync_zalo_chats_groups():
    print("sync_zalo_chats_groups doing")

    async with browser_lock:
        await page.wait_for_load_state("networkidle")
    await asyncio.sleep(3)
    try:
        # z--btn--v2 btn-primary small sync-v2-ok suggestNewSync --rounded sync-v2-ok suggestNewSync
        # await page.locator(".suggestNewSync.btn-primary", timeout=10000).click(force=True)

        async with browser_lock:
            # Đợi cho tới khi DOM của trang mới thực sự sẵn sàng
            await page.wait_for_selector(".sync-v2-banner.suggestNewSync", state="attached", timeout=10000)
            await page.locator(".sync-v2-banner.suggestNewSync").click(force=True)

    except Exception as e:
        print(f"Không tìm thấy nút Đồng bộ ngay .suggestNewSync.btn-primary")
    try:
        # tds-conversation__footer-content-sync-button
        async with browser_lock:
            await page.wait_for_selector(".tds-conversation__footer-content-sync-button", state="attached", timeout=10000)
            await page.locator(".tds-conversation__footer-content-sync-button").click(force=True)

    except Exception as e:
        print(f"Không tìm thấy nút Đồng bộ ngay .tds-conversation__footer-content-sync-button")

    try:
        async with browser_lock:
            await page.get_by_text("Nhấn để đồng bộ ngay", timeout=10000).click(force=True)    
            print(f"Click nút Nhấn để đồng bộ ngay") 

        await asyncio.sleep(3)
    except Exception as e:
        print(f"Không tìm thấy nút Nhấn để đồng bộ ngay")
    try:
        async with browser_lock:
            await page.get_by_text("Đồng bộ ngay", timeout=10000).click(force=True)    
            print(f"Click nút Đồng bộ ngay") 

        await asyncio.sleep(3)
    except Exception as e:
        print(f"Không tìm thấy nút Đồng bộ ngay")

    try:
        #sync-message-popup
            
        qr_selector = ".sync-message-popup"
        while not isStop:
            try:
                async with browser_lock:
                    found=await page.wait_for_selector(qr_selector, timeout=10000)
                if found:
                    print("Đang đồng bộ")
                    await asyncio.sleep(10)

                    print("Vẫn đang hiện .sync-message-popup")
                    await bot_telegram.send_telegram_message(TELEGRAM_OWNER_USERID,f"Vẫn đang hiện .sync-message-popup, bạn mở zalo để đồng ý đồng bộ")
                    await asyncio.sleep(10)
            except Exception as ex:

                print(f"Không có .sync-message-popup -> đã đồng bộ: {ex}")
                
                break 
                
                pass
    except:
        pass

async def check_zalo_qr_auth():

    async with browser_lock:
        await page.wait_for_load_state("networkidle")

    # https://id.zalo.me/account?continue=https%3A%2F%2Fchat.zalo.me%2F

    # qr_file=await download_qr_code()
    qr_file=None

    qr_selector = ".fa-Contact_28_Line"
    while not isStop:
        try:
            async with browser_lock:
                found=await page.wait_for_selector(qr_selector, timeout=10000)
            if found:
                print("QR code đã ẩn, đã vào trang chat")

                return 
            else:
                print(f"Redownload QR để check qr_selector: {qr_selector}")
                if not qr_file:
                    qr_file=await download_qr_code()
                    print("Redownload QR")
                else:
                    print("QR code download xong, cần đăng nhập bằng điện thoại để vào trang chat")
                    await bot_telegram.send_telegram_message(TELEGRAM_OWNER_USERID,f"QR code download xong, cần đăng nhập bằng điện thoại để vào trang chat", 
                    files=[qr_file])
                    await asyncio.sleep(5)      
                    
            await asyncio.sleep(3)               
        except Exception as ex:
            print(f"check_zalo_qr_auth Lỗi khi check QR: {ex}")
            # case timeout dom selector

            print(f"Redownload QR để check qr_selector: {qr_selector}")
            if not qr_file:
                qr_file=await download_qr_code()
                print("Redownload QR")
            else:
                print("QR code download xong, cần đăng nhập bằng điện thoại để vào trang chat")
                await bot_telegram.send_telegram_message(TELEGRAM_OWNER_USERID,f"QR code download xong, cần đăng nhập bằng điện thoại để vào trang chat", 
                files=[qr_file])
                await asyncio.sleep(5) 

            await asyncio.sleep(3)
       
        pass

#qr-container

    pass
# vi du action queue, khi cần làm j đó với 1 page đã được mở lên, không tạo mới page ko sợ mất session     
# 

async def open_zalo_group_omt_tbp(groupname:str="OMT-TBP"):
    async with browser_lock:
        await page.wait_for_load_state("networkidle")
    try:
        
        print("click OMT-TBP")

        # page.locator("div:has-text('OMT-TBP')").click()
        async with browser_lock:
            found =page.get_by_text(groupname)

        while not found:
            if found:
                break
            
            sync_zalo_chats_groups()

            async with browser_lock:
                found =page.get_by_text(groupname)
            await asyncio.sleep(10)
    
        async with browser_lock:
            await found.click(force=True, timeout=10000)
        
        while not isStop:
            async with browser_lock:
                text = await page.locator("div#messageViewContainer").text_content()
            if  text:
               break
            
            await asyncio.sleep(1)

        # text = page.get_by_test_id("messageViewContainer").inner_text()
        # msg=await page.inner_text("messageViewContainer")
        print("messageViewContainer",text)

        count=0
        chat_items=None
        async with browser_lock:
            chat_items = page.locator("div#messageViewContainer div.chat-item")
            # Lấy số lượng tìm thấy
            count = await chat_items.count()
            print(f"Tìm thấy {count} tin nhắn.")

        listmsg=[]
        # todo: có thể dùng page scroll để lấy msg cũ
        # Lặp qua từng cái
        for i in range(count):
            item = chat_items.nth(i)
            # print(f"Nội dung item {i}: {await item.inner_text()}")
            listmsg.append(await item.inner_text())

        # all_texts = await page.locator("div#messageViewContainer div.chat-item").all_inner_texts()
        # Kết quả trả về là một mảng: ['Tin nhắn 1', 'Tin nhắn 2', ...]
        # print("all_texts",all_texts)
        return listmsg

    except:
        return None

    pass

zalo_group_msg_ActionBlockQueue= asyncio.Queue()

latest_zalo_group_msg_list_check_duplicate=[]

async def loop_enqueue_processed_zalo_group_msg():
    all_texts=[]
    while not isStop:
        all_texts=await open_zalo_group_omt_tbp("OMT-TBP")

    if all_texts:
        await zalo_group_msg_ActionBlockQueue.put({"groupname":"OMT-TBP", "message":all_texts})
    await asyncio.sleep(10)
    pass


async def loop_dequeue_processed_zalo_group_msg_into_telegram():
    while not isStop:
        all_texts=[]
        
        duplicate_text_to_check=""
        duplicate_text_to_check_count=0

        while not isStop:
            txt =await zalo_group_msg_ActionBlockQueue.get()

            all_texts.append(txt)

            if not txt:
                break
            if duplicate_text_to_check_count>2:
                latest_zalo_group_msg_list_check_duplicate.append(duplicate_text_to_check)
                
                if duplicate_text_to_check  in latest_zalo_group_msg_list_check_duplicate:
                    # nếu 3 message cuối cùng trùng nhau , tức là conversation chưa có message mới
                    # all_texts=all_texts[:-3]
                    all_texts=[]

                duplicate_text_to_check=""
            else:
                duplicate_text_to_check= txt["groupname"]+":"+duplicate_text_to_check+ txt["message"]
                duplicate_text_to_check_count=duplicate_text_to_check_count+1

        if len(all_texts)==0:
            await asyncio.sleep(1)
            pass
        
        print("all_texts processed", all_texts)

        #todo:cần push vào db        
        knowledgebase.dbcontext.zalo_all_message.insert({
            "message":all_texts
        })

        await asyncio.sleep(10)
    pass

async def loop():
    global isStop
    
    await browserActionBlockQueue.put(open_zalo_web)
    await browserActionBlockQueue.put(check_zalo_qr_auth)
    await browserActionBlockQueue.put(sync_zalo_chats_groups)

    await asyncio.gather( loop_run_browser_agent(),
                          loop_enqueue_processed_zalo_group_msg(),
                        #   loop_dequeue_processed_zalo_group_msg_into_telegram()
                          )

asyncio.run(loop())